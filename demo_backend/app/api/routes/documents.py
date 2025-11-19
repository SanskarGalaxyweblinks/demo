# demo_backend/app/api/routes/documents.py
from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.document import DocumentAnalysisResponse
from ...services.document_service import analyze_document
from ...dependencies import get_current_user, UsageLimitChecker, get_db # Imported UsageLimitChecker

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    file: UploadFile,
    # Check limit before execution. The checker returns the user, so we can use it as the user dependency.
    user: Any = Depends(UsageLimitChecker("document")) 
):
    """
    Accepts a file, checks usage limits, and performs analysis.
    """
    try:
        result = await analyze_document(file=file, user=user)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Document analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during document analysis.",
        )