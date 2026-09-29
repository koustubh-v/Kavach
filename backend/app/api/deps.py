"""Shared FastAPI dependencies (dependency injection).

Provides database sessions and service instances to route handlers.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.database.session import get_db
from app.models.user import User
from app.repositories.alert import AlertRepository
from app.repositories.prediction import PredictionRepository
from app.repositories.user import UserRepository
from app.services.alert_service import AlertService
from app.services.auth import AuthService
from app.services.prediction import PredictionService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Provide a UserRepository bound to the request session."""
    return UserRepository(session)


async def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Provide an AuthService wired to the user repository."""
    return AuthService(repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Resolve a bearer token to its current user record."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required")
    return await auth_service.get_user_from_token(credentials.credentials)


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Require the authenticated user account to be active."""
    if not user.is_active:
        raise ForbiddenError("Inactive user")
    return user


async def get_current_admin_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """Require an active administrator account."""
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Administrator access required")
    return user


async def get_prediction_repository(
    session: AsyncSession = Depends(get_db),
) -> PredictionRepository:
    """Provide a PredictionRepository bound to the request session."""
    return PredictionRepository(session)


async def get_alert_repository(
    session: AsyncSession = Depends(get_db),
) -> AlertRepository:
    """Provide an AlertRepository bound to the request session."""
    return AlertRepository(session)


async def get_alert_service(
    repository: AlertRepository = Depends(get_alert_repository),
) -> AlertService:
    """Provide an AlertService wired to the repository."""
    return AlertService(repository)


async def get_prediction_service(
    repository: PredictionRepository = Depends(get_prediction_repository),
    alert_service: AlertService = Depends(get_alert_service),
) -> PredictionService:
    """Provide a PredictionService wired to the repository."""
    return PredictionService(repository, alert_service)
