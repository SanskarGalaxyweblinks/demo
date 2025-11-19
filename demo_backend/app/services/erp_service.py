# app/services/erp_service.py
from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

# Sample customer data for demo purposes
SAMPLE_CUSTOMERS = [
    {
        "id": "KYC001",
        "name": "John Smith", 
        "email": "john.smith@email.com",
        "status": "onboarded",
        "document_type": "Driver License + Invoice",
        "submission_date": "2024-11-19",
        "verification_status": "verified"
    },
    {
        "id": "KYC002",
        "name": "Sarah Johnson",
        "email": "sarah.j@company.com", 
        "status": "pending",
        "document_type": "Passport + Bank Statement",
        "submission_date": "2024-11-19",
        "verification_status": "pending"
    },
    {
        "id": "KYC003", 
        "name": "Mike Chen",
        "email": "mike.chen@business.com",
        "status": "rejected",
        "document_type": "ID Card + Invoice", 
        "submission_date": "2024-11-18",
        "verification_status": "flagged"
    },
    {
        "id": "KYC004",
        "name": "Emma Davis",
        "email": "emma.davis@startup.com",
        "status": "onboarded",
        "document_type": "Passport + Utility Bill",
        "submission_date": "2024-11-18", 
        "verification_status": "verified"
    }
]

# In-memory storage for demo (in real implementation, use actual database)
_customer_records = SAMPLE_CUSTOMERS.copy()

async def get_customer_records(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Get all customer records from ERP system.
    In real implementation, this would query the actual database.
    """
    # For demo, return sample data
    return _customer_records.copy()

async def create_customer_record(
    db: AsyncSession, 
    customer_data: Dict[str, Any],
    created_by_user: Any
) -> Dict[str, Any]:
    """
    Create a new customer record in ERP system.
    Called after successful KYC onboarding process.
    """
    # Generate customer ID
    customer_id = f"KYC{random.randint(100, 999)}"
    
    # Create customer record
    customer_record = {
        "id": customer_id,
        "name": customer_data.get("name", "Unknown Customer"),
        "email": customer_data.get("email", "unknown@email.com"),
        "status": customer_data.get("status", "pending"),
        "document_type": customer_data.get("document_type", "Not specified"),
        "submission_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "verification_status": customer_data.get("verification_status", "pending"),
        "created_by": getattr(created_by_user, 'email', 'system'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Add to in-memory storage (in real implementation, save to database)
    _customer_records.append(customer_record)
    
    return customer_record

async def get_customer_by_id(db: AsyncSession, customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific customer record by ID.
    """
    for customer in _customer_records:
        if customer["id"] == customer_id:
            return customer
    return None

async def delete_customer_record(
    db: AsyncSession, 
    customer_id: str, 
    deleted_by_user: Any
) -> bool:
    """
    Delete a customer record from ERP system.
    Used for data removal requests or failed KYC.
    """
    global _customer_records
    
    # Find and remove customer
    original_count = len(_customer_records)
    _customer_records = [c for c in _customer_records if c["id"] != customer_id]
    
    # Return True if a record was actually deleted
    return len(_customer_records) < original_count

async def update_customer_status(
    db: AsyncSession,
    customer_id: str, 
    new_status: str,
    verification_status: str = None
) -> Optional[Dict[str, Any]]:
    """
    Update customer onboarding status.
    """
    for customer in _customer_records:
        if customer["id"] == customer_id:
            customer["status"] = new_status
            if verification_status:
                customer["verification_status"] = verification_status
            customer["updated_at"] = datetime.utcnow().isoformat()
            return customer
    return None

def create_kyc_record(
    customer_name: str,
    customer_email: str, 
    document_types: List[str],
    extraction_data: Dict[str, Any],
    user: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Create a KYC customer record after successful processing.
    This function integrates email classification, document extraction, and tamper detection results.
    """
    customer_id = f"KYC{random.randint(1000, 9999)}"
    
    # Determine status based on processing results
    status = "pending"
    verification_status = "pending"
    
    if extraction_data.get("tamper_detected"):
        status = "rejected"
        verification_status = "flagged"
    elif extraction_data.get("confidence", 0) > 0.9:
        status = "onboarded" 
        verification_status = "verified"
    
    record = {
        "customer_id": customer_id,
        "name": customer_name,
        "email": customer_email,
        "status": status,
        "verification_status": verification_status,
        "document_types": ", ".join(document_types),
        "confidence_score": extraction_data.get("confidence", 0.0),
        "processing_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "extracted_data": extraction_data,
        "processed_by": user.get("email") if user else "system"
    }
    
    return record

# Legacy function for backward compatibility
def sync_to_erp(
    customer_name: str,
    order_amount: float,
    currency: str,
    user: dict[str, Any] | None,
):
    """
    Legacy function - now redirects to KYC customer record creation.
    """
    record_id = f"KYC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Convert old order data to customer record format
    customer_record = {
        "customer_id": record_id,
        "name": customer_name,
        "email": "legacy@example.com",
        "status": "onboarded",
        "verification_status": "verified", 
        "document_types": "Legacy Import",
        "confidence_score": 0.95,
        "processing_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "legacy_data": {
            "order_amount": order_amount,
            "currency": currency
        }
    }
    
    return {
        "record_id": record_id,
        "status": "Success", 
        "synced": True,
        "timestamp": datetime.utcnow(),
        "customer_record": customer_record,
        "note": "Converted legacy order to KYC customer record"
    }