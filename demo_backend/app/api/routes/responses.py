# demo_backend/app/api/routes/responses.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from ...models.response import NotificationRequest, NotificationResponse
from ...services.response_service import send_customer_notification
from ...dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/send", response_model=NotificationResponse)
async def send_notification_endpoint(
    notification_request: NotificationRequest,
    user: Any = Depends(get_current_user)
):
    """
    Send automated notifications to customers during KYC process:
    - Onboarding confirmation emails
    - Document receipt confirmations
    - Verification status updates
    - Rejection notifications with next steps
    """
    try:
        result = await send_customer_notification(
            customer_email=notification_request.customer_email,
            notification_type=notification_request.notification_type,
            context_data=notification_request.context_data,
            user=user
        )
        
        return NotificationResponse(
            status="sent",
            message_id=result["message_id"],
            sent_at=result["sent_at"]
        )
        
    except Exception as e:
        print(f"Notification error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send customer notification"
        )

@router.get("/")
async def get_notifications():
    """Health check endpoint for notifications module"""
    return {"message": "Customer notifications module active"}