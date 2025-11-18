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
    # Allow configuring allowed CORS origins via the FRONTEND_ORIGIN env var.
    # FRONTEND_ORIGIN may be a single origin or a comma-separated list.
    # When not set, default to common localhost dev origins (avoid wildcard
    # when `allow_credentials=True` to prevent browser CORS errors).
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