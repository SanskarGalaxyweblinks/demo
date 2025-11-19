# demo_backend/app/services/auth_service.py
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.user import User
from ..security import create_access_token, get_password_hash, verify_password


class UserAlreadyExists(Exception):
    """Raised when trying to register an email that already exists."""


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    email: EmailStr,
    password: str,
    full_name: str | None,
    organization_name: str | None, # Added parameter
) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise UserAlreadyExists("User with this email already exists")

    user = User(
        email=email.lower(),
        hashed_password=get_password_hash(password),
        full_name=full_name,
        organization_name=organization_name, # Store in DB
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: EmailStr,
    password: str,
) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


async def google_login(
    db: AsyncSession,
    email: EmailStr,
    full_name: str | None,
) -> User:
    user = await get_user_by_email(db, email)
    if user:
        return user

    user = User(
        email=email.lower(),
        hashed_password=get_password_hash("google-login"),
        full_name=full_name,
        email_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def issue_token_for_user(user: User) -> str:
    return create_access_token({"sub": user.email})