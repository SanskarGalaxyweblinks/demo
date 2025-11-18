# demo_backend/app/dependencies.py
from fastapi import Header, HTTPException, status
from typing import Any
from .services import auth_service


def get_current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """
    FastAPI dependency function to validate the session token in the 'Authorization: Bearer <token>' header.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Expected 'Bearer'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_session_user(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Note: Returning user data as dict because the user model in routes.auth.py expects a dict
    return user