# app/schemas/email.py (or wherever your email.py is located)
from pydantic import BaseModel, Field

class EmailClassificationRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=10, max_length=8000)

class EmailClassificationResponse(BaseModel):
    category: str
    reasoning: str
    summary: str
    processing_time: float = 0.0