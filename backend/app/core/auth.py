"""Password hashing and JWT helpers for dashboard authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings
from app.core.constants import JWT_ALGORITHM


def hash_password(password: str) -> str:
    """Return a bcrypt hash for a plaintext password."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Passwords must not exceed 72 UTF-8 bytes")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Compare a plaintext password with a stored bcrypt hash."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        return False
    try:
        return bcrypt.checkpw(password_bytes, password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(*, subject: str, email: str, role: str) -> str:
    """Sign a user access token using the configured application secret."""
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY must be configured to issue JWTs")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    claims = {"sub": subject, "email": email, "role": role, "exp": expires_at}
    return jwt.encode(claims, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate and decode a signed JWT access token."""
    if not settings.secret_key:
        raise ValueError("JWT signing is not configured")
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "sub", "email", "role"]},
    )
    if not isinstance(payload, dict):
        raise ValueError("Invalid token payload")
    return payload
