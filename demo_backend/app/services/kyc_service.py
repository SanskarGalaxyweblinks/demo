# demo_backend/app/services/kyc_service.py
from __future__ import annotations

import time
import base64
from typing import Any, Dict, List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.kyc import (
    KYCWorkflowRequest, 
    KYCWorkflowResponse, 
    EmailClassificationResult, 
    DocumentExtractionResult, 
    TamperDetectionResult, 
    ERPIntegrationResult
)
from .email_service import classify_email
from .document_service import analyze_document, detect_tamper
from .erp_service import (
    create_kyc_processing_record,
    create_customer_in_odoo
)

async def process_complete_kyc_workflow(
    request: KYCWorkflowRequest,
    user: Any,
    db: AsyncSession
) -> KYCWorkflowResponse:
    start_time = time.time()
    
    # 1. Email Classification
    print(f"[KYC] Step 1: AI analyzing email...")
    try:
        email_result = classify_email(request.subject, request.body, user.__dict__ if user else None)
        email_classification = EmailClassificationResult(**email_result)
    except Exception as e:
        print(f"[KYC] Email classification error: {e}")
        email_classification = EmailClassificationResult(
            category="Other", priority="Medium", sentiment="Neutral", confidence=0.5, tags=[], reasoning="Error"
        )
    
    # 2. Document Analysis & 3. Tamper Detection
    document_analysis = None
    tamper_detection = None
    attachments_for_erp = []

    if request.attachments:
        print(f"[KYC] Analyzing {len(request.attachments)} documents...")
        first_attachment = request.attachments[0]
        
        try:
            # Prepare attachment for Odoo (Base64 encode)
            # We need to read all attachments
            for file in request.attachments:
                await file.seek(0)
                content = await file.read()
                b64_content = base64.b64encode(content).decode('utf-8')
                attachments_for_erp.append({
                    "name": file.filename,
                    "content": b64_content
                })
                # Reset for analysis
                await file.seek(0)

            # Analyze the first one for metadata
            doc_result = await analyze_document(file=first_attachment, user=user)
            document_analysis = DocumentExtractionResult(
                document_type=doc_result["documentType"],
                page_count=doc_result["pageCount"],
                entities=doc_result["entities"],
                detected_currency=doc_result.get("detectedCurrency"),
                confidence=doc_result["confidence"],
                received_at=doc_result["receivedAt"],
                preview=doc_result.get("preview"),
                extracted_data=doc_result.get("extractedData"),
                processing_time=doc_result.get("processingTime", 0)
            )

            await first_attachment.seek(0)
            tamper_result = await detect_tamper(file=first_attachment, user=user)
            tamper_detection = TamperDetectionResult(
                is_authentic=tamper_result["isAuthentic"],
                confidence_score=tamper_result["confidenceScore"],
                detected_issues=tamper_result["detectedIssues"],
                risk_level=tamper_result["riskLevel"],
                analysis_details=tamper_result["analysisDetails"],
                processing_time=tamper_result["processingTime"]
            )
        except Exception as e:
            print(f"[KYC] Document error: {e}")

    # 4. Create Customer in Odoo Contact App
    # Extract name logic (simplified)
    customer_name = "Unknown Customer"
    if document_analysis and document_analysis.extracted_data:
        customer_name = document_analysis.extracted_data.get("fullName", customer_name)
    
    # Create/Get Customer
    customer_id = create_customer_in_odoo(customer_name, user.email if user else None)

    # 5. Create Lead in Odoo CRM with details and attachments
    email_data = {
        "customer_name": customer_name,
        "subject": request.subject,
        "category": email_classification.category,
        "confidence": email_classification.confidence,
        "tags": email_classification.tags,
        "reasoning": email_classification.reasoning,
        "sentiment": email_classification.sentiment,
        "priority": email_classification.priority
    }

    doc_data = None
    if document_analysis:
        doc_data = document_analysis.dict(by_alias=True)
    
    tamper_data = None
    if tamper_detection:
        tamper_data = tamper_detection.dict(by_alias=True)

    processing_record_id = create_kyc_processing_record(
        customer_id=customer_id if customer_id else 0,
        user_email=user.email if user else "system@demo.com",
        email_data=email_data,
        email_body=request.body,
        document_data=doc_data,
        tamper_data=tamper_data,
        attachments=attachments_for_erp
    )

    erp_result = ERPIntegrationResult(
        customerId=str(customer_id),
        status="Success" if processing_record_id else "Partial",
        message=f"Stored in Odoo CRM (ID: {processing_record_id})"
    )

    return KYCWorkflowResponse(
        email_classification=email_classification,
        document_analysis=document_analysis,
        tamper_detection=tamper_detection,
        erp_integration=erp_result,
        processing_time=round(time.time() - start_time, 2)
    )