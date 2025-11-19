# demo_backend/app/api/routes/documents.py
from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from typing import Any

from ...models.document import DocumentAnalysisResponse, TamperDetectionResponse
from ...services.document_service import analyze_document, detect_tamper
from ...dependencies import get_current_user  # Simple auth dependency

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    file: UploadFile,
    # Optional authentication - remove Depends() if you want it public
    user: Any = Depends(get_current_user)
):
    """
    Analyze uploaded documents for KYC data extraction:
    - Extract PII from ID documents (name, DOB, address, document numbers)
    - Extract invoice data (amounts, companies, dates)
    - Validate document format and content
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded"
            )
        
        # Check file extension
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Analyze the document
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


@router.post("/tamper-detect", response_model=TamperDetectionResponse)
async def tamper_detection_endpoint(
    file: UploadFile,
    # Optional authentication - remove Depends() if you want it public
    user: Any = Depends(get_current_user)
):
    """
    Detect document tampering and fraud:
    - Analyze metadata for manipulation signs
    - Check pixel-level editing traces
    - Assess compression artifacts
    - Generate risk assessment and confidence scores
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded"
            )
        
        # Check file extension (tamper detection works best with images and PDFs)
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported for tamper detection. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Perform tamper detection
        result = await detect_tamper(file=file, user=user)
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Tamper detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during tamper detection.",
        )