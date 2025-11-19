# app/models/erp.py
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, condecimal

class CreateCustomerRequest(BaseModel):
    """Request model for creating a new KYC customer record"""
    name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=250)
    status: str = Field(default="pending", description="Status: onboarded, pending, or rejected")
    document_type: str = Field(description="Type of documents submitted")
    verification_status: str = Field(default="pending", description="Verification status: verified, pending, or flagged")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "status": "pending",
                "document_type": "Driver License + Bank Statement",
                "verification_status": "pending"
            }
        }

class CustomerRecordResponse(BaseModel):
    """Response model for customer records"""
    id: str
    name: str
    email: str
    status: str
    document_type: str = Field(alias="documentType")
    submission_date: str = Field(alias="submissionDate")
    verification_status: str = Field(alias="verificationStatus")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    created_at: Optional[str] = Field(default=None, alias="createdAt")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "KYC001",
                "name": "John Smith",
                "email": "john.smith@email.com", 
                "status": "onboarded",
                "documentType": "Driver License + Invoice",
                "submissionDate": "2024-11-19",
                "verificationStatus": "verified",
                "createdBy": "admin@jupiterbrains.com",
                "createdAt": "2024-11-19T10:30:00Z"
            }
        }

class CustomerRecord(BaseModel):
    """Base customer record model for internal use"""
    id: str
    name: str
    email: str
    status: str
    document_type: str
    submission_date: str
    verification_status: str

# Legacy models for backward compatibility
class ERPIntegrationRequest(BaseModel):
    """Legacy request model - now redirects to customer record creation"""
    customer_name: str = Field(min_length=2, max_length=200, alias="customerName")
    order_amount: condecimal(gt=0, max_digits=12, decimal_places=2) = Field(alias="orderAmount")
    currency: str = Field(default="USD", min_length=3, max_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "customerName": "John Smith",
                "orderAmount": 2500.00,
                "currency": "USD"
            }
        }

class ERPIntegrationResponse(BaseModel):
    """Legacy response model - now returns customer record information"""
    record_id: str = Field(alias="recordId")
    status: str
    synced: bool
    timestamp: datetime
    payload: Optional[Dict[str, Any]] = None
    customer_record: Optional[Dict[str, Any]] = Field(default=None, alias="customerRecord")
    note: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "recordId": "KYC-20241119103000",
                "status": "Success",
                "synced": True,
                "timestamp": "2024-11-19T10:30:00Z",
                "customerRecord": {
                    "customer_id": "KYC-20241119103000",
                    "name": "John Smith",
                    "email": "legacy@example.com",
                    "status": "onboarded"
                },
                "note": "Converted legacy order to KYC customer record"
            }
        }