# app/models/email.py
from pydantic import BaseModel, Field
from typing import List

class EmailClassificationRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=10, max_length=8000)

class EmailClassificationResponse(BaseModel):
    category: str = Field(description="KYC category: Onboarding, Dispute, or Other")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    sentiment: str = Field(description="Email sentiment: Positive, Negative, or Neutral")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence score")
    tags: List[str] = Field(description="Additional tags detected in the email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Onboarding",
                "priority": "High", 
                "sentiment": "Positive",
                "confidence": 0.92,
                "tags": ["authenticated", "documents_mentioned", "has_attachments"]
            }
        }

# Legacy response model for backward compatibility
class LegacyEmailClassificationResponse(BaseModel):
    category: str
    reasoning: str
    summary: str
    processing_time: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Onboarding",
                "reasoning": "Email contains keywords related to new account opening and document submission",
                "summary": "Customer requesting new account with attached documents for KYC verification",
                "processing_time": 0.45
            }
        }