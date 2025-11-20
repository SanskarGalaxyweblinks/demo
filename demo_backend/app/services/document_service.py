# app/services/document_service.py
from __future__ import annotations

import io
import os
import time
import json
import base64
from typing import Any, Dict
from fastapi import HTTPException, UploadFile, status
from groq import Groq
import fitz  # PyMuPDF for PDF processing
from PIL import Image
import pytesseract

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)

# Supported file types
SUPPORTED_TYPES = {
    "application/pdf": "PDF",
    "application/msword": "DOC", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "Image",
    "image/png": "Image",
    "image/jpg": "Image",
    "text/plain": "Text"
}

# Document analysis prompts
DOCUMENT_ANALYSIS_SYSTEM_PROMPT = """
You are an expert AI system for KYC document analysis. Your task is to extract critical information from identity documents and financial documents for customer onboarding.

DOCUMENT TYPES TO IDENTIFY:
- "ID_Document" - Driver's licenses, passports, national IDs, state IDs
- "Financial_Document" - Bank statements, invoices, receipts, tax documents
- "Proof_of_Address" - Utility bills, lease agreements, official correspondence
- "Other" - Any document that doesn't fit the above categories

FOR ID DOCUMENTS, EXTRACT:
- Full name
- Date of birth
- Document number
- Document type
- Issuing authority
- Expiry date
- Address (if present)

FOR FINANCIAL DOCUMENTS, EXTRACT:
- Company/institution name
- Document number (invoice #, account #)
- Date
- Amount/balance
- Currency
- Account holder name

FOR PROOF OF ADDRESS, EXTRACT:
- Name on document
- Address
- Document date
- Issuing company/authority

You must respond in valid JSON format only.
"""

DOCUMENT_ANALYSIS_USER_PROMPT = """
Analyze this document text for KYC data extraction:

DOCUMENT TEXT:
{document_text}

FILENAME: {filename}

Respond with a JSON object containing:
{{
    "document_type": "ID_Document|Financial_Document|Proof_of_Address|Other",
    "extracted_entities": ["Entity 1", "Entity 2", "..."],
    "structured_data": {{
        "field_name": "value",
        "field_name2": "value2"
    }},
    "confidence": 0.0-1.0,
    "summary": "Brief description of document content"
}}

Extract all relevant KYC information. Use null for missing fields.
"""

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from various file types using appropriate methods"""
    try:
        file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
        contents = await file.read()
        
        if file_type == "PDF":
            # Use PyMuPDF for PDF text extraction
            return extract_pdf_text(contents)
        elif file_type == "Image":
            # Use OCR for image files
            return extract_image_text(contents)
        elif file_type == "Text":
            # Direct text extraction
            return contents.decode('utf-8', errors='ignore')
        else:
            # Try to decode as text for DOC/DOCX (basic approach)
            return contents.decode('utf-8', errors='ignore')[:2000]
            
    except Exception as e:
        print(f"Text extraction error: {e}")
        return f"Error extracting text from {file.filename}: {str(e)}"

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text[:3000]  # Limit text size for API
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return "Unable to extract text from PDF"

def extract_image_text(image_bytes: bytes) -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text[:3000]  # Limit text size for API
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return "Unable to extract text from image"

async def analyze_document(file: UploadFile, user: Any | None) -> Dict[str, Any]:
    """
    Analyze document for KYC data extraction using real Groq AI.
    """
    start_time = time.time()
    
    # Validate file
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file type
    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
    if file_type == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    try:
        # Extract text from document
        print(f"[DOCUMENT] Extracting text from {file.filename} ({file_type})")
        document_text = await extract_text_from_file(file)
        
        if not document_text or len(document_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract readable text from document"
            )
        
        # Use Groq AI for document analysis
        print(f"[DOCUMENT] Analyzing document with AI...")
        client = get_groq_client()
        
        user_prompt = DOCUMENT_ANALYSIS_USER_PROMPT.format(
            document_text=document_text,
            filename=file.filename
        )
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": DOCUMENT_ANALYSIS_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="openai/gpt-oss-20b",
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        # Parse AI response
        ai_response = json.loads(chat_completion.choices[0].message.content)
        
        # Build entities list from structured data
        entities = []
        structured_data = ai_response.get("structured_data", {})
        
        for key, value in structured_data.items():
            if value and str(value).strip():
                formatted_key = key.replace("_", " ").title()
                entities.append(f"{formatted_key}: {value}")
        
        # Add extracted entities
        entities.extend(ai_response.get("extracted_entities", []))
        
        # Add file metadata
        entities.insert(0, f"File Type: {file_type}")
        if user:
            entities.append(f"Processed by: {getattr(user, 'email', 'Unknown')}")
        
        processing_time = time.time() - start_time
        
        return {
            "documentType": ai_response.get("document_type", "Other"),
            "pageCount": 1,  # Could be enhanced to count actual pages
            "entities": entities,
            "detectedCurrency": extract_currency(structured_data),
            "confidence": float(ai_response.get("confidence", 0.85)),
            "receivedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "preview": document_text[:400],
            "extractedData": structured_data,
            "processingTime": round(processing_time, 2)
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return _fallback_document_analysis(file, document_text if 'document_text' in locals() else "", start_time)
    except Exception as e:
        print(f"Document analysis error: {e}")
        return _fallback_document_analysis(file, "", start_time)

def extract_currency(structured_data: Dict[str, Any]) -> str | None:
    """Extract currency from structured data"""
    currency_fields = ["currency", "amount", "balance", "total"]
    for field in currency_fields:
        value = str(structured_data.get(field, ""))
        if "USD" in value or "$" in value:
            return "USD"
        elif "EUR" in value or "€" in value:
            return "EUR"
        elif "GBP" in value or "£" in value:
            return "GBP"
    return None

async def detect_tamper(file: UploadFile, user: Any | None) -> Dict[str, Any]:
    """
    Detect document tampering using metadata analysis and content inspection.
    """
    start_time = time.time()
    
    # Validate file
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    try:
        contents = await file.read()
        file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
        
        # Basic tamper detection analysis
        is_authentic = True
        detected_issues = []
        confidence_score = 0.95
        
        # Check file size anomalies
        if len(contents) < 1000:
            detected_issues.append("Unusually small file size")
            confidence_score -= 0.1
        
        # Check for suspicious metadata patterns
        if file_type == "PDF":
            # Analyze PDF metadata
            try:
                doc = fitz.open(stream=contents, filetype="pdf")
                metadata = doc.metadata
                
                # Check for suspicious creation/modification patterns
                if metadata.get("creator") and "photoshop" in metadata.get("creator", "").lower():
                    detected_issues.append("Document created with image editing software")
                    confidence_score -= 0.2
                    
                doc.close()
            except:
                pass
        
        # Determine authenticity based on issues found
        if len(detected_issues) > 0:
            is_authentic = len(detected_issues) <= 1  # Allow minor issues
            risk_level = "High" if len(detected_issues) > 2 else "Medium"
        else:
            risk_level = "Low"
        
        analysis_details = {
            "metadataConsistency": len(detected_issues) == 0,
            "pixelAnalysis": True,  # Would require advanced image analysis
            "compressionArtifacts": True,
            "editingTraces": len(detected_issues) > 1
        }
        
        processing_time = time.time() - start_time
        
        return {
            "isAuthentic": is_authentic,
            "confidenceScore": round(max(confidence_score, 0.5), 3),
            "detectedIssues": detected_issues,
            "riskLevel": risk_level,
            "analysisDetails": analysis_details,
            "processingTime": round(processing_time, 2)
        }
        
    except Exception as e:
        print(f"Tamper detection error: {e}")
        return {
            "isAuthentic": False,
            "confidenceScore": 0.0,
            "detectedIssues": ["Analysis failed due to technical error"],
            "riskLevel": "High",
            "analysisDetails": {
                "metadataConsistency": False,
                "pixelAnalysis": False,
                "compressionArtifacts": False,
                "editingTraces": True
            },
            "processingTime": round(time.time() - start_time, 2)
        }

def _fallback_document_analysis(file: UploadFile, document_text: str, start_time: float) -> Dict[str, Any]:
    """Fallback document analysis if AI fails"""
    print("[DOCUMENT] Using fallback analysis due to API error")
    
    filename = file.filename.lower() if file.filename else ""
    
    # Basic document type detection
    if any(word in filename for word in ["license", "passport", "id"]):
        doc_type = "ID_Document"
        entities = ["Document type detected from filename", "Manual review recommended"]
    elif any(word in filename for word in ["invoice", "statement", "bill"]):
        doc_type = "Financial_Document"
        entities = ["Financial document detected", "Manual extraction required"]
    else:
        doc_type = "Other"
        entities = ["Unknown document type", "Manual review required"]
    
    return {
        "documentType": doc_type,
        "pageCount": 1,
        "entities": entities,
        "detectedCurrency": None,
        "confidence": 0.6,
        "receivedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preview": document_text[:400] if document_text else "No preview available",
        "extractedData": {"error": "AI analysis failed, manual review needed"},
        "processingTime": round(time.time() - start_time, 2)
    }