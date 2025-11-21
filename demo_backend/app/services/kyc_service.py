# demo_backend/app/services/kyc_service.py
from __future__ import annotations

import time
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
    create_kyc_record,
    create_kyc_processing_record,
    create_customer_in_odoo
)

async def process_complete_kyc_workflow(
    request: KYCWorkflowRequest,
    user: Any,
    db: AsyncSession
) -> KYCWorkflowResponse:
    """
    Orchestrate the complete KYC workflow using real Groq AI with enhanced data storage:
    1. Email Classification - Real AI analysis of email content and intent
    2. Document Analysis - Real OCR + AI extraction from attachments
    3. Tamper Detection - Real forensic analysis of document authenticity
    4. Custom Odoo Storage - Store all AI processing results in custom models
    5. Customer Creation - Create customer record with extracted real data
    
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
    
    # Step 4: Extract customer information from AI processing results
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
    
    # Step 5: Create customer record in Odoo
    print("[KYC] Step 4: Creating customer record in Odoo ERP with real extracted data...")
    customer_id = None
    try:
        customer_id = create_customer_in_odoo(customer_name, customer_email)
        print(f"[KYC] Customer record created with ID: {customer_id}")
    except Exception as e:
        print(f"[KYC] Customer creation error: {e}")
    
    # Step 6: Store complete AI processing results in custom Odoo model
    print("[KYC] Step 5: Storing complete AI processing results in custom Odoo models...")
    processing_record_id = None
    try:
        if customer_id:
            # Prepare complete processing data for storage
            email_data = {
                "customer_name": customer_name,
                "category": email_classification.category,
                "priority": email_classification.priority,
                "sentiment": email_classification.sentiment,
                "confidence": email_classification.confidence,
                "tags": email_classification.tags,
                "reasoning": email_classification.reasoning,
                "subject": request.subject[:100],  # Truncate for storage
                "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Prepare document data (if available)
            doc_data = None
            if document_analysis:
                doc_data = {
                    "document_type": document_analysis.document_type,
                    "page_count": document_analysis.page_count,
                    "entities": document_analysis.entities,
                    "detected_currency": document_analysis.detected_currency,
                    "confidence": document_analysis.confidence,
                    "preview": document_analysis.preview,
                    "extracted_data": document_analysis.extracted_data,
                    "processing_time": document_analysis.processing_time
                }
            
            # Prepare tamper detection data (if available)
            tamper_data = None
            if tamper_detection:
                tamper_data = {
                    "is_authentic": tamper_detection.is_authentic,
                    "confidence_score": tamper_detection.confidence_score,
                    "detected_issues": tamper_detection.detected_issues,
                    "risk_level": tamper_detection.risk_level,
                    "analysis_details": tamper_detection.analysis_details,
                    "processing_time": tamper_detection.processing_time
                }
            
            # Store in custom Odoo model
            user_email = get_user_email(user)
            processing_record_id = create_kyc_processing_record(
                customer_id=customer_id,
                user_email=user_email,
                email_data=email_data,
                document_data=doc_data,
                tamper_data=tamper_data
            )
            
            print(f"[KYC] AI processing results stored in Odoo record: {processing_record_id}")
        
    except Exception as e:
        print(f"[KYC] Error storing AI processing results: {e}")
    
    # Step 7: Create traditional KYC record for backward compatibility
    try:
        # Determine document types from real file analysis
        document_types = []
        if request.attachments:
            if document_analysis and document_analysis.document_type:
                document_types.append(document_analysis.document_type)
            else:
                # Fallback to file extensions
                document_types = [f.filename.split('.')[-1].upper() for f in request.attachments if f.filename]
        
        # Create traditional KYC record
        extraction_data = prepare_extraction_data_for_legacy_system(
            email_classification=email_classification,
            document_analysis=document_analysis,
            tamper_detection=tamper_detection
        )
        
        odoo_result = create_kyc_record(
            customer_name=customer_name,
            customer_email=customer_email,
            document_types=document_types,
            extraction_data=extraction_data,
            user=user.__dict__ if user else None
        )
        
        erp_integration = ERPIntegrationResult(
            customer_id=str(odoo_result.get("customer_id", customer_id)),
            status="Success",
            message=f"Complete AI processing results stored for {customer_name} - Customer ID: {customer_id}, Processing Record: {processing_record_id}"
        )
        print(f"[KYC] Complete workflow integration successful")
        
    except Exception as e:
        print(f"[KYC] Legacy KYC record creation error: {e}")
        # Create fallback ERP response
        erp_integration = ERPIntegrationResult(
            customer_id=str(customer_id) if customer_id else f"KYC{int(time.time() % 1000)}",
            status="Partial Success", 
            message=f"AI processing completed but some storage operations failed: {str(e)}"
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

def get_user_email(user: Any) -> str:
    """Extract user email for record attribution"""
    if user:
        if hasattr(user, 'email') and user.email:
            return user.email
        elif isinstance(user, dict) and user.get('email'):
            return user['email']
    return "system@demo.com"

def prepare_extraction_data_for_legacy_system(
    email_classification: EmailClassificationResult,
    document_analysis: Optional[DocumentExtractionResult],
    tamper_detection: Optional[TamperDetectionResult]
) -> Dict[str, Any]:
    """Prepare comprehensive extraction data for legacy KYC system"""
    
    extraction_data = {
        "confidence": email_classification.confidence,
        "email_category": email_classification.category,
        "email_priority": email_classification.priority,
        "email_sentiment": email_classification.sentiment,
        "email_tags": email_classification.tags,
        "processing_method": "enhanced_ai_pipeline"
    }
    
    # Add document analysis data if available
    if document_analysis:
        extraction_data.update({
            "document_confidence": document_analysis.confidence,
            "document_type": document_analysis.document_type,
            "document_entities": document_analysis.entities,
            "document_analysis": document_analysis.extracted_data,
            "document_processing_time": document_analysis.processing_time
        })
    
    # Add tamper detection data if available
    if tamper_detection:
        extraction_data.update({
            "tamper_detected": not tamper_detection.is_authentic,
            "tamper_confidence": tamper_detection.confidence_score,
            "tamper_risk_level": tamper_detection.risk_level,
            "tamper_issues": tamper_detection.detected_issues,
            "tamper_analysis": tamper_detection.analysis_details
        })
    
    return extraction_data

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

def calculate_overall_confidence(
    email_classification: EmailClassificationResult,
    document_analysis: Optional[DocumentExtractionResult],
    tamper_detection: Optional[TamperDetectionResult]
) -> float:
    """Calculate overall confidence score from all AI processing components"""
    
    scores = [email_classification.confidence]
    
    if document_analysis:
        scores.append(document_analysis.confidence)
    
    if tamper_detection:
        scores.append(tamper_detection.confidence_score)
    
    # Weighted average with email classification being most important
    if len(scores) == 1:
        return scores[0]
    elif len(scores) == 2:
        return (scores[0] * 0.6 + scores[1] * 0.4)
    else:  # All three components
        return (scores[0] * 0.4 + scores[1] * 0.35 + scores[2] * 0.25)