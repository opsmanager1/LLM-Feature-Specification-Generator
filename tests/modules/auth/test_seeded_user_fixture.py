from sqlalchemy.orm import Session
import pytest

from app.modules.auth.models import User


@pytest.mark.db
def test_seed_default_user_fixture(db_session: Session, seed_default_user: User) -> None:
    loaded = db_session.query(User).filter(User.id == seed_default_user.id).one_or_none()

    assert loaded is not None
    assert loaded.email == seed_default_user.email
    assert loaded.is_superuser is True