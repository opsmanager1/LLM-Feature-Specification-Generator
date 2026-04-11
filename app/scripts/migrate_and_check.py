from pathlib import Path
import logging

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_alembic_config() -> Config:
    config = Config(str(_project_root() / "alembic.ini"))
    config.set_main_option(
        "sqlalchemy.url", _normalize_database_url(settings.DATABASE_URL)
    )
    return config


def migrate_and_check() -> None:
    config = _build_alembic_config()

    logger.info("Running Alembic upgrade to head")
    command.upgrade(config, "head")

    script = ScriptDirectory.from_config(config)
    expected_heads = set(script.get_heads())

    engine = create_engine(
        _normalize_database_url(settings.DATABASE_URL),
        pool_pre_ping=True,
    )

    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_heads = set(context.get_current_heads())
    finally:
        engine.dispose()

    if current_heads != expected_heads:
        raise RuntimeError(
            "Alembic DB revision is not at head: "
            f"current={sorted(current_heads)} expected={sorted(expected_heads)}"
        )

    logger.info("Alembic migrations are applied and DB is in sync")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[migrations] %(message)s",
    )
    migrate_and_check()


if __name__ == "__main__":
    main()
