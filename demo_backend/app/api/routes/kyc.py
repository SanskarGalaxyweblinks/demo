# demo_backend/app/api/routes/kyc.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.kyc import KYCWorkflowRequest, KYCWorkflowResponse
from ...services.kyc_service import process_complete_kyc_workflow
from ...dependencies import get_current_user, get_db

router = APIRouter(prefix="/kyc", tags=["kyc"])

@router.post("/process-complete", response_model=KYCWorkflowResponse)
async def process_complete_kyc(
    # Form fields for email content
    subject: str = Form(..., description="Email subject"),
    body: str = Form(..., description="Email body content"),
    # Optional file attachments
    attachments: Optional[List[UploadFile]] = File(None, description="Document attachments"),
    # Dependencies
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Complete KYC workflow endpoint that processes:
    1. Email classification (Onboarding/Dispute/Other)
    2. Document analysis (if attachments provided) 
    3. Tamper detection (if attachments provided)
    4. ERP integration (customer record creation)
    
    This is the main endpoint used by the frontend complete workflow demo.
    """
    try:
        # Validate required fields
        if not subject or not body:
            raise HTTPException(
                status_code=400,
                detail="Both subject and body are required"
            )
        
        # Validate attachments if provided
        if attachments:
            for file in attachments:
                if not file.filename:
                    raise HTTPException(
                        status_code=400,
                        detail="All uploaded files must have filenames"
                    )
        
        # Create request object
        workflow_request = KYCWorkflowRequest(
            subject=subject,
            body=body,
            attachments=attachments or []
        )
        
        # Process the complete workflow
        result = await process_complete_kyc_workflow(
            request=workflow_request,
            user=user,
            db=db
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"KYC Workflow Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing complete KYC workflow: {str(e)}"
        )

@router.get("/health")
async def kyc_health_check():
    """Health check for KYC workflow service"""
    return {
        "status": "healthy",
        "service": "KYC Complete Workflow",
        "endpoints": [
            "POST /kyc/process-complete - Complete KYC automation workflow"
        ]
    }