"""
Collection of API routers grouped by domain.

This module exposes all the API route modules for the KYC automation system.
Each router handles a specific domain of functionality:

- auth: User authentication and session management
- kyc: Complete KYC workflow automation (MAIN FEATURE)
- emails: Individual email classification (Onboarding/Dispute/Other)
- documents: Individual document extraction and tamper detection
- erp: Customer records and ERP integration
- health: System health checks
"""

from . import auth
from . import documents
from . import emails
from . import erp
from . import health
from . import kyc

__all__ = [
    "auth",
    "documents", 
    "emails",
    "erp",
    "health",
    "kyc",
]