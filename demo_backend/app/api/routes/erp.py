from fastapi import APIRouter, Depends

from ...dependencies import get_optional_user
from ...models import erp as erp_models
from ...services import erp_service

router = APIRouter(prefix="/erp", tags=["erp"])


@router.post("/sync", response_model=erp_models.ERPIntegrationResponse)
async def sync_to_erp(
    payload: erp_models.ERPIntegrationRequest,
    user=Depends(get_optional_user),
):
    result = erp_service.sync_to_erp(
        customer_name=payload.customer_name,
        order_amount=float(payload.order_amount),
        currency=payload.currency,
        user=user,
    )
    return erp_models.ERPIntegrationResponse(**result)


