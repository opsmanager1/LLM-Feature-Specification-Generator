import logging
from collections.abc import AsyncGenerator, Generator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _to_asyncpg_url(url: str) -> str:
    async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    parts = urlsplit(async_url)
    query_params = parse_qsl(parts.query, keep_blank_values=True)

    normalized_query: list[tuple[str, str]] = []
    for key, value in query_params:
        if key == "sslmode":
            normalized_query.append(("ssl", value))
        else:
            normalized_query.append((key, value))

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(normalized_query),
            parts.fragment,
        )
    )


class Base(DeclarativeBase):
    pass


database_url = _normalize_database_url(settings.DATABASE_URL)
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_database_url = _to_asyncpg_url(database_url)
async_engine = create_async_engine(async_database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Failed to close database session")


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
