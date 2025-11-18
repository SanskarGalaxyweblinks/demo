from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserModel(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = Field(default=None, alias="fullName")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None
    )


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    # Accept both fullName and full_name
    full_name: Optional[str] = Field(
        default=None,
        alias="fullName",
        validation_alias="full_name",
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
        alias="fullName",
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
