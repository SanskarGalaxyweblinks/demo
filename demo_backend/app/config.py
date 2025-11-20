from __future__ import annotations
import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    app_name: str = "Jupiter AI Backend"
    # Default to local postgres user/pass if env vars aren't set
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/jupiter_demo"
        )
    )
    token_expiry_minutes: int = 60 * 24  # 24 hours
    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "super-secret-dev-key-change-me")
    )
    algorithm: str = "HS256"
    
    # --- Email Settings ---
    MAIL_USERNAME: str = Field(default_factory=lambda: os.getenv("MAIL_USERNAME", ""))
    MAIL_PASSWORD: str = Field(default_factory=lambda: os.getenv("MAIL_PASSWORD", ""))
    MAIL_FROM: str = Field(default_factory=lambda: os.getenv("MAIL_FROM", "noreply@jupiterbrains.com"))
    MAIL_PORT: int = Field(default_factory=lambda: int(os.getenv("MAIL_PORT", 587)))
    MAIL_SERVER: str = Field(default_factory=lambda: os.getenv("MAIL_SERVER", "smtp.gmail.com"))
    MAIL_STARTTLS: bool = Field(default_factory=lambda: os.getenv("MAIL_STARTTLS", "True").lower() == "true")
    MAIL_SSL_TLS: bool = Field(default_factory=lambda: os.getenv("MAIL_SSL_TLS", "False").lower() == "true")

    # --- Groq AI API Settings ---
    GROQ_API_KEY: str = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", "")
    )
    GROQ_MODEL_EMAIL: str = Field(
        default_factory=lambda: os.getenv("GROQ_MODEL_EMAIL", "openai/gpt-oss-20b")
    )
    GROQ_MODEL_DOCUMENT: str = Field(
        default_factory=lambda: os.getenv("GROQ_MODEL_DOCUMENT", "openai/gpt-oss-20b")
    )
    GROQ_MAX_TOKENS: int = Field(
        default_factory=lambda: int(os.getenv("GROQ_MAX_TOKENS", "1000"))
    )
    GROQ_TEMPERATURE: float = Field(
        default_factory=lambda: float(os.getenv("GROQ_TEMPERATURE", "0.1"))
    )
    
    # --- KYC Processing Settings ---
    KYC_MAX_FILE_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("KYC_MAX_FILE_SIZE", "10485760"))  # 10MB
    )
    KYC_ALLOWED_EXTENSIONS: list[str] = Field(
        default_factory=lambda: ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    )
    KYC_MAX_DAILY_REQUESTS_PER_USER: int = Field(
        default_factory=lambda: int(os.getenv("KYC_MAX_DAILY_REQUESTS", "50"))
    )
    KYC_ENABLE_RATE_LIMITING: bool = Field(
        default_factory=lambda: os.getenv("KYC_ENABLE_RATE_LIMITING", "True").lower() == "true"
    )
    
    # --- Token Usage Tracking ---
    GROQ_DAILY_TOKEN_LIMIT: int = Field(
        default_factory=lambda: int(os.getenv("GROQ_DAILY_TOKEN_LIMIT", "100000"))
    )
    GROQ_ENABLE_TOKEN_TRACKING: bool = Field(
        default_factory=lambda: os.getenv("GROQ_ENABLE_TOKEN_TRACKING", "True").lower() == "true"
    )
    
    # --- OCR Settings ---
    TESSERACT_CMD: str = Field(
        default_factory=lambda: os.getenv("TESSERACT_CMD", "tesseract")
    )
    
    # Allow configuring allowed CORS origins via the FRONTEND_ORIGIN env var.
    cors_origins: list[str] = Field(
        default_factory=lambda: (
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:3000",
            ]
            if os.getenv("FRONTEND_ORIGIN") is None
            else [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "").split(",") if o.strip()]
        )
    )

    class Config:
        arbitrary_types_allowed = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()