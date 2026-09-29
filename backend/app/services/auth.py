"""Authentication business logic for dashboard users."""

from uuid import UUID

import jwt

from app.core.auth import create_access_token, decode_access_token, verify_password
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenData, UserRead


class AuthService:
    """Authenticate users and resolve access tokens to current user records."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def login(self, credentials: LoginRequest) -> TokenData:
        """Verify credentials and return a signed access token."""
        user = await self._repository.get_by_email(credentials.email)
        if user is None or not verify_password(
            credentials.password, user.password_hash
        ):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("Inactive user")
        access_token = create_access_token(
            subject=str(user.id),
            email=user.email,
            role=user.role.value,
        )
        return TokenData(
            access_token=access_token,
            user=UserRead.model_validate(user),
        )

    async def get_user_from_token(self, token: str) -> User:
        """Decode a token and load its user, rejecting invalid claims."""
        try:
            claims = decode_access_token(token)
            user_id = UUID(claims["sub"])
            UserRole(claims["role"])
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise UnauthorizedError("Invalid or expired token") from exc

        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Invalid or expired token")
        return user
