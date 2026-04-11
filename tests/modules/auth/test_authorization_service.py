from collections.abc import Callable

import pytest

from app.modules.auth.errors import PermissionDeniedError
from app.modules.auth.service import AuthorizationService
from tests.factories.user_factory import UserStub


def test_ensure_superuser_allows_superuser(admin_user: UserStub) -> None:
    service = AuthorizationService()

    assert service.ensure_superuser(admin_user) is admin_user


def test_ensure_superuser_denies_non_superuser(user_factory: Callable[..., UserStub]) -> None:
    service = AuthorizationService()

    with pytest.raises(PermissionDeniedError, match="Not enough permissions"):
        service.ensure_superuser(user_factory(is_superuser=False))


def test_ensure_groups_allows_when_group_matches(user_factory: Callable[..., UserStub]) -> None:
    service = AuthorizationService()
    user = user_factory(groups=["editors", "reviewers"])

    assert service.ensure_groups(user, {"admins", "editors"}) is user


def test_ensure_groups_denies_when_no_groups_match(user_factory: Callable[..., UserStub]) -> None:
    service = AuthorizationService()
    user = user_factory(groups=["guests"])

    with pytest.raises(PermissionDeniedError, match="Requires one of groups"):
        service.ensure_groups(user, {"admins", "editors"})


def test_ensure_permission_allows_when_permission_exists(
    user_factory: Callable[..., UserStub],
) -> None:
    service = AuthorizationService()
    user = user_factory(permissions=["read:spec", "write:spec"])

    assert service.ensure_permission(user, "write:spec") is user


def test_ensure_permission_denies_when_permission_missing(
    user_factory: Callable[..., UserStub],
) -> None:
    service = AuthorizationService()
    user = user_factory(permissions=["read:spec"])

    with pytest.raises(PermissionDeniedError, match="Requires permission: write:spec"):
        service.ensure_permission(user, "write:spec")
