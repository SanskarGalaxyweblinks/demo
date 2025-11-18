from fastapi import APIRouter, Depends

from ...dependencies import get_optional_user
from ...models import email as email_models
from ...services import email_service

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/classify", response_model=email_models.EmailClassificationResponse)
async def classify_email(
    payload: email_models.EmailClassificationRequest,
    user=Depends(get_optional_user),
):
    classification = email_service.classify_email(
        subject=payload.subject,
        body=payload.body,
        user=user,
    )
    return email_models.EmailClassificationResponse(**classification)


