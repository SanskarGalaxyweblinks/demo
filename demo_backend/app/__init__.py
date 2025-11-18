"""
Jupiter AI backend package.

Initializes FastAPI application modules and exposes the application
instance for ASGI servers (see `app.main`).
"""

from .main import app  # noqa: F401


