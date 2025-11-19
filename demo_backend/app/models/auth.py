# demo_backend/app/models/auth.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserModel(BaseModel):
    id: int
    email: EmailStr
    # CHANGED: Use serialization_alias for output JSON key
    full_name: Optional[str] = Field(default=None, serialization_alias="fullName")
    organization_name: Optional[str] = Field(default=None, serialization_alias="organizationName") # Added
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None
    )


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    # CHANGED: Use serialization_alias instead of alias to avoid conflict
    full_name: Optional[str] = Field(
        default=None,
        serialization_alias="fullName",
        validation_alias="full_name",
    )
    
    # Added organization name field
    organization_name: Optional[str] = Field(
        default=None,
        serialization_alias="organizationName",
        validation_alias="organization_name", 
    )

    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class GoogleAuthRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(
        default=None,
        serialization_alias="fullName",
        validation_alias="full_name",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )


class AuthResponse(BaseModel):
    token: str
    user: UserModel

    model_config = ConfigDict(
        populate_by_name=True,
    )