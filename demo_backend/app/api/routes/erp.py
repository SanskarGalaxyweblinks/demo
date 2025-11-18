from fastapi import APIRouter
router = APIRouter(prefix="/erp", tags=["erp"])
@router.get("/")
async def get_erp():
    return {"message": "ERP module active"}