# app/models/document.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class PIIExtractionData(BaseModel):
    """Model for PII data extracted from ID documents"""
    full_name: str = Field(alias="fullName")
    date_of_birth: str = Field(alias="dateOfBirth")
    document_number: str = Field(alias="documentNumber")
    document_type: str = Field(alias="documentType")
    expiry_date: str = Field(alias="expiryDate")
    issuing_authority: str = Field(alias="issuingAuthority")
    address: str
    confidence_score: float = Field(ge=0.0, le=1.0, alias="confidenceScore")

class InvoiceExtractionData(BaseModel):
    """Model for invoice data extraction"""
    invoice_number: str = Field(alias="invoiceNumber")
    issuing_company: str = Field(alias="issuingCompany")
    bill_to_company: str = Field(alias="billToCompany")
    invoice_date: str = Field(alias="invoiceDate")
    total_amount: float = Field(alias="totalAmount")
    currency: str
    customer_po: Optional[str] = Field(default=None, alias="customerPO")
    confidence_score: str = Field(alias="confidenceScore")
    language: str

# Legacy model for backward compatibility
class InvoiceExtractionResponse(BaseModel):
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
    """Response model for document analysis (KYC data extraction)"""
    document_type: str = Field(alias="documentType", description="Type: ID_Document, Invoice, Bank_Statement, or Other")
    page_count: int = Field(ge=1, alias="pageCount")
    detected_currency: str | None = Field(default=None, alias="detectedCurrency")
    received_at: str = Field(alias="receivedAt")
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, alias="extractedData")
    processing_time: float = Field(alias="processingTime")
    
    # Fields that don't need renaming
    confidence: float = Field(ge=0.0, le=1.0)
    preview: str | None = None
    entities: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "documentType": "ID_Document",
                "pageCount": 1,
                "entities": ["Name: John Smith", "DOB: 1985-03-15", "Document: Driver License"],
                "detectedCurrency": None,
                "confidence": 0.94,
                "receivedAt": "2024-11-19 10:30:00",
                "preview": "Sample document preview text...",
                "extractedData": {
                    "fullName": "John Smith",
                    "dateOfBirth": "1985-03-15",
                    "documentNumber": "DL123456789",
                    "documentType": "Driver License"
                },
                "processingTime": 1.2
            }
        }

class TamperAnalysisDetails(BaseModel):
    """Detailed analysis breakdown for tamper detection"""
    metadata_consistency: bool = Field(alias="metadataConsistency")
    pixel_analysis: bool = Field(alias="pixelAnalysis")
    compression_artifacts: bool = Field(alias="compressionArtifacts")
    editing_traces: bool = Field(alias="editingTraces")

class TamperDetectionResponse(BaseModel):
    """Response model for document tamper detection"""
    is_authentic: bool = Field(alias="isAuthentic")
    confidence_score: float = Field(ge=0.0, le=1.0, alias="confidenceScore")
    detected_issues: List[str] = Field(alias="detectedIssues")
    risk_level: str = Field(alias="riskLevel", description="Risk level: Low, Medium, or High")
    analysis_details: TamperAnalysisDetails = Field(alias="analysisDetails")
    processing_time: float = Field(alias="processingTime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "isAuthentic": True,
                "confidenceScore": 0.94,
                "detectedIssues": [],
                "riskLevel": "Low",
                "analysisDetails": {
                    "metadataConsistency": True,
                    "pixelAnalysis": True,
                    "compressionArtifacts": True,
                    "editingTraces": False
                },
                "processingTime": 2.1
            }
        }