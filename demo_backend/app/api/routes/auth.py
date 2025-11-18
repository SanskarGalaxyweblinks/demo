# demo_backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_current_user
from ...models import auth as auth_models
from ...models.user import User
from ...services import auth_service
from ...services.auth_service import UserAlreadyExists
from ...services.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_model(user: User) -> auth_models.UserModel:
    return auth_models.UserModel(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
    )


@router.post("/register", response_model=auth_models.AuthResponse, status_code=201)
async def register(
    payload: auth_models.RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await auth_service.register_user(
            db=db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    token = auth_service.issue_token_for_user(user)
    return auth_models.AuthResponse(token=token, user=_to_user_model(user))


@router.post("/login", response_model=auth_models.AuthResponse)
async def login(
    payload: auth_models.LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = auth_service.issue_token_for_user(user)
    return auth_models.AuthResponse(token=token, user=_to_user_model(user))


@router.post("/google", response_model=auth_models.AuthResponse)
async def google_login(
    payload: auth_models.GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.google_login(db, payload.email, payload.full_name)
    token = auth_service.issue_token_for_user(user)
    return auth_models.AuthResponse(token=token, user=_to_user_model(user))


@router.get("/session", response_model=auth_models.UserModel)
async def get_session(user: User = Depends(get_current_user)):
    return _to_user_model(user)


@router.post("/logout", status_code=204)
async def logout() -> None:
    # Stateless JWTs cannot be revoked server-side without additional storage.
    # We simply return 204 so the client can discard the token.
    return None