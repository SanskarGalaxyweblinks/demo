from fastapi import APIRouter
router = APIRouter(prefix="/responses", tags=["responses"])
@router.get("/")
async def get_responses():
    return {"message": "Responses module active"}