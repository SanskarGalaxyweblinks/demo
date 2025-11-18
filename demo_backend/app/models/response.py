from pydantic import BaseModel, Field


class ResponseGenerationRequest(BaseModel):
    message: str = Field(min_length=10, max_length=8000)
    tone: str | None = Field(
        default="professional", description="Optional tone for the generated response"
    )


class ResponseGenerationResponse(BaseModel):
    response: str
    tone: str
    tokens_used: int = Field(ge=1, alias="tokensUsed")
    latency_ms: int = Field(ge=0, alias="latencyMs")


