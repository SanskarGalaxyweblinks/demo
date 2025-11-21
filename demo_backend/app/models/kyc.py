# demo_backend/app/models/kyc.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import UploadFile
from datetime import datetime

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

    class Config:
        populate_by_name = True

class ERPIntegrationResult(BaseModel):
    """ERP integration results"""
    customer_id: str = Field(alias="customerId", description="Generated customer ID")
    status: str = Field(description="Integration status")
    message: str = Field(description="Status message")

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

# =================== NEW CUSTOM ODOO STORAGE MODELS ===================

class KYCProcessingRecord(BaseModel):
    """Model for KYC processing records stored in Odoo"""
    id: int = Field(description="Odoo record ID")
    customer_name: str = Field(description="Customer name from processing")
    customer_email: str = Field(description="Customer email")
    odoo_customer_id: Optional[int] = Field(description="Related Odoo customer ID")
    email_classification: Optional[Dict[str, Any]] = Field(description="Email classification results")
    document_analysis: Optional[Dict[str, Any]] = Field(description="Document analysis results")
    tamper_detection: Optional[Dict[str, Any]] = Field(description="Tamper detection results")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall processing confidence")
    processing_timestamp: str = Field(description="When the processing occurred")
    processed_by: str = Field(description="User who initiated the processing")
    created_date: str = Field(description="When the record was created in Odoo")
    status: str = Field(default="pending", description="Processing status: pending, verified, flagged")

class KYCRecordSummary(BaseModel):
    """Summary model for KYC record display"""
    id: int = Field(description="Record ID")
    customer_name: str = Field(description="Customer name")
    email_category: str = Field(description="Email classification category")
    confidence_score: float = Field(description="Processing confidence")
    processing_date: str = Field(description="Processing date")
    status: str = Field(description="Current status")
    document_types: List[str] = Field(default_factory=list, description="Types of documents processed")

class UserKYCStats(BaseModel):
    """Statistics for user's KYC processing history"""
    total_records: int = Field(description="Total number of processed records")
    confidence_breakdown: Dict[str, int] = Field(description="Confidence level breakdown")
    category_breakdown: Dict[str, int] = Field(description="Email category breakdown")
    last_processing: Optional[str] = Field(description="Last processing timestamp")
    recent_activity: List[KYCRecordSummary] = Field(default_factory=list, description="Recent processing activities")

class KYCDataRequest(BaseModel):
    """Request model for KYC data operations"""
    user_email: str = Field(description="User's email for data filtering")
    record_id: Optional[int] = Field(description="Specific record ID for operations", default=None)
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of records to return")
    offset: int = Field(default=0, ge=0, description="Number of records to skip")

class KYCDataResponse(BaseModel):
    """Response model for KYC data retrieval"""
    records: List[KYCProcessingRecord] = Field(description="List of KYC processing records")
    total_count: int = Field(description="Total number of records available")
    user_stats: UserKYCStats = Field(description="User's processing statistics")

class KYCDeleteRequest(BaseModel):
    """Request model for deleting KYC records"""
    record_id: int = Field(description="ID of the record to delete")
    user_email: str = Field(description="Email of the user requesting deletion")

class KYCDeleteResponse(BaseModel):
    """Response model for KYC record deletion"""
    success: bool = Field(description="Whether the deletion was successful")
    message: str = Field(description="Status message")
    deleted_record_id: Optional[int] = Field(description="ID of the deleted record")

# =================== ODOO INTEGRATION MODELS ===================

class OdooCustomerData(BaseModel):
    """Model for customer data stored in Odoo"""
    odoo_id: int = Field(description="Odoo partner ID")
    name: str = Field(description="Customer name")
    email: Optional[str] = Field(description="Customer email")
    created_date: str = Field(description="Creation date in Odoo")

class OdooKYCProcessingData(BaseModel):
    """Model for KYC processing data stored in Odoo CRM leads"""
    lead_id: int = Field(description="Odoo CRM lead ID")
    customer_id: int = Field(description="Related customer ID")
    processing_summary: Dict[str, Any] = Field(description="Complete AI processing results")
    confidence_score: float = Field(description="Overall confidence score")
    processed_by: str = Field(description="User who processed the request")
    created_date: str = Field(description="Record creation date")

class ERP7DataModel(BaseModel):
    """Extended model for ERP-7 like data structure"""
    kyc_id: str = Field(description="Unique KYC processing identifier")
    customer_reference: str = Field(description="Customer reference number")
    processing_pipeline: List[str] = Field(description="Steps in the processing pipeline")
    ai_models_used: List[str] = Field(description="AI models involved in processing")
    risk_assessment: Dict[str, Any] = Field(description="Comprehensive risk assessment")
    compliance_flags: List[str] = Field(default_factory=list, description="Compliance-related flags")
    audit_trail: List[Dict[str, Any]] = Field(description="Complete audit trail of operations")

# =================== EXISTING GROQ API MODELS ===================

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

# =================== DASHBOARD & ANALYTICS MODELS ===================

class KYCDashboardData(BaseModel):
    """Complete dashboard data for KYC management"""
    user_email: str = Field(description="User's email")
    overview_stats: UserKYCStats = Field(description="Overview statistics")
    recent_records: List[KYCRecordSummary] = Field(description="Recent processing records")
    processing_trends: Dict[str, Any] = Field(description="Processing trends and patterns")
    system_health: Dict[str, Any] = Field(description="System health indicators")

class KYCAnalytics(BaseModel):
    """Analytics model for KYC processing insights"""
    processing_volume: Dict[str, int] = Field(description="Processing volume by time period")
    accuracy_metrics: Dict[str, float] = Field(description="Accuracy and confidence metrics")
    category_distribution: Dict[str, int] = Field(description="Distribution of email categories")
    document_type_breakdown: Dict[str, int] = Field(description="Types of documents processed")
    risk_assessment_summary: Dict[str, int] = Field(description="Risk level distribution")