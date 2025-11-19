"""
Collection of API routers grouped by domain.

This module exposes all the API route modules for the KYC automation system.
Each router handles a specific domain of functionality:

- auth: User authentication and session management
- emails: KYC email classification (Onboarding/Dispute/Other)
- documents: Document extraction and tamper detection
- erp: Customer records and ERP integration
- health: System health checks
"""

from . import auth
from . import documents
from . import emails
from . import erp
from . import health

__all__ = [
    "auth",
    "documents", 
    "emails",
    "erp",
    "health",
]