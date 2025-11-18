from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from ...models.document import DocumentAnalysisResponse
from ...services.document_service import analyze_document
from ...dependencies import get_current_user
from typing import Any

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    file: UploadFile,
    user: Any = Depends(get_current_user)
):
    """
    Accepts a file and authenticates a user to perform document analysis.
    """
    try:
        # The core logic is delegated to the service function
        result = await analyze_document(file=file, user=user)
        return result
    except HTTPException as e:
        # Re-raise explicit HTTP exceptions (e.g., File missing/empty)
        raise e
    except Exception as e:
        # Catch all other unexpected errors
        print(f"Document analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during document analysis.",
        )