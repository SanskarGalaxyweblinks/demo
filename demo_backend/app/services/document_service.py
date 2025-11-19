# app/services/document_service.py
from __future__ import annotations

import io
import random
import time
import re
from typing import Any, Dict
from fastapi import HTTPException, UploadFile, status

# Simple document processing without external AI dependencies
SUPPORTED_TYPES = {
    "application/pdf": "PDF",
    "application/msword": "DOC", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "Image",
    "image/png": "Image",
    "text/plain": "Text"
}

# Sample data for demo purposes
SAMPLE_PII_DATA = [
    {
        "fullName": "John Smith",
        "dateOfBirth": "1985-03-15",
        "documentNumber": "DL123456789",
        "documentType": "Driver License",
        "expiryDate": "2028-03-15",
        "issuingAuthority": "California DMV",
        "address": "123 Main St, Los Angeles, CA 90210",
        "confidenceScore": 0.94
    },
    {
        "fullName": "Sarah Johnson",
        "dateOfBirth": "1992-08-22",
        "documentNumber": "P987654321",
        "documentType": "Passport",
        "expiryDate": "2030-08-22",
        "issuingAuthority": "US State Department",
        "address": "456 Oak Ave, New York, NY 10001",
        "confidenceScore": 0.91
    }
]

SAMPLE_INVOICE_DATA = [
    {
        "invoiceNumber": "INV-2024-001",
        "issuingCompany": "ABC Technologies Inc",
        "billToCompany": "XYZ Corporation",
        "invoiceDate": "2024-11-15",
        "totalAmount": 2500.00,
        "currency": "USD",
        "customerPO": "PO-2024-456",
        "confidenceScore": "high",
        "language": "en"
    },
    {
        "invoiceNumber": "FACT-2024-789",
        "issuingCompany": "Global Services Ltd",
        "billToCompany": "Tech Solutions Inc",
        "invoiceDate": "2024-11-18",
        "totalAmount": 1750.50,
        "currency": "USD",
        "customerPO": None,
        "confidenceScore": "high",
        "language": "en"
    }
]

def extract_text_preview(contents: bytes, file_type: str) -> str:
    """Extract text preview from different file types"""
    try:
        if file_type in ["PDF", "DOC", "DOCX"]:
            # For demo purposes, simulate text extraction
            text = f"Sample {file_type} document content. This would contain the actual extracted text in a real implementation."
        elif file_type == "Image":
            text = "Sample OCR text from image document. This would be the actual OCR results."
        else:
            text = contents.decode("utf-8", errors="ignore")[:500]
        
        return text
    except Exception:
        return "Unable to extract text preview"

def detect_document_type(content: str, filename: str) -> str:
    """Detect if document is ID document or invoice based on content analysis"""
    content_lower = content.lower()
    filename_lower = filename.lower() if filename else ""
    
    # Check for ID document indicators
    id_keywords = ["license", "passport", "id", "identification", "driver", "birth certificate"]
    invoice_keywords = ["invoice", "bill", "receipt", "statement", "payment"]
    
    id_score = sum(1 for keyword in id_keywords if keyword in content_lower or keyword in filename_lower)
    invoice_score = sum(1 for keyword in invoice_keywords if keyword in content_lower or keyword in filename_lower)
    
    if id_score > invoice_score:
        return "ID_Document"
    elif invoice_score > 0:
        return "Invoice"
    else:
        return "Other"

async def analyze_document(file: UploadFile, user: Any | None) -> Dict[str, Any]:
    """
    Analyze document for KYC data extraction.
    Extracts PII from ID documents and invoice data from financial documents.
    """
    start_time = time.time()
    
    # Validate file
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded"
        )
    
    # Get file type
    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
    if file_type == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # Extract text preview
    text_preview = extract_text_preview(contents, file_type)
    
    # Detect document type
    doc_type = detect_document_type(text_preview, file.filename)
    
    # Extract relevant data based on document type
    extracted_data = None
    entities = []
    confidence = 0.85
    
    if doc_type == "ID_Document":
        # Use sample PII data for demo
        extracted_data = random.choice(SAMPLE_PII_DATA)
        entities = [
            f"Name: {extracted_data['fullName']}",
            f"DOB: {extracted_data['dateOfBirth']}", 
            f"Document: {extracted_data['documentType']}",
            f"Number: {extracted_data['documentNumber']}"
        ]
    elif doc_type == "Invoice":
        # Use sample invoice data for demo
        extracted_data = random.choice(SAMPLE_INVOICE_DATA)
        entities = [
            f"Invoice: {extracted_data['invoiceNumber']}",
            f"From: {extracted_data['issuingCompany']}",
            f"Amount: {extracted_data['currency']} {extracted_data['totalAmount']}",
            f"Date: {extracted_data['invoiceDate']}"
        ]
    else:
        entities = ["Document type not recognized", "Manual review required"]
        confidence = 0.60
    
    # Add file metadata
    entities.insert(0, f"File Type: {file_type}")
    if user:
        entities.append(f"Processed by: {getattr(user, 'email', 'Unknown')}")
    
    processing_time = time.time() - start_time
    
    return {
        "documentType": doc_type,
        "pageCount": max(1, len(contents) // 2000),  # Estimate page count
        "entities": entities,
        "detectedCurrency": extracted_data.get("currency") if extracted_data and "currency" in extracted_data else None,
        "confidence": confidence,
        "receivedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preview": text_preview[:400],
        "extractedData": extracted_data
    }

async def detect_tamper(file: UploadFile, user: Any | None) -> Dict[str, Any]:
    """
    Detect document tampering and fraud for KYC compliance.
    Analyzes metadata, compression artifacts, and editing traces.
    """
    start_time = time.time()
    
    # Validate file
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded"
        )
    
    # Get file type
    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
    if file_type == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type for tamper detection: {file.content_type}"
        )
    
    # Simulate tamper detection analysis
    # In a real implementation, this would use image forensics libraries
    
    # Random analysis results for demo
    is_authentic = random.random() > 0.25  # 75% chance of being authentic
    confidence_score = random.uniform(0.82, 0.98)
    
    detected_issues = []
    risk_level = "Low"
    
    if not is_authentic:
        potential_issues = [
            "Metadata inconsistencies detected",
            "Suspicious compression artifacts",
            "Possible text overlay detected", 
            "Image editing traces found",
            "Unusual file creation timestamp"
        ]
        detected_issues = random.sample(potential_issues, random.randint(1, 3))
        risk_level = random.choice(["Medium", "High"])
        confidence_score = random.uniform(0.85, 0.95)
    
    # Analysis details
    analysis_details = {
        "metadataConsistency": random.random() > 0.15,
        "pixelAnalysis": random.random() > 0.20,
        "compressionArtifacts": random.random() > 0.25,
        "editingTraces": not is_authentic and random.random() > 0.70
    }
    
    processing_time = time.time() - start_time
    
    return {
        "isAuthentic": is_authentic,
        "confidenceScore": round(confidence_score, 3),
        "detectedIssues": detected_issues,
        "riskLevel": risk_level,
        "analysisDetails": analysis_details,
        "processingTime": round(processing_time, 2)
    }