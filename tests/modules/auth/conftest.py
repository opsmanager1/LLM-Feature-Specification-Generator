from collections.abc import Callable

import pytest

from tests.factories import make_user
from tests.factories.user_factory import UserStub


@pytest.fixture
def user_factory() -> Callable[..., UserStub]:
    def factory(
        *,
        is_superuser: bool = False,
        groups: list[str] | None = None,
        permissions: list[str] | None = None,
    ) -> UserStub:
        return make_user(
            is_superuser=is_superuser,
            groups=groups,
            permissions=permissions,
        )

    return factory


@pytest.fixture
def admin_user(user_factory: Callable[..., UserStub]) -> UserStub:
    return user_factory(is_superuser=True)


@pytest.fixture
def guest_user(user_factory: Callable[..., UserStub]) -> UserStub:
    return user_factory(groups=["guests"], permissions=["spec:read"])