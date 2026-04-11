import logging

from app.core.bootstrap import bootstrap_auth
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def main() -> None:
    db = SessionLocal()
    try:
        bootstrap_auth(db)
        logger.info("Admin bootstrap script completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
