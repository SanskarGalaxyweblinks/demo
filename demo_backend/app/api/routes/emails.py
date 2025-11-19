# demo_backend/app/api/routes/emails.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from app.models.email import EmailClassificationRequest, EmailClassificationResponse
from app.services.email_service import classify_email_chain
from app.dependencies import UsageLimitChecker # Import the checker

router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/classify", response_model=EmailClassificationResponse)
async def classify_email_endpoint(
    email_request: EmailClassificationRequest,
    # Check usage limit for 'email' type. This also enforces authentication.
    user: Any = Depends(UsageLimitChecker("email")) 
):
    try:
        # Call the LangChain service
        result = await classify_email_chain(
            subject=email_request.subject,
            body=email_request.body
        )
        return result
        
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing email classification via AI service."
        )