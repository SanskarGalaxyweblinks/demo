from fastapi import APIRouter, Depends, File, UploadFile

from ...dependencies import get_optional_user
from ...models import document as document_models
from ...services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/analyze",
    response_model=document_models.DocumentAnalysisResponse,
)
async def analyze_document(
    file: UploadFile = File(...),
    user=Depends(get_optional_user),
):
    analysis = await document_service.analyze_document(file=file, user=user)
    return document_models.DocumentAnalysisResponse(**analysis)


