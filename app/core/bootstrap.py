import logging

from fastapi_users.password import PasswordHelper
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.modules.auth.models import User

logger = logging.getLogger(__name__)


def _resolve_bootstrap_hashed_password() -> str:
    helper = PasswordHelper()
    if not settings.AUTH_PASSWORD:
        raise RuntimeError(
            "AUTH_PASSWORD must be set for admin bootstrap user creation"
        )
    return helper.hash(settings.AUTH_PASSWORD)


def _is_bootstrap_enabled() -> bool:
    if settings.ENV.lower() == "production":
        return settings.AUTH_BOOTSTRAP_ENABLED
    return settings.AUTH_BOOTSTRAP_ENABLED or bool(settings.AUTH_EMAIL)


def bootstrap_auth(db: Session) -> None:
    if not _is_bootstrap_enabled():
        logger.info("Auth bootstrap is disabled")
        return

    if not settings.AUTH_EMAIL or not settings.AUTH_USERNAME:
        raise RuntimeError(
            "AUTH_EMAIL and AUTH_USERNAME must be set when bootstrap is enabled"
        )

    existing_user = (
        db.query(User).filter(User.email == settings.AUTH_EMAIL).one_or_none()
    )
    if existing_user is not None:
        try:
            if not existing_user.hashed_password:
                existing_user.hashed_password = _resolve_bootstrap_hashed_password()
                db.add(existing_user)
            db.commit()
        except Exception:
            logger.exception(
                "Failed to ensure bootstrap state for existing user: email=%s",
                settings.AUTH_EMAIL,
            )
            db.rollback()
            raise
        return

    try:
        user = User(
            username=settings.AUTH_USERNAME,
            email=settings.AUTH_EMAIL,
            hashed_password=_resolve_bootstrap_hashed_password(),
            is_active=True,
            is_superuser=settings.AUTH_BOOTSTRAP_SUPERUSER,
            is_verified=True,
        )
        db.add(user)
        db.commit()
    except Exception:
        logger.exception(
            "Failed to create bootstrap user: email=%s",
            settings.AUTH_EMAIL,
        )
        db.rollback()
        raise


def ensure_default_user(db: Session) -> None:
    bootstrap_auth(db)
