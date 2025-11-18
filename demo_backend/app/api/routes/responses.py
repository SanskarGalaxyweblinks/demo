from fastapi import APIRouter, Depends

from ...dependencies import get_optional_user
from ...models import response as response_models
from ...services import response_service

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("/generate", response_model=response_models.ResponseGenerationResponse)
async def generate_response(
    payload: response_models.ResponseGenerationRequest,
    user=Depends(get_optional_user),
):
    generated = response_service.generate_response(
        message=payload.message, tone=payload.tone, user=user
    )
    return response_models.ResponseGenerationResponse(**generated)


