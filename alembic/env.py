import logging
from logging.config import fileConfig
from importlib import import_module
import pkgutil

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.database import Base, _normalize_database_url
from app.core.settings import settings


def _import_all_models() -> None:
    modules_pkg = import_module("app.modules")
    for module in pkgutil.iter_modules(modules_pkg.__path__, "app.modules."):
        model_module_name = f"{module.name}.models"
        try:
            import_module(model_module_name)
        except ModuleNotFoundError:
            continue


_import_all_models()

config = context.config
logger = logging.getLogger("alembic.runtime.migration")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", _normalize_database_url(settings.DATABASE_URL))

target_metadata = Base.metadata


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
