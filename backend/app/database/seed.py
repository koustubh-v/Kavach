"""Idempotent demo-user seeding for local and demonstration deployments."""

from app.core.auth import hash_password
from app.core.config import settings
from app.core.constants import UserRole
from app.core.logging import get_logger
from app.database.session import SessionLocal
from app.repositories.user import UserRepository

logger = get_logger(__name__)

DEMO_USERS = (
    ("admin@kavach.com", "Kavach Admin", UserRole.ADMIN, settings.demo_admin_password),
    (
        "operator@kavach.com",
        "Kavach Operator",
        UserRole.OPERATOR,
        settings.demo_operator_password,
    ),
    (
        "viewer@kavach.com",
        "Kavach Viewer",
        UserRole.VIEWER,
        settings.demo_viewer_password,
    ),
)


async def seed_demo_users() -> None:
    """Create missing demo accounts when all unique passwords are configured."""
    if any(not password for _, _, _, password in DEMO_USERS):
        logger.info(
            "Demo-user seeding skipped; demo account passwords are not configured"
        )
        return

    created_count = 0
    async with SessionLocal() as session:
        repository = UserRepository(session)
        for email, full_name, role, password in DEMO_USERS:
            created = await repository.create_if_missing(
                email=email,
                password_hash=hash_password(password),
                full_name=full_name,
                role=role,
            )
            if created:
                created_count += 1

    if created_count:
        logger.info("Demo users seeded", extra={"created_count": created_count})
