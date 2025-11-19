# demo_backend/app/api/routes/erp.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.erp import CustomerRecord, CreateCustomerRequest, CustomerRecordResponse
from ...services.erp_service import (
    get_customer_records,
    create_customer_record,
    delete_customer_record,
    get_customer_by_id
)
from ...dependencies import get_current_user, get_db

router = APIRouter(prefix="/erp", tags=["erp"])

@router.get("/customers", response_model=List[CustomerRecordResponse])
async def get_customers_endpoint(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Get all customer records from ERP system.
    Returns list of onboarded customers with their KYC status.
    """
    try:
        customers = await get_customer_records(db)
        return customers
    except Exception as e:
        print(f"ERP get customers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer records"
        )

@router.post("/customers", response_model=CustomerRecordResponse, status_code=201)
async def create_customer_endpoint(
    customer_data: CreateCustomerRequest,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Create a new customer record in ERP system.
    Used after successful KYC onboarding process.
    """
    try:
        customer = await create_customer_record(
            db=db,
            customer_data=customer_data,
            created_by_user=user
        )
        return customer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"ERP create customer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer record"
        )

@router.get("/customers/{customer_id}", response_model=CustomerRecordResponse)
async def get_customer_endpoint(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Get a specific customer record by ID.
    """
    try:
        customer = await get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer record not found"
            )
        return customer
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERP get customer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer record"
        )

@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer_endpoint(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Delete a customer record from ERP system.
    Used for data removal requests or failed KYC.
    """
    try:
        success = await delete_customer_record(db, customer_id, deleted_by_user=user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer record not found"
            )
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERP delete customer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete customer record"
        )

@router.get("/stats")
async def get_erp_stats(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Get ERP statistics for dashboard display.
    Returns counts of customers by status.
    """
    try:
        # This could call a service function to get aggregated stats
        stats = {
            "total_customers": 0,
            "onboarded": 0, 
            "pending": 0,
            "rejected": 0
        }
        
        customers = await get_customer_records(db)
        stats["total_customers"] = len(customers)
        
        for customer in customers:
            if customer.status == "onboarded":
                stats["onboarded"] += 1
            elif customer.status == "pending":
                stats["pending"] += 1
            elif customer.status == "rejected":
                stats["rejected"] += 1
                
        return stats
    except Exception as e:
        print(f"ERP stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ERP statistics"
        )

@router.get("/")
async def get_erp():
    """Health check endpoint for ERP module"""
    return {"message": "ERP customer management module active"}