from sqlalchemy import text

from app.core.startup import session_scope


def check_database_ready() -> None:
    with session_scope() as db:
        version = db.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one_or_none()
        if version is None:
            raise RuntimeError("Alembic version is missing")