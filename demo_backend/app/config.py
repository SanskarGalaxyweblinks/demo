from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    app_name: str = "Jupiter AI Backend"
    data_dir: Path = Field(default=BASE_DIR / "data")
    database_path: Path = Field(default=BASE_DIR / "data" / "app.db")
    token_expiry_minutes: int = 60 * 24  # 24 hours
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            os.getenv("FRONTEND_ORIGIN", "").strip() or "*",
        ]
    )
    secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "JUPITER_SECRET_KEY", "change-this-dev-secret-key"
        )
    )

    class Config:
        arbitrary_types_allowed = True


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()


