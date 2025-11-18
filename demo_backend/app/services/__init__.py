"""
Service package initializer.

IMPORTANT:
Do NOT import service modules here.
Importing inside __init__.py triggers circular imports because
models → database → services → auth_service → models (loop).

We only expose module names via __all__ so other files can use:
    from app.services import auth_service
without requiring imports here.
"""

__all__ = [
    "auth_service",
    "database",
    "document_service",
    "email_service",
    "erp_service",
    "response_service",
]
