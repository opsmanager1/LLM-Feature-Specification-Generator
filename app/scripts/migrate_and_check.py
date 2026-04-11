import logging
from pathlib import Path
import re
import subprocess
import sys

logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_alembic(*args: str) -> str:
    command = [sys.executable, "-m", "alembic", *args]
    result = subprocess.run(
        command,
        cwd=_project_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _extract_revisions(raw_output: str) -> set[str]:
    revisions: set[str] = set()
    for line in raw_output.splitlines():
        match = re.match(r"^([0-9a-f]+)\b", line.strip())
        if match:
            revisions.add(match.group(1))
    return revisions


def migrate_and_check() -> None:
    logger.info("Running Alembic upgrade to head")
    _run_alembic("upgrade", "head")

    current_heads = _extract_revisions(_run_alembic("current"))
    expected_heads = _extract_revisions(_run_alembic("heads"))

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
