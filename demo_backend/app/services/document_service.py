from __future__ import annotations

import io
import random
import json
import time
from typing import Any, Dict

from fastapi import HTTPException, UploadFile, status
# Imports for real LLM integration
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .prompts import DOCUMENT_PROMPTS, DOCUMENT_JSON_SCHEMA 
# Import the actual models
from ..models.document import DocumentAnalysisResponse, InvoiceExtractionResponse


# --- Initialize Real LLM ---
llm = ChatGroq(
    temperature=0,
    model_name="openai/gpt-oss-20b",
    api_key=os.environ.get("GROQ_API_KEY") 
)


# --- Multilingual Prompt Generator (Using constants from prompts.py) ---
def get_multilingual_prompt(text: str, detected_lang: str, logo_text_data: Dict = None) -> str:
    """Create language-specific prompt for invoice extraction"""
    
    prompts = DOCUMENT_PROMPTS
    json_schema = DOCUMENT_JSON_SCHEMA
    
    # 1. Get base instructions and schema
    lang_data = prompts.get(detected_lang, prompts["en"])
    # The JSON schema is formatted below the instructions to guide the LLM
    base_prompt = lang_data["instructions"] + "\n" + json_schema
    
    # 2. Add optional logo text instruction
    if logo_text_data and logo_text_data.get("logo_text"):
        logo_text = logo_text_data.get("logo_text", "")
        logo_instructions = lang_data["logo_instruction"].format(logo_text=logo_text)
        base_prompt += logo_instructions

    # 3. Add final instructions and truncate input text placeholder (actual text added later)
    final_instructions = lang_data["json_instructions"]
    base_prompt += final_instructions
    
    # Return the full prompt template string (will be formatted with content later)
    return base_prompt + "\n{document_content}" 


# --- Main Analysis Function ---

SUPPORTED_TYPES = {
    "application/pdf": "PDF",
    "application/msword": "DOC",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "Image",
    "image/png": "Image",
}


async def analyze_document(file: UploadFile, user: Any | None): # user is a User model from ORM
    start_time = time.time()
    
    # --- Input Validation ---
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File missing")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
    preview = preview_text(contents)
    
    # --- Heuristic for Language Detection (Basic Mock) ---
    detected_lang = "en"
    if "facture" in preview.lower():
        detected_lang = "fr"
    elif "fattura" in preview.lower():
        detected_lang = "it"
    elif "factura" in preview.lower():
        detected_lang = "es"

    # --- LLM Processing ---
    extracted_data = None
    confidence = round(random.uniform(0.6, 0.75), 2)
    entities = ["General Metadata"]
    
    # Only run complex extraction on documents containing a keyword indicating an invoice
    if any(word in preview.lower() for word in ["invoice", "facture", "fattura", "factura"]):
        try:
            # 1. Generate the LLM prompt (Instructions + JSON Schema)
            full_llm_prompt = get_multilingual_prompt(preview, detected_lang, logo_text_data=None)

            # 2. Define and invoke the LangChain pipeline (using globally initialized 'llm')
            extraction_chain = (
                ChatPromptTemplate.from_template(full_llm_prompt)
                | llm
                | JsonOutputParser()
            )

            # Invoke the chain, passing the actual truncated content to the placeholder
            llm_result = await extraction_chain.ainvoke({
                "document_content": preview[:2500]
            })
            
            # 3. Validate and populate the extraction model
            extracted_data = InvoiceExtractionResponse.model_validate(llm_result)
            
            # Update confidence and entities based on extracted data
            confidence = float(extracted_data.confidence_score in ["high", "medium"])
            entities = [
                f"Invoice # {extracted_data.invoice_number}",
                f"Issuing Company: {extracted_data.issuing_company}",
                f"Total: {extracted_data.currency} {extracted_data.total_amount}",
                f"Date: {extracted_data.invoice_date}"
            ]
            
        except Exception as e:
            # If LLM fails to return valid JSON or validation fails, capture error in logs/entities
            print(f"LLM Extraction Failed: {e}")
            confidence = round(random.uniform(0.6, 0.75), 2)
            entities = ["Structured Extraction Failed", "Fallback to Basic Metadata"]
    
    # --- Finalizing Metadata ---
    if user and hasattr(user, 'email') and user.email:
        entities.append("User:" + user.email)
        
    if file_type != "Unknown":
        entities.insert(0, f"File Type: {file_type}")
        
    execution_time = time.time() - start_time
        
    # --- Return Final Structured Response (FIXED KEYS to match Pydantic ALIASES) ---
# app/services/document_service.py

# ...
    # --- Return Final Structured Response (FIXED KEYS to match Pydantic ALIASES) ---
    return {
        "documentType": file_type, # FIXED: was 'document_type'
        "pageCount": max(1, len(contents) // 2000), # FIXED: was 'page_count'
        "entities": entities,
        "detectedCurrency": extracted_data.currency if extracted_data else None, # FIXED: was 'detected_currency'
        "confidence": confidence,
        "preview": preview[:400],
        "extractedData": extracted_data.model_dump(by_alias=True) if extracted_data else None, # FIXED: was 'extracted_data'
        "processingTime": round(execution_time, 2) # FIXED: was 'processing_time'
    }


def preview_text(contents: bytes) -> str:
    # ... (function body remains unchanged)
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents[:400].decode("latin-1", errors="ignore")

    output = io.StringIO()
    for line in text.splitlines():
        if not line.strip():
            continue
        output.write(line.strip())
        output.write("\n")
        if output.tell() > 600:
            break
    return output.getvalue().strip()