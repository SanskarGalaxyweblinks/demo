from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = Field(default=None, serialization_alias="fullName")
    created_at: datetime = Field(serialization_alias="createdAt")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=128, alias="fullName")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class GoogleAuthRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(default=None, alias="fullName")


class AuthResponse(BaseModel):
    token: str
    user: UserModel


