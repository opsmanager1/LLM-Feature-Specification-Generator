from __future__ import annotations

from dataclasses import dataclass, field

from tests.test_settings import (
    TEST_DEFAULT_EMAIL,
    TEST_DEFAULT_HASHED_PASSWORD,
    TEST_DEFAULT_USERNAME,
)


@dataclass
class UserStub:
    is_superuser: bool = False
    groups: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)


def make_user(
    *,
    is_superuser: bool = False,
    groups: list[str] | None = None,
    permissions: list[str] | None = None,
) -> UserStub:
    return UserStub(
        is_superuser=is_superuser,
        groups=list(groups or []),
        permissions=list(permissions or []),
    )


def make_db_user_payload(
    *,
    username: str = TEST_DEFAULT_USERNAME,
    email: str = TEST_DEFAULT_EMAIL,
    hashed_password: str = TEST_DEFAULT_HASHED_PASSWORD,
    is_active: bool = True,
    is_superuser: bool = True,
    is_verified: bool = True,
) -> dict[str, str | bool]:
    return {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "is_active": is_active,
        "is_superuser": is_superuser,
        "is_verified": is_verified,
    }
