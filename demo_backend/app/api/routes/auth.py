from fastapi import APIRouter, Depends, Header, HTTPException, status

from ...dependencies import get_current_user
from ...models import auth as auth_models
from ...services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=auth_models.AuthResponse, status_code=201)
async def register(payload: auth_models.RegisterRequest):
    user = auth_service.register_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    token = auth_service.create_session(user_id=user["id"])
    return auth_models.AuthResponse(token=token, user=auth_models.UserModel(**user))


@router.post("/login", response_model=auth_models.AuthResponse)
async def login(payload: auth_models.LoginRequest):
    user = auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = auth_service.create_session(user_id=user["id"])
    return auth_models.AuthResponse(token=token, user=auth_models.UserModel(**user))


@router.post("/google", response_model=auth_models.AuthResponse)
async def google_login(payload: auth_models.GoogleAuthRequest):
    user = auth_service.google_login(email=payload.email, full_name=payload.full_name)
    token = auth_service.create_session(user_id=user["id"])
    return auth_models.AuthResponse(token=token, user=auth_models.UserModel(**user))


@router.get("/session", response_model=auth_models.UserModel)
async def get_session(user=Depends(get_current_user)):
    return auth_models.UserModel(**user)


@router.post("/logout", status_code=204)
async def logout(authorization: str | None = Header(default=None)):
    if not authorization:
        return
    token = authorization.replace("Bearer ", "")
    auth_service.revoke_session(token)


