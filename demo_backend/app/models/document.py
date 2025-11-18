from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InvoiceExtractionResponse(BaseModel):
    # Core invoice data fields 
    invoice_number: str = Field(alias="invoiceNumber")
    issuing_company: str = Field(alias="issuingCompany")
    bill_to_company: str = Field(alias="billToCompany")
    invoice_date: str = Field(alias="invoiceDate")
    total_amount: float = Field(alias="totalAmount")
    currency: str
    customer_po: Optional[str] = Field(default=None, alias="customerPO")
    confidence_score: str = Field(alias="confidenceScore")
    language: str


class DocumentAnalysisResponse(BaseModel):
    # Fields with explicit aliases (must be returned as camelCase keys)
    document_type: str = Field(alias="documentType")
    page_count: int = Field(ge=1, alias="pageCount")
    detected_currency: str | None = Field(default=None, alias="detectedCurrency")
    received_at: datetime = Field(default_factory=datetime.utcnow, alias="receivedAt")
    extracted_data: Optional[InvoiceExtractionResponse] = Field(default=None, alias="extractedData")
    # Added missing processing_time field
    processing_time: float = Field(alias="processingTime") 

    # Fields that don't need renaming
    confidence: float = Field(ge=0.0, le=1.0)
    preview: str | None = None
    entities: list[str] = Field(default_factory=list)