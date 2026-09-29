"""Dashboard authentication endpoints."""

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_current_active_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenData, UserRead
from app.schemas.common import SuccessResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SuccessResponse[TokenData])
async def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse[TokenData]:
    """Authenticate a dashboard user and return a bearer token."""
    token_data = await auth_service.login(credentials)
    return SuccessResponse(message="Login successful", data=token_data)


@router.get("/me", response_model=SuccessResponse[UserRead])
async def get_me(
    user: User = Depends(get_current_active_user),
) -> SuccessResponse[UserRead]:
    """Return the authenticated user's public profile."""
    return SuccessResponse(
        message="Current user fetched",
        data=UserRead.model_validate(user),
    )
