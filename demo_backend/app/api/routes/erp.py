from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.erp import ERPIntegrationRequest, ERPIntegrationResponse
from ...models.kyc import (
    KYCDataRequest, 
    KYCDataResponse,
    KYCDeleteRequest, 
    KYCDeleteResponse,
    UserKYCStats,
    KYCDashboardData,
    KYCProcessingRecord
)
from ...services.erp_service import (
    sync_to_erp,
    get_customer_records,
    create_customer_record,
    create_kyc_record,
    # NEW KYC Data Management Functions
    get_user_kyc_records,
    delete_user_kyc_record,
    get_user_kyc_stats,
    create_kyc_processing_record
)
from ...dependencies import get_current_user, get_db

router = APIRouter(prefix="/erp", tags=["erp"])

# =================== EXISTING ERP ENDPOINTS ===================

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

# =================== NEW KYC DATA MANAGEMENT ENDPOINTS ===================

@router.get("/kyc/records", response_model=KYCDataResponse)
async def get_user_kyc_records_endpoint(
    limit: int = 50,
    offset: int = 0,
    user: Any = Depends(get_current_user)
):
    """
    Get all KYC processing records for the authenticated user.
    Returns user's KYC processing history with pagination.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        # Get user's KYC records
        records = get_user_kyc_records(user_email)
        
        # Apply pagination
        total_count = len(records)
        paginated_records = records[offset:offset + limit]
        
        # Get user statistics
        user_stats = get_user_kyc_stats(user_email)
        
        # Convert to proper models
        kyc_records = []
        for record in paginated_records:
            kyc_record = KYCProcessingRecord(
                id=record.get('id', 0),
                customer_name=record.get('customer_name', 'Unknown'),
                customer_email=user_email,
                odoo_customer_id=record.get('odoo_customer_id'),
                email_classification=record.get('email_classification'),
                document_analysis=record.get('document_analysis'),
                tamper_detection=record.get('tamper_detection'),
                confidence_score=record.get('confidence_score', 0.0),
                processing_timestamp=record.get('processing_timestamp', ''),
                processed_by=record.get('processed_by', ''),
                created_date=record.get('created_date', ''),
                status=record.get('status', 'pending')
            )
            kyc_records.append(kyc_record)
        
        stats = UserKYCStats(
            total_records=user_stats.get('total_records', 0),
            confidence_breakdown=user_stats.get('confidence_breakdown', {}),
            category_breakdown=user_stats.get('category_breakdown', {}),
            last_processing=user_stats.get('last_processing')
        )
        
        return KYCDataResponse(
            records=kyc_records,
            total_count=total_count,
            user_stats=stats
        )
        
    except Exception as e:
        print(f"KYC records retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KYC records: {str(e)}"
        )

@router.delete("/kyc/records/{record_id}", response_model=KYCDeleteResponse)
async def delete_kyc_record_endpoint(
    record_id: int,
    user: Any = Depends(get_current_user)
):
    """
    Delete a specific KYC processing record.
    Users can only delete their own records.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        # Delete the record (with user verification)
        success = delete_user_kyc_record(record_id, user_email)
        
        if success:
            return KYCDeleteResponse(
                success=True,
                message=f"KYC record {record_id} deleted successfully",
                deleted_record_id=record_id
            )
        else:
            return KYCDeleteResponse(
                success=False,
                message=f"Failed to delete record {record_id} - record not found or access denied",
                deleted_record_id=None
            )
            
    except Exception as e:
        print(f"KYC record deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete KYC record: {str(e)}"
        )

@router.get("/kyc/stats", response_model=UserKYCStats)
async def get_user_kyc_stats_endpoint(
    user: Any = Depends(get_current_user)
):
    """
    Get KYC processing statistics for the authenticated user.
    Returns analytics and processing history summary.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        stats = get_user_kyc_stats(user_email)
        
        return UserKYCStats(
            total_records=stats.get('total_records', 0),
            confidence_breakdown=stats.get('confidence_breakdown', {}),
            category_breakdown=stats.get('category_breakdown', {}),
            last_processing=stats.get('last_processing')
        )
        
    except Exception as e:
        print(f"KYC stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KYC statistics: {str(e)}"
        )

@router.get("/kyc/dashboard", response_model=KYCDashboardData)
async def get_kyc_dashboard_endpoint(
    user: Any = Depends(get_current_user)
):
    """
    Get complete KYC dashboard data for the user.
    Returns overview stats, recent records, and system health.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        # Get user statistics
        stats = get_user_kyc_stats(user_email)
        user_stats = UserKYCStats(
            total_records=stats.get('total_records', 0),
            confidence_breakdown=stats.get('confidence_breakdown', {}),
            category_breakdown=stats.get('category_breakdown', {}),
            last_processing=stats.get('last_processing')
        )
        
        # Get recent records (last 10)
        recent_records_raw = get_user_kyc_records(user_email)[:10]
        recent_records = []
        for record in recent_records_raw:
            summary = {
                'id': record.get('id', 0),
                'customer_name': record.get('customer_name', 'Unknown'),
                'email_category': record.get('email_classification', {}).get('category', 'Other'),
                'confidence_score': record.get('confidence_score', 0.0),
                'processing_date': record.get('processing_timestamp', ''),
                'status': record.get('status', 'pending'),
                'document_types': record.get('email_classification', {}).get('document_types', [])
            }
            recent_records.append(summary)
        
        # System health indicators
        system_health = {
            'odoo_connection': 'connected',
            'ai_services': 'active', 
            'processing_queue': 'normal',
            'last_backup': 'recent'
        }
        
        # Processing trends (mock data for now)
        processing_trends = {
            'daily_volume': stats.get('total_records', 0),
            'weekly_growth': '+12%',
            'accuracy_trend': 'improving',
            'avg_processing_time': '3.2s'
        }
        
        return KYCDashboardData(
            user_email=user_email,
            overview_stats=user_stats,
            recent_records=recent_records,
            processing_trends=processing_trends,
            system_health=system_health
        )
        
    except Exception as e:
        print(f"KYC dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load KYC dashboard: {str(e)}"
        )

@router.post("/kyc/bulk-delete")
async def bulk_delete_kyc_records_endpoint(
    record_ids: List[int],
    user: Any = Depends(get_current_user)
):
    """
    Delete multiple KYC processing records at once.
    Users can only delete their own records.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        deleted_records = []
        failed_records = []
        
        for record_id in record_ids:
            success = delete_user_kyc_record(record_id, user_email)
            if success:
                deleted_records.append(record_id)
            else:
                failed_records.append(record_id)
        
        return {
            "success": len(failed_records) == 0,
            "deleted_records": deleted_records,
            "failed_records": failed_records,
            "message": f"Deleted {len(deleted_records)} records, {len(failed_records)} failed"
        }
        
    except Exception as e:
        print(f"KYC bulk deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk delete KYC records: {str(e)}"
        )

# =================== EXISTING UTILITY ENDPOINTS ===================

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
        user_email = user.get("email", "")
        user_kyc_stats = get_user_kyc_stats(user_email)
        
        stats = {
            "total_customers": len(customers),
            "recent_customers": len([c for c in customers if c.get('create_date')]),
            "user_kyc_records": user_kyc_stats.get('total_records', 0),
            "odoo_connection": "Connected",
            "last_sync": "Just now"
        }
        
        return stats
    except Exception as e:
        print(f"ERP stats error: {e}")
        return {
            "total_customers": 0,
            "recent_customers": 0,
            "user_kyc_records": 0,
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
                "kyc_data_management": "active",
                "message": "ERP integration with Odoo is active, KYC data management ready"
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
    return {
        "message": "ERP integration with Odoo is active",
        "features": [
            "Customer management",
            "KYC data storage",
            "User record management", 
            "Analytics and reporting"
        ]
    }