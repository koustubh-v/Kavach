"""Database access for dashboard users."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.models.user import User


class UserRepository:
    """Read and create users using a request-scoped database session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Return a user matching the email, if present."""
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by UUID, if present."""
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_if_missing(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        role: UserRole,
    ) -> bool:
        """Insert a user only if its unique email is not already present."""
        statement = (
            insert(User)
            .values(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role=role,
                is_active=True,
            )
            .on_conflict_do_nothing(index_elements=[User.email])
        )
        result = await self._session.execute(statement)
        await self._session.commit()
        return bool(result.rowcount)
