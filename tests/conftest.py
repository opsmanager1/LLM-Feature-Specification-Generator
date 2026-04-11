from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from tests.factories import make_db_user_payload
from tests.test_settings import (
    TEST_DATABASE_URL,
    TEST_DEFAULT_EMAIL,
    TEST_DEFAULT_HASHED_PASSWORD,
    TEST_DEFAULT_USERNAME,
    apply_test_environment,
)

apply_test_environment()

from app.core.database import Base
from app.modules.auth.models import User


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return TEST_DATABASE_URL


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    engine = create_engine(test_database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        engine.dispose()
        raise RuntimeError(
            "Local test Postgres is unavailable. "
            "Start Postgres and verify TEST_DATABASE_URL before running DB tests."
        ) from exc
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def seed_default_user(db_session: Session) -> User:
    default_user_payload = make_db_user_payload(
        username=TEST_DEFAULT_USERNAME,
        email=TEST_DEFAULT_EMAIL,
        hashed_password=TEST_DEFAULT_HASHED_PASSWORD,
        is_superuser=True,
    )

    user = db_session.query(User).filter(User.email == default_user_payload["email"]).one_or_none()
    if user is None:
        user = User(**default_user_payload)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user
