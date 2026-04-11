import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.readiness import check_database_ready
from app.core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "env": settings.ENV,
    }


@router.get("/ready")
def ready() -> dict[str, str]:
    try:
        check_database_ready()
    except (SQLAlchemyError, RuntimeError) as exc:
        logger.warning("Readiness check failed: database unavailable")
        logger.debug("Database readiness failure details", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc
    return {"status": "ready"}