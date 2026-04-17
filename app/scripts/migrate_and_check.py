import logging
import importlib
from pathlib import Path
import re
import subprocess
import sys

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_alembic(*args: str) -> str:
    command = [sys.executable, "-m", "alembic", *args]
    result = subprocess.run(command, cwd=_project_root(), capture_output=True, text=True)
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        details = stderr or stdout or "unknown error"
        raise RuntimeError(f"Alembic command failed: {' '.join(args)}; {details}")
    return result.stdout


def _extract_revisions(raw_output: str) -> set[str]:
    revisions: set[str] = set()
    for line in raw_output.splitlines():
        match = re.match(r"^([0-9a-f]+)\b", line.strip())
        if match:
            revisions.add(match.group(1))
    return revisions


def _has_migration_files() -> bool:
    versions_dir = _project_root() / "alembic" / "versions"
    return any(versions_dir.glob("*.py"))


def _bootstrap_schema_without_migrations() -> None:
    importlib.import_module("app.modules.auth.models")
    importlib.import_module("app.modules.feature_spec.models")
    from app.core.database import Base, engine

    logger.warning(
        "No Alembic migration files found; creating schema via SQLAlchemy metadata"
    )
    if not Base.metadata.tables:
        raise RuntimeError(
            "No SQLAlchemy models are registered; cannot bootstrap schema"
        )
    Base.metadata.create_all(bind=engine)
    logger.info(
        "Schema created via SQLAlchemy metadata (tables=%s)",
        sorted(Base.metadata.tables.keys()),
    )


def migrate_and_check() -> None:
    if not _has_migration_files():
        _bootstrap_schema_without_migrations()
        return

    logger.info("Running Alembic upgrade to head")
    _run_alembic("upgrade", "head")

    current_heads = _extract_revisions(_run_alembic("current"))
    expected_heads = _extract_revisions(_run_alembic("heads"))

    if not current_heads:
        raise RuntimeError("No migration state found in DB after alembic upgrade")

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
