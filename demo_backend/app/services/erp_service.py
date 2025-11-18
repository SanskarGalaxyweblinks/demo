from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any


def sync_to_erp(
    customer_name: str,
    order_amount: float,
    currency: str,
    user: dict[str, Any] | None,
):
    record_id = f"ERP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    payload = {
        "customerName": customer_name,
        "orderAmount": float(round(Decimal(order_amount), 2)),
        "currency": currency.upper(),
    }
    if user:
        payload["syncedBy"] = user["email"]
    return {
        "record_id": record_id,
        "status": "Success",
        "synced": True,
        "timestamp": datetime.utcnow(),
        "payload": payload,
    }


