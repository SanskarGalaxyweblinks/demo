from datetime import datetime

from pydantic import BaseModel, Field, condecimal


class ERPIntegrationRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=200, alias="customerName")
    order_amount: condecimal(gt=0, max_digits=12, decimal_places=2) = Field(
        alias="orderAmount"
    )
    currency: str = Field(default="USD", min_length=3, max_length=3)


class ERPIntegrationResponse(BaseModel):
    record_id: str = Field(alias="recordId")
    status: str
    synced: bool
    timestamp: datetime
    payload: dict[str, str | float] | None = None


