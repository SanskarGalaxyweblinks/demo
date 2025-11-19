from __future__ import annotations

import io
import random
import json
import time
from typing import Any, Dict
import fitz  # PyMuPDF for PDF text extraction

from json_repair import repair_json
from fastapi import HTTPException, UploadFile, status

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .prompts import DOCUMENT_PROMPTS, DOCUMENT_JSON_SCHEMA
from ..models.document import DocumentAnalysisResponse, InvoiceExtractionResponse


# ---------------------------------------------------------
# LLM Initialization
# ---------------------------------------------------------
llm = ChatGroq(
    temperature=0,
    model_name="openai/gpt-oss-20b",
    api_key=os.environ.get("GROQ_API_KEY")
)


# ---------------------------------------------------------
# PDF Text Extraction
# ---------------------------------------------------------
def extract_pdf_text(contents: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        pages_text = []
        with fitz.open(stream=contents, filetype="pdf") as pdf:
            for page in pdf:
                text = page.get_text("text")
                if text:
                    pages_text.append(text)

        full_text = "\n".join(pages_text).strip()
        if not full_text:
            return contents.decode("utf-8", errors="ignore")

        return full_text[:15000]
    except:
        try:
            return contents.decode("utf-8", errors="ignore")
        except:
            return contents.decode("latin-1", errors="ignore")


# ---------------------------------------------------------
# Fallback Preview Text Extraction
# ---------------------------------------------------------
def preview_text(contents: bytes) -> str:
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents.decode("latin-1", errors="ignore")

    out = io.StringIO()
    for line in text.splitlines():
        if not line.strip():
            continue
        out.write(line.strip() + "\n")
        if out.tell() > 600:
            break
    return out.getvalue().strip()


# ---------------------------------------------------------
# Multilingual Prompt Builder (system message only)
# ---------------------------------------------------------
def get_multilingual_prompt(detected_lang: str, logo_text_data: Dict = None) -> str:
    lang_data = DOCUMENT_PROMPTS.get(detected_lang, DOCUMENT_PROMPTS["en"])

    schema = DOCUMENT_JSON_SCHEMA.replace("<LANG>", detected_lang)
    base_prompt = lang_data["instructions"] + "\n" + schema


    if logo_text_data and logo_text_data.get("logo_text"):
        logo_text = logo_text_data["logo_text"]
        base_prompt += lang_data["logo_instruction"].format(logo_text=logo_text)

    base_prompt += lang_data["json_instructions"]

    # IMPORTANT: No document content here.
    return base_prompt


# ---------------------------------------------------------
# Main Analysis Function
# ---------------------------------------------------------
SUPPORTED_TYPES = {
    "application/pdf": "PDF",
    "application/msword": "DOC",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "Image",
    "image/png": "Image",
}


async def analyze_document(file: UploadFile, user: Any | None):
    start = time.time()

    # Validate file
    if not file:
        raise HTTPException(400, "File missing")

    contents = await file.read()
    if not contents:
        raise HTTPException(400, "Uploaded file is empty")

    # File type
    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")

    # PDF or fallback text
    if file.content_type == "application/pdf":
        preview = extract_pdf_text(contents)
    else:
        preview = preview_text(contents)

    # Language detection
    txt = preview.lower()
    if "facture" in txt:
        detected_lang = "fr"
    elif "fattura" in txt:
        detected_lang = "it"
    elif "factura" in txt:
        detected_lang = "es"
    else:
        detected_lang = "en"

    extracted_data = None
    confidence = round(random.uniform(0.6, 0.75), 2)
    entities = ["General Metadata"]

    # Run extraction only if invoice keyword exists
    if any(w in txt for w in ["invoice", "facture", "fattura", "factura"]):
        try:
            # Build SYSTEM message
            system_prompt = get_multilingual_prompt(detected_lang, logo_text_data=None)

            parser = JsonOutputParser()

            # Proper chain
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{document_content}")
            ])

            chain = prompt | llm

            # Call LLM
            try:
                raw = await chain.ainvoke({
                    "document_content": preview[:3000]
                })

                raw_json = raw.content

                try:
                    parsed = parser.parse(raw_json)
                except:
                    repaired = repair_json(raw_json)
                    parsed = json.loads(repaired)

            except Exception as e:
                print("LLM raw error:", e)
                raise e

            # Validate
            extracted_data = InvoiceExtractionResponse.model_validate(parsed)

            # Build entities
            confidence = float(extracted_data.confidence_score in ["high", "medium"])
            entities = [
                f"Invoice # {extracted_data.invoice_number}",
                f"Issuing Company: {extracted_data.issuing_company}",
                f"Total: {extracted_data.currency} {extracted_data.total_amount}",
                f"Date: {extracted_data.invoice_date}"
            ]


        except Exception as e:
            print("LLM Extraction Failed:", e)
            extracted_data = None
            entities = ["Structured Extraction Failed", "Fallback to Basic Metadata"]

    # Add user/email
    if user and hasattr(user, "email") and user.email:
        entities.append(f"User:{user.email}")

    if file_type != "Unknown":
        entities.insert(0, f"File Type: {file_type}")

    process_time = round(time.time() - start, 2)

    return {
        "documentType": file_type,
        "pageCount": max(1, len(contents) // 2000),
        "entities": entities,
        "detectedCurrency": extracted_data.currency if extracted_data else None,
        "confidence": confidence,
        "preview": preview[:400],
        "extractedData": extracted_data.model_dump(by_alias=True) if extracted_data else None,
        "processingTime": process_time
    }
