# demo_backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from ...dependencies import get_current_user
from ...models import auth as auth_models
from ...models.user import User
from ...services import auth_service
from ...services.database import get_db
from ...utils.email import generate_otp, send_verification_email
from ...security import get_password_hash, verify_password 

router = APIRouter(prefix="/auth", tags=["auth"])

# --- New Pydantic Models for Verification ---
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

# --- Updated Register Route ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: auth_models.RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # 1. Check if user exists
    existing_user = await auth_service._get_user_by_email(db, payload.email)
    
    if existing_user:
        if existing_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        else:
            # User exists but not verified: Resend OTP logic could go here
            # For simplicity in this demo, we raise an error or handle resend
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account exists but is not verified. Please verify your email.",
            )

    # 2. Generate OTP and Hash it
    otp = generate_otp()
    hashed_otp = get_password_hash(otp)
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    # 3. Create User (Inactive/Unverified)
    # We need to modify auth_service.register_user to accept these tokens 
    # or manually create the user here if the service doesn't support it yet.
    # Assuming we use the service but update the user object after:
    user = await auth_service.register_user(
        db=db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    
    # Update verification fields manually
    user.email_verified = False
    user.email_verification_token = hashed_otp
    user.email_verification_token_expires = otp_expires
    db.add(user)
    await db.commit()

    # 4. Send Email in Background
    background_tasks.add_task(send_verification_email, user.email, otp)

    return {"message": "Registration successful. Please check your email for a verification code."}

# --- New Verify Email Route ---
@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest, 
    db: AsyncSession = Depends(get_db)
):
    user = await auth_service._get_user_by_email(db, payload.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        return {"message": "Email already verified"}

    # Validate Token
    if not user.email_verification_token or not user.email_verification_token_expires:
        raise HTTPException(status_code=400, detail="Invalid verification request")
        
    if user.email_verification_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    if not verify_password(payload.token, user.email_verification_token):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Activate User
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires = None
    await db.commit()

    return {"message": "Email verified successfully. You can now log in."}

# --- Updated Login Route ---
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
    
    # Check Verification Status
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    token = auth_service.issue_token_for_user(user)
    
    # Helper function from your original code
    def _to_user_model(user: User):
        return auth_models.UserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        )
        
    return auth_models.AuthResponse(token=token, user=_to_user_model(user))