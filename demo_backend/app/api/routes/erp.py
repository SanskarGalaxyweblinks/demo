from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.kyc import (
    KYCDataResponse,
    KYCDeleteResponse,
    UserKYCStats,
    KYCDashboardData,
    KYCProcessingRecord
)
from ...services.erp_service import (
    get_user_kyc_records,
    delete_user_kyc_record,
    get_user_kyc_stats,
)
from ...dependencies import get_current_user

router = APIRouter(prefix="/erp", tags=["erp"])

@router.get("/kyc/records", response_model=KYCDataResponse)
async def get_user_kyc_records_endpoint(
    limit: int = 50,
    offset: int = 0,
    user: Any = Depends(get_current_user)
):
    """Get all KYC processing records for the authenticated user."""
    try:
        records = get_user_kyc_records(user.email)
        total_count = len(records)
        paginated = records[offset:offset + limit]
        
        kyc_records = [
            KYCProcessingRecord(
                id=r.get('id', 0),
                customer_name=r.get('customer_name', 'Unknown'),
                customer_email=user.email,
                odoo_customer_id=r.get('odoo_customer_id'),
                email_classification=r.get('email_classification'),
                document_analysis=r.get('document_analysis'),
                tamper_detection=r.get('tamper_detection'),
                confidence_score=r.get('confidence_score', 0.0),
                processing_timestamp=r.get('processing_timestamp', ''),
                processed_by=r.get('processed_by', ''),
                created_date=r.get('created_date', ''),
                status=r.get('status', 'pending')
            ) for r in paginated
        ]
        
        stats_data = get_user_kyc_stats(user.email)
        stats = UserKYCStats(**stats_data)
        
        return KYCDataResponse(
            records=kyc_records,
            total_count=total_count,
            user_stats=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/kyc/records/{record_id}", response_model=KYCDeleteResponse)
async def delete_kyc_record_endpoint(
    record_id: int,
    user: Any = Depends(get_current_user)
):
    success = delete_user_kyc_record(record_id, user.email)
    if success:
        return KYCDeleteResponse(success=True, message="Deleted", deleted_record_id=record_id)
    return KYCDeleteResponse(success=False, message="Failed", deleted_record_id=None)

@router.get("/kyc/dashboard", response_model=KYCDashboardData)
async def get_kyc_dashboard_endpoint(user: Any = Depends(get_current_user)):
    """Get complete KYC dashboard data."""
    stats_data = get_user_kyc_stats(user.email)
    records = get_user_kyc_records(user.email)[:10]
    
    recent_records = []
    for r in records:
        recent_records.append({
            'id': r.get('id'),
            'customer_name': r.get('customer_name'),
            'email_category': r.get('email_classification', {}).get('category', 'Other'),
            'confidence_score': r.get('confidence_score', 0),
            'processing_date': r.get('processing_timestamp', ''),
            'status': 'pending',
            'document_types': []
        })

    return KYCDashboardData(
        user_email=user.email,
        overview_stats=UserKYCStats(**stats_data),
        recent_records=recent_records,
        processing_trends={},
        system_health={}
    )