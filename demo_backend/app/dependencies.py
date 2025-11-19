# demo_backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .config import settings
from .models.user import User
from .services.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)

# Define usage limits
USAGE_LIMITS = {
    "document": 2,
    "email": 5
}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        if not email:
            raise JWTError("Missing subject claim")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# --- New Usage Limit Logic ---

class UsageLimitChecker:
    def __init__(self, feature_type: str):
        self.feature_type = feature_type

    async def __call__(
        self, 
        user: User = Depends(get_current_user), 
        db: AsyncSession = Depends(get_db)
    ):
        limit = USAGE_LIMITS.get(self.feature_type, 5)
        
        if self.feature_type == "document":
            if user.document_classifier_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Usage limit exceeded. You have used {user.document_classifier_count}/{limit} document analyses."
                )
            user.document_classifier_count += 1
            
        elif self.feature_type == "email":
            if user.email_classifier_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Usage limit exceeded. You have used {user.email_classifier_count}/{limit} email classifications."
                )
            user.email_classifier_count += 1
            
        db.add(user)
        await db.commit()
        return user