from datetime import datetime

from fastapi import APIRouter

from ...config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck():
    return {
        "status": "ok",
        "app": settings.app_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


