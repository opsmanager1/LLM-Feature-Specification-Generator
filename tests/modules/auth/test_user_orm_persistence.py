from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.modules.auth.models import User


def _make_unique_user() -> User:
    suffix = uuid4().hex[:10]
    return User(
        username=f"orm_user_{suffix}",
        email=f"orm_{suffix}@example.com",
        hashed_password="$2b$12$kAeaA3C3m6K1SZ8b0jYV8uVf5V8M0ltv8R8xX9mE0A1U6hL9I0i3K",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


@pytest.mark.db
def test_user_create_persists_record(db_session: Session) -> None:
    user = _make_unique_user()

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    loaded = db_session.query(User).filter(User.id == user.id).one_or_none()
    assert loaded is not None
    assert loaded.email == user.email
    assert loaded.username == user.username


@pytest.mark.db
def test_user_update_persists_changes(db_session: Session) -> None:
    user = _make_unique_user()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user.is_active = False
    user.username = f"updated_{user.username}"
    db_session.commit()
    db_session.refresh(user)

    loaded = db_session.query(User).filter(User.id == user.id).one()
    assert loaded.is_active is False
    assert loaded.username == user.username


@pytest.mark.db
def test_user_delete_removes_record(db_session: Session) -> None:
    user = _make_unique_user()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    db_session.delete(user)
    db_session.commit()

    loaded = db_session.query(User).filter(User.id == user_id).one_or_none()
    assert loaded is None
