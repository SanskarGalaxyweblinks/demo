# demo_backend/app/api/routes/emails.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from app.models.email import EmailClassificationRequest, EmailClassificationResponse
from app.services.email_service import classify_email
from app.dependencies import get_current_user  # Simple auth dependency

router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/classify", response_model=EmailClassificationResponse)
async def classify_email_endpoint(
    email_request: EmailClassificationRequest,
    # Optional authentication - remove Depends() if you want it public
    user: Any = Depends(get_current_user)
):
    """
    Classify customer emails into KYC categories:
    - Onboarding: New customer requests with documents
    - Dispute: Account verification disputes and appeals
    - Other: General inquiries and non-KYC related emails
    """
    try:
        # Call the KYC classification service
        result = classify_email(
            subject=email_request.subject,
            body=email_request.body,
            user=user  # Pass user context for personalization
        )
        
        # Convert to response model
        return EmailClassificationResponse(
            category=result["category"],
            priority=result["priority"], 
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            tags=result["tags"]
        )
        
    except Exception as e:
        print(f"Email Classification Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing KYC email classification."
        )