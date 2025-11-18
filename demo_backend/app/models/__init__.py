"""
Model package initializer.

IMPORTANT:
Do NOT import model modules here.
Importing models inside __init__.py creates circular imports because:
    database → models → services → auth_service → user → database (loop)

We only define __all__ so other modules can reference model names cleanly.
"""

__all__ = [
    "auth",
    "document",
    "email",
    "erp",
    "response",
    "user",
    "user_api_key",
]
