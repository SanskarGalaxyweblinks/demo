# demo_backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from ...models import auth as auth_models
from ...services import auth_service
from ...services.database import get_db
from ...utils.email import generate_otp, send_verification_email
from ...security import get_password_hash, verify_password 

router = APIRouter(prefix="/auth", tags=["auth"])

# --- New Pydantic Models for Verification ---
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str

# --- Updated Register Route ---
@router.post("/register", status_code=status.HTTP_201_CREATED) 
async def register(
    payload: auth_models.RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # 1. Check if user exists
    existing_user = await auth_service.get_user_by_email(db, payload.email)
    
    if existing_user:
        if existing_user.email_verified:
            raise HTTPException(status_code=400, detail="User already exists")
        else:
            raise HTTPException(status_code=409, detail="Account exists but is not verified.")

    # 2. Generate & Hash OTP
    otp = generate_otp()
    hashed_otp = get_password_hash(otp)
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    # 3. Create User
    user = await auth_service.register_user(
        db=db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        organization_name=payload.organization_name, # Pass organization name
    )
    
    # 4. Update User with OTP
    user.email_verified = False
    user.email_verification_token = hashed_otp
    user.email_verification_token_expires = otp_expires
    db.add(user)
    await db.commit()

    # 5. Send Email in Background
    background_tasks.add_task(send_verification_email, user.email, otp)

    return {"message": "Registration successful. Please check your email."}


# --- Updated Verify Email Route ---
@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest, 
    db: AsyncSession = Depends(get_db)
):
    user = await auth_service.get_user_by_email(db, payload.email)

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
    db.add(user)
    await db.commit()

    return {"message": "Email verified successfully. You can now log in."}


# --- Updated Login Route ---
@router.post("/login", response_model=auth_models.AuthResponse)
async def login(
    payload: auth_models.LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # 1. Authenticate basic credentials
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # 2. Check Verification Status
    if not user.email_verified:
        # Generate OTP
        otp = generate_otp()
        hashed_otp = get_password_hash(otp)
        otp_expires = datetime.utcnow() + timedelta(minutes=10)

        user.email_verification_token = hashed_otp
        user.email_verification_token_expires = otp_expires
        db.add(user)
        await db.commit()

        # Add email task to queue
        background_tasks.add_task(send_verification_email, user.email, otp)
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Email not verified. A new verification code has been sent."},
            background=background_tasks 
        )

    token = auth_service.issue_token_for_user(user)
    
    def _to_user_model(user):
        return auth_models.UserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization_name=user.organization_name, # Add to response model mapping
            created_at=user.created_at,
        )
        
    return auth_models.AuthResponse(token=token, user=_to_user_model(user))