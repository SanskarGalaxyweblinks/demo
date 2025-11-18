from datetime import datetime

from pydantic import BaseModel, Field


class DocumentAnalysisResponse(BaseModel):
    document_type: str = Field(serialization_alias="documentType")
    page_count: int = Field(ge=1, alias="pageCount")
    entities: list[str]
    detected_currency: str | None = Field(default=None, alias="detectedCurrency")
    confidence: float = Field(ge=0.0, le=1.0)
    received_at: datetime = Field(default_factory=datetime.utcnow, alias="receivedAt")
    preview: str | None = None


