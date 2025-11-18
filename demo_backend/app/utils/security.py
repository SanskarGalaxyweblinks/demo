# demo_backend/app/utils/security.py
import secrets
# NOTE: In a production application, you should use a dedicated, strong hashing library
# like 'passlib' with algorithms like bcrypt or Argon2 for password security.
# This implementation is for structure completeness and mock functionality only.

def get_password_hash(password: str) -> str:
    """Mock function to simulate password hashing."""
    return f"insecure_hash_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mock function to simulate password verification."""
    return hashed_password == f"insecure_hash_{plain_password}"

def create_session_token(length: int = 32) -> str:
    """Generates a secure, random hexadecimal string for a session token."""
    return secrets.token_hex(length)