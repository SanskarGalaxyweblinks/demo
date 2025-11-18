from __future__ import annotations
import os
from functools import lru_cache
from pydantic import BaseModel, Field

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
    cors_origins: list[str] = ["*"]

    class Config:
        arbitrary_types_allowed = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()