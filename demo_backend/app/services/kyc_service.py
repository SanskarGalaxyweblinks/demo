# demo_backend/app/services/kyc_service.py
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.kyc import KYCWorkflowRequest, KYCWorkflowResponse, EmailClassificationResult, DocumentExtractionResult, TamperDetectionResult, ERPIntegrationResult
from .email_service import classify_email
from .document_service import analyze_document, detect_tamper
from .erp_service import create_customer_record

async def process_complete_kyc_workflow(
    request: KYCWorkflowRequest,
    user: Any,
    db: AsyncSession
) -> KYCWorkflowResponse:
    """
    Orchestrate the complete KYC workflow using real Groq AI:
    1. Email Classification - Real AI analysis of email content and intent
    2. Document Analysis - Real OCR + AI extraction from attachments
    3. Tamper Detection - Real forensic analysis of document authenticity
    4. ERP Integration - Create customer record with extracted real data
    
    Args:
        request: KYC workflow request with email and attachments
        user: Authenticated user performing the request
        db: Database session for ERP operations
        
    Returns:
        Complete workflow results with all real AI processing steps
    """
    start_time = time.time()
    
    # Step 1: Email Classification using Real Groq AI
    print(f"[KYC] Step 1: AI analyzing email - Subject: {request.subject[:50]}...")
    try:
        email_result = classify_email(
            subject=request.subject,
            body=request.body,
            user=user.__dict__ if user else None
        )
        
        email_classification = EmailClassificationResult(
            category=email_result["category"],
            priority=email_result["priority"],
            sentiment=email_result["sentiment"],
            confidence=email_result["confidence"],
            tags=email_result["tags"],
            reasoning=email_result["reasoning"]
        )
        print(f"[KYC] Email classified as {email_result['category']} with {email_result['confidence']:.1%} confidence")
        
    except Exception as e:
        print(f"[KYC] Email classification error: {e}")
        # Fallback classification
        email_classification = EmailClassificationResult(
            category="Other",
            priority="Medium",
            sentiment="Neutral",
            confidence=0.5,
            tags=["processing_error"],
            reasoning="Classification failed, manual review required"
        )
    
    # Step 2 & 3: Document Analysis and Tamper Detection (if attachments provided)
    document_analysis = None
    tamper_detection = None
    
    if request.attachments and len(request.attachments) > 0:
        print(f"[KYC] Step 2: Real AI analyzing {len(request.attachments)} document(s)...")
        try:
            # Process first attachment with real AI (can be extended for all documents)
            first_attachment = request.attachments[0]
            
            # Real document analysis using Groq AI + OCR
            doc_result = await analyze_document(
                file=first_attachment,
                user=user
            )
            
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
            print(f"[KYC] Document analysis completed for {first_attachment.filename}")
            print(f"[KYC] Extracted data: {doc_result.get('extractedData', {})}")
            
            # Step 3: Real tamper detection
            print(f"[KYC] Step 3: Performing real tamper detection...")
            # Reset file pointer for tamper detection
            await first_attachment.seek(0)
            
            tamper_result = await detect_tamper(
                file=first_attachment,
                user=user
            )
            
            tamper_detection = TamperDetectionResult(
                is_authentic=tamper_result["isAuthentic"],
                confidence_score=tamper_result["confidenceScore"],
                detected_issues=tamper_result["detectedIssues"],
                risk_level=tamper_result["riskLevel"],
                analysis_details=tamper_result["analysisDetails"],
                processing_time=tamper_result["processingTime"]
            )
            print(f"[KYC] Tamper detection completed - Authentic: {tamper_result['isAuthentic']}, Risk: {tamper_result['riskLevel']}")
            
        except Exception as e:
            print(f"[KYC] Document processing error: {e}")
            # Create error response for document processing failure
            document_analysis = DocumentExtractionResult(
                document_type="Processing_Error",
                page_count=1,
                entities=[f"Error processing {len(request.attachments)} document(s): {str(e)}"],
                detected_currency=None,
                confidence=0.0,
                received_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                preview="Document processing failed - manual review required",
                extracted_data={"error": "AI processing failed", "manual_review_required": True},
                processing_time=0.1
            )
            
            tamper_detection = TamperDetectionResult(
                is_authentic=False,
                confidence_score=0.0,
                detected_issues=["Document processing failed", "Unable to perform authenticity analysis"],
                risk_level="High",
                analysis_details={
                    "metadataConsistency": False,
                    "pixelAnalysis": False,
                    "compressionArtifacts": False,
                    "editingTraces": True
                },
                processing_time=0.1
            )
    else:
        print("[KYC] Step 2-3: No documents to process, skipping analysis and tamper detection")
    
    # Step 4: ERP Integration - Create customer record with real extracted data
    print("[KYC] Step 4: Creating customer record in ERP with real extracted data...")
    try:
        # Extract customer info using real AI-extracted data
        customer_name = extract_customer_name_from_real_data(
            subject=request.subject,
            body=request.body,
            document_analysis=document_analysis,
            email_classification=email_classification
        )
        
        customer_email = extract_customer_email_from_real_data(
            body=request.body,
            user=user,
            document_analysis=document_analysis
        )
        
        # Determine document types from real file analysis
        document_types = []
        if request.attachments:
            if document_analysis and document_analysis.document_type:
                document_types.append(document_analysis.document_type)
            else:
                # Fallback to file extensions
                document_types = [f.filename.split('.')[-1].upper() for f in request.attachments if f.filename]
        
        # Determine verification status based on real tamper detection
        verification_status = determine_verification_status(
            email_classification=email_classification,
            tamper_detection=tamper_detection,
            document_analysis=document_analysis
        )
        
        # Create customer record with real extracted data
        customer_record = await create_customer_record(
            db=db,
            customer_data={
                "name": customer_name,
                "email": customer_email,
                "status": "pending" if email_classification.category == "Onboarding" else "other",
                "document_type": ", ".join(document_types) if document_types else "Email Only",
                "verification_status": verification_status
            },
            created_by_user=user
        )
        
        erp_integration = ERPIntegrationResult(
            customer_id=customer_record["id"],
            status="Success",
            message=f"Customer record created successfully for {customer_name} with real AI-extracted data"
        )
        print(f"[KYC] Customer record created: {customer_record['id']} for {customer_name}")
        
    except Exception as e:
        print(f"[KYC] ERP integration error: {e}")
        # Create fallback ERP response
        erp_integration = ERPIntegrationResult(
            customer_id=f"KYC{int(time.time() % 1000)}",
            status="Partial Success", 
            message=f"Email processed with AI but ERP integration had issues: {str(e)}"
        )
    
    # Calculate total processing time
    processing_time = round(time.time() - start_time, 2)
    
    # Construct complete response with real AI results
    workflow_response = KYCWorkflowResponse(
        email_classification=email_classification,
        document_analysis=document_analysis,
        tamper_detection=tamper_detection,
        erp_integration=erp_integration,
        processing_time=processing_time
    )
    
    print(f"[KYC] Complete AI workflow finished in {processing_time}s - Customer: {erp_integration.customer_id}")
    
    return workflow_response

def extract_customer_name_from_real_data(
    subject: str, 
    body: str, 
    document_analysis: Optional[DocumentExtractionResult],
    email_classification: EmailClassificationResult
) -> str:
    """Extract customer name prioritizing real AI-extracted data"""
    
    # Priority 1: Use real AI-extracted data from documents
    if document_analysis and document_analysis.extracted_data:
        extracted = document_analysis.extracted_data
        
        # Check for various name fields that AI might extract
        name_fields = ["fullName", "full_name", "name", "customer_name", "account_holder", "document_holder"]
        for field in name_fields:
            if field in extracted and extracted[field] and str(extracted[field]).strip():
                name = str(extracted[field]).strip()
                if len(name.split()) >= 2:  # Ensure it's a full name
                    print(f"[KYC] Customer name extracted from document AI: {name}")
                    return name
    
    # Priority 2: Extract from email subject (common pattern: "Application - John Smith")
    if " - " in subject:
        potential_name = subject.split(" - ")[-1].strip()
        if len(potential_name.split()) >= 2 and potential_name.replace(" ", "").isalpha():
            print(f"[KYC] Customer name extracted from email subject: {potential_name}")
            return potential_name
    
    # Priority 3: Use AI tags to find name patterns in email body
    if "new_customer" in email_classification.tags:
        import re
        name_patterns = [
            r"my name is ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"I am ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"from ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"([A-Z][a-z]+ [A-Z][a-z]+) here"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, body)
            if match:
                name = match.group(1)
                print(f"[KYC] Customer name extracted from email body pattern: {name}")
                return name
    
    # Ultimate fallback
    print("[KYC] Unable to extract customer name, using fallback")
    return "Unknown Customer"

def extract_customer_email_from_real_data(
    body: str, 
    user: Any,
    document_analysis: Optional[DocumentExtractionResult]
) -> str:
    """Extract customer email prioritizing real sources"""
    
    # Priority 1: Use authenticated user's email
    if user and hasattr(user, 'email') and user.email:
        print(f"[KYC] Using authenticated user email: {user.email}")
        return user.email
    
    # Priority 2: Check if AI extracted email from documents
    if document_analysis and document_analysis.extracted_data:
        extracted = document_analysis.extracted_data
        email_fields = ["email", "email_address", "contact_email"]
        
        for field in email_fields:
            if field in extracted and extracted[field]:
                email = str(extracted[field]).strip()
                if "@" in email and "." in email:
                    print(f"[KYC] Customer email extracted from document: {email}")
                    return email
    
    # Priority 3: Find email in body text
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, body)
    if emails:
        email = emails[0]
        print(f"[KYC] Customer email found in body: {email}")
        return email
    
    # Fallback
    print("[KYC] Unable to extract customer email, using fallback")
    return "customer@unknown.com"

def determine_verification_status(
    email_classification: EmailClassificationResult,
    tamper_detection: Optional[TamperDetectionResult],
    document_analysis: Optional[DocumentExtractionResult]
) -> str:
    """Determine verification status based on real AI analysis results"""
    
    # If documents were flagged as tampered
    if tamper_detection and not tamper_detection.is_authentic:
        return "flagged"
    
    # If tamper detection shows high confidence authentic
    if tamper_detection and tamper_detection.is_authentic and tamper_detection.confidence_score > 0.9:
        return "verified"
    
    # If document analysis failed
    if document_analysis and document_analysis.confidence < 0.5:
        return "pending"
    
    # If email was classified as dispute
    if email_classification.category == "Dispute":
        return "flagged"
    
    # Default for normal processing
    return "pending"