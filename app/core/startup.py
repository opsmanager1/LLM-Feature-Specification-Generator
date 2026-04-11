import logging
from collections.abc import Generator
from contextlib import asynccontextmanager, contextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application startup: initializing application state")
    try:
        logger.info("Application startup completed")
        yield
    finally:
        logger.info("Application shutdown completed")
