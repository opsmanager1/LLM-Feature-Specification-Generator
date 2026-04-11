import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text

from alembic import context
from importlib import import_module

from app.core.database import Base, _normalize_database_url
from app.core.settings import settings

import_module("app.modules.auth.models")

config = context.config
logger = logging.getLogger("alembic.runtime.migration")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", _normalize_database_url(settings.DATABASE_URL))

target_metadata = Base.metadata


def _ensure_version_num_capacity(connection) -> None:
    """Prevent failures when custom revision IDs are longer than 32 chars."""
    result = connection.execute(
        text(
            """
            SELECT character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = 'alembic_version'
              AND column_name = 'version_num'
            """
        )
    ).scalar_one_or_none()

    if result is None:
        return

    if result < 255:
        logger.warning(
            "Expanding alembic_version.version_num from %s to 255 chars for revision-id safety",
            result,
        )
        connection.execute(
            text(
                "ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255)"
            )
        )


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _ensure_version_num_capacity(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
