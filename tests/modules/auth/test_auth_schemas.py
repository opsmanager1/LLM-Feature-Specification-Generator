import pytest

from app.modules.auth.schemas import UserCreate


@pytest.mark.unit
def test_user_create_rejects_superuser_flag() -> None:
    with pytest.raises(ValueError):
        UserCreate(
            email="user@example.com",
            password="StrongPass123!",
            username="user",
            is_superuser=True,
        )


@pytest.mark.unit
def test_user_create_defaults_to_non_superuser() -> None:
    user = UserCreate(
        email="user@example.com",
        password="StrongPass123!",
        username="user",
    )

    assert user.is_superuser is False
