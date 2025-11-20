# demo_backend/app/models/kyc.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import UploadFile

class KYCWorkflowRequest(BaseModel):
    """Request model for complete KYC workflow processing"""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    attachments: List[UploadFile] = Field(default_factory=list, description="Document attachments")
    
    class Config:
        arbitrary_types_allowed = True  # Allow UploadFile type

class EmailClassificationResult(BaseModel):
    """Email classification results from Groq API"""
    category: str = Field(description="KYC category: Onboarding, Dispute, or Other")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    sentiment: str = Field(description="Email sentiment: Positive, Negative, or Neutral")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence score")
    tags: List[str] = Field(description="Extracted tags and keywords")
    reasoning: str = Field(description="AI reasoning for classification")

class DocumentExtractionResult(BaseModel):
    """Document data extraction results from Groq API"""
    document_type: str = Field(alias="documentType", description="Type of document analyzed")
    page_count: int = Field(alias="pageCount", description="Number of pages processed")
    entities: List[str] = Field(description="Extracted entities and data points")
    detected_currency: Optional[str] = Field(alias="detectedCurrency", default=None)
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")
    received_at: str = Field(alias="receivedAt", description="Processing timestamp")
    preview: Optional[str] = Field(description="Document preview text")
    extracted_data: Optional[Dict[str, Any]] = Field(alias="extractedData", description="Structured extracted data")
    processing_time: float = Field(alias="processingTime", description="Processing duration")

    # ADD THIS CONFIG BLOCK
    class Config:
        populate_by_name = True

class TamperDetectionResult(BaseModel):
    """Document tamper detection results"""
    is_authentic: bool = Field(alias="isAuthentic", description="Document authenticity status")
    confidence_score: float = Field(alias="confidenceScore", ge=0.0, le=1.0)
    detected_issues: List[str] = Field(alias="detectedIssues", description="List of potential tampering signs")
    risk_level: str = Field(alias="riskLevel", description="Risk assessment: Low, Medium, High")
    analysis_details: Dict[str, bool] = Field(alias="analysisDetails", description="Detailed analysis breakdown")
    processing_time: float = Field(alias="processingTime", description="Processing duration")

    # ADD THIS CONFIG BLOCK
    class Config:
        populate_by_name = True

class ERPIntegrationResult(BaseModel):
    """ERP integration results"""
    customer_id: str = Field(alias="customerId", description="Generated customer ID")
    status: str = Field(description="Integration status")
    message: str = Field(description="Status message")

    # ADD THIS CONFIG BLOCK
    class Config:
        populate_by_name = True

class KYCWorkflowResponse(BaseModel):
    """Complete KYC workflow response with all processing results"""
    email_classification: EmailClassificationResult = Field(alias="emailClassification")
    document_analysis: Optional[DocumentExtractionResult] = Field(alias="documentAnalysis", default=None)
    tamper_detection: Optional[TamperDetectionResult] = Field(alias="tamperDetection", default=None)
    erp_integration: ERPIntegrationResult = Field(alias="erpIntegration")
    processing_time: float = Field(alias="processingTime", description="Total workflow processing time")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "emailClassification": {
                    "category": "Onboarding",
                    "priority": "High",
                    "sentiment": "Positive",
                    "confidence": 0.94,
                    "tags": ["kyc_request", "documents_attached", "new_customer"],
                    "reasoning": "Email contains clear onboarding intent with document attachments"
                },
                "documentAnalysis": {
                    "documentType": "ID_Document",
                    "pageCount": 1,
                    "entities": ["Name: John Smith", "DOB: 1985-03-15", "Document: Driver License"],
                    "detectedCurrency": None,
                    "confidence": 0.91,
                    "receivedAt": "2024-11-20 10:30:00",
                    "preview": "Driver License - State of California...",
                    "extractedData": {
                        "fullName": "John Smith",
                        "dateOfBirth": "1985-03-15",
                        "documentNumber": "DL123456789",
                        "documentType": "Driver License",
                        "issuingAuthority": "California DMV"
                    },
                    "processingTime": 2.1
                },
                "tamperDetection": {
                    "isAuthentic": True,
                    "confidenceScore": 0.96,
                    "detectedIssues": [],
                    "riskLevel": "Low",
                    "analysisDetails": {
                        "metadataConsistency": True,
                        "pixelAnalysis": True,
                        "compressionArtifacts": True,
                        "editingTraces": False
                    },
                    "processingTime": 1.8
                },
                "erpIntegration": {
                    "customerId": "KYC789",
                    "status": "Success",
                    "message": "Customer record created successfully"
                },
                "processingTime": 6.5
            }
        }

# Groq API specific models for prompt engineering
class GroqEmailPrompt(BaseModel):
    """Structured prompt for Groq email classification"""
    system_message: str
    user_message: str
    expected_format: str

class GroqDocumentPrompt(BaseModel):
    """Structured prompt for Groq document analysis"""
    system_message: str
    user_message: str
    document_text: str
    expected_format: str

# Response validation models for Groq API
class GroqEmailResponse(BaseModel):
    """Expected response format from Groq API for email classification"""
    category: str = Field(description="Must be one of: Onboarding, Dispute, Other")
    priority: str = Field(description="Must be one of: High, Medium, Low") 
    sentiment: str = Field(description="Must be one of: Positive, Negative, Neutral")
    confidence: float = Field(ge=0.0, le=1.0)
    tags: List[str] = Field(description="Relevant tags extracted from content")
    reasoning: str = Field(description="Explanation of classification decision")

class GroqDocumentResponse(BaseModel):
    """Expected response format from Groq API for document analysis"""
    document_type: str = Field(description="Type of document: ID_Document, Invoice, Bank_Statement, etc.")
    extracted_entities: List[str] = Field(description="List of extracted data points")
    structured_data: Dict[str, Any] = Field(description="Structured extracted data")
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str = Field(description="Brief summary of document content")