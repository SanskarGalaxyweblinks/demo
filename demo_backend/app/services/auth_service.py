from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status

from ..utils import security
from . import database


def _serialize_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row.get("full_name"),
        "created_at": datetime.fromisoformat(row["created_at"]),
    }


def register_user(email: str, password: str, full_name: str | None) -> dict[str, Any]:
    existing = database.get_user_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    password_hash = security.hash_password(password)
    user = database.create_user(email=email, full_name=full_name, password_hash=password_hash)
    return _serialize_user(user)


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    user = database.get_user_by_email(email)
    if not user:
        return None
    if not security.verify_password(password, user["password_hash"]):
        return None
    return _serialize_user(user)


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    database.create_session(user_id=user_id, token=token)
    return token


def get_user_by_token(token: str) -> dict[str, Any] | None:
    session = database.get_session(token)
    if not session:
        return None
    user = database.get_user_by_id(session["user_id"])
    return _serialize_user(user) if user else None


def revoke_session(token: str) -> None:
    database.delete_session(token)


def google_login(email: str, full_name: str | None) -> dict[str, Any]:
    user = database.get_user_by_email(email)
    if user:
        return _serialize_user(user)
    password_hash = security.hash_password(secrets.token_urlsafe(16))
    user = database.create_user(email=email, full_name=full_name, password_hash=password_hash)
    return _serialize_user(user)


