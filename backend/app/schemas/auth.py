"""Authentication request and response schemas."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import UserRole


class LoginRequest(BaseModel):
    """Credentials submitted to the dashboard login endpoint."""

    email: str = Field(..., min_length=3, max_length=320)
    password: str = Field(..., min_length=1, max_length=128)


class UserRead(BaseModel):
    """Public user profile; never includes password hashes."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole


class TokenData(BaseModel):
    """Bearer token and the authenticated user's public profile."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead
