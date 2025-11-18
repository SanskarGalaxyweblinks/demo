from pydantic import BaseModel, Field


class EmailClassificationRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=10, max_length=8000)


class EmailClassificationResponse(BaseModel):
    category: str
    priority: str
    sentiment: str
    confidence: float = Field(ge=0.0, le=1.0)
    tags: list[str]


