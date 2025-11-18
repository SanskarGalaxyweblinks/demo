# demo_backend/app/services/auth_service.py
from typing import Any
from pydantic import EmailStr
from . import database
from ..utils.security import get_password_hash, verify_password, create_session_token


class UserAlreadyExists(Exception):
    """Custom exception for registration conflict."""
    pass


def register_user(email: EmailStr, password: str, full_name: str | None) -> dict[str, Any]:
    """Register a new user, checking for existing email."""
    if database.get_user_by_email(email):
        raise UserAlreadyExists("User with this email already exists")

    password_hash = get_password_hash(password)
    user = database.create_user(email, full_name, password_hash)
    return user


def authenticate_user(email: EmailStr, password: str) -> dict[str, Any] | None:
    """Verify user credentials and return user data if successful."""
    user = database.get_user_by_email(email)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def google_login(email: EmailStr, full_name: str | None) -> dict[str, Any]:
    """Handle login for Google authenticated users, auto-registering if needed."""
    user = database.get_user_by_email(email)
    if not user:
        # Placeholder for password hash since it's required by database schema
        user = database.create_user(email, full_name, "google_login_hash")
    return user


def create_session(user_id: int) -> str:
    """Create a new session token for a user and store it in the database."""
    token = create_session_token()
    database.create_session(user_id, token)
    return token


def revoke_session(token: str) -> None:
    """Delete a session token from the database."""
    database.delete_session(token)


def get_session_user(token: str) -> dict[str, Any] | None:
    """Validate a session token and return the associated user."""
    session_data = database.get_session(token)
    if not session_data:
        return None
    user = database.get_user_by_id(session_data["user_id"])
    return user