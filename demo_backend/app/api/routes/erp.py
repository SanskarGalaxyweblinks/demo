from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.erp import ERPIntegrationRequest, ERPIntegrationResponse
from ...services.erp_service import (
    sync_to_erp,
    get_customer_records,
    create_customer_record,
    create_kyc_record
)
from ...dependencies import get_current_user, get_db

router = APIRouter(prefix="/erp", tags=["erp"])

@router.post("/sync", response_model=ERPIntegrationResponse)
async def sync_to_erp_endpoint(
    request: ERPIntegrationRequest,
    user: Any = Depends(get_current_user)
):
    """
    Sync customer data to Odoo ERP system.
    Creates customer record and sales opportunity in Odoo.
    """
    try:
        result = sync_to_erp(
            customer_name=request.customer_name,
            order_amount=float(request.order_amount),
            currency=request.currency,
            user=user
        )
        
        return ERPIntegrationResponse(
            record_id=result["record_id"],
            status=result["status"],
            synced=result["synced"],
            timestamp=result["timestamp"],
            payload=result.get("payload")
        )
        
    except Exception as e:
        print(f"ERP sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync to ERP: {str(e)}"
        )

@router.get("/customers")
async def get_customers_endpoint(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Get all customer records from Odoo ERP system.
    Returns list of customers from Odoo CRM.
    """
    try:
        customers = await get_customer_records(db)
        return {"customers": customers, "total": len(customers)}
    except Exception as e:
        print(f"ERP get customers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer records from Odoo"
        )

@router.post("/customers")
async def create_customer_endpoint(
    customer_data: dict,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Create a new customer record in Odoo ERP system.
    """
    try:
        customer = await create_customer_record(
            db=db,
            customer_data=customer_data,
            created_by_user=user
        )
        return customer
    except Exception as e:
        print(f"ERP create customer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer record in Odoo"
        )

@router.post("/kyc")
async def create_kyc_record_endpoint(
    request: dict,
    user: Any = Depends(get_current_user)
):
    """
    Create KYC customer record in Odoo after document processing.
    Creates customer + support ticket for verification.
    """
    try:
        result = create_kyc_record(
            customer_name=request.get("customer_name", "Unknown"),
            customer_email=request.get("customer_email", ""),
            document_types=request.get("document_types", []),
            extraction_data=request.get("extraction_data", {}),
            user=user
        )
        return result
    except Exception as e:
        print(f"ERP KYC record error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KYC record in Odoo"
        )

@router.get("/stats")
async def get_erp_stats(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Get ERP statistics from Odoo for dashboard display.
    """
    try:
        customers = await get_customer_records(db)
        
        stats = {
            "total_customers": len(customers),
            "recent_customers": len([c for c in customers if c.get('create_date')]),
            "odoo_connection": "Connected",
            "last_sync": "Just now"
        }
        
        return stats
    except Exception as e:
        print(f"ERP stats error: {e}")
        return {
            "total_customers": 0,
            "recent_customers": 0,
            "odoo_connection": "Disconnected",
            "last_sync": "Failed",
            "error": str(e)
        }

@router.get("/health")
async def erp_health_check():
    """Health check endpoint for ERP module"""
    from ...services.erp_service import _odoo_client
    
    try:
        # Test Odoo connection
        if _odoo_client.authenticate():
            return {
                "status": "healthy",
                "odoo_connection": "connected",
                "database": _odoo_client.db,
                "message": "ERP integration with Odoo is active"
            }
        else:
            return {
                "status": "unhealthy", 
                "odoo_connection": "failed",
                "message": "Failed to connect to Odoo"
            }
    except Exception as e:
        return {
            "status": "error",
            "odoo_connection": "error", 
            "error": str(e),
            "message": "ERP integration error"
        }

@router.get("/")
async def get_erp():
    """Default ERP endpoint"""
    return {"message": "ERP integration with Odoo is active"}