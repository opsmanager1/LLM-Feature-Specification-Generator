from collections.abc import Callable

import pytest
from fastapi import status
from fastapi.exceptions import HTTPException

from app.modules.auth.dependencies import (_map_permission_denied,
                                           get_current_user, require_groups,
                                           require_permission)
from app.modules.auth.errors import PermissionDeniedError
from tests.factories.user_factory import UserStub


@pytest.mark.asyncio
async def test_get_current_user_passthrough(
    user_factory: Callable[..., UserStub]
) -> None:
    user = user_factory()

    result = await get_current_user(user)

    assert result is user


def test_map_permission_denied_to_403_http_exception() -> None:
    exc = _map_permission_denied(PermissionDeniedError("denied"))

    assert isinstance(exc, HTTPException)
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == "denied"


@pytest.mark.asyncio
async def test_require_groups_allows_user_with_matching_group(
    user_factory: Callable[..., UserStub],
) -> None:
    user = user_factory(groups=["admins"])
    dependency = require_groups("admins", "editors")

    result = await dependency(user)

    assert result is user


@pytest.mark.asyncio
async def test_require_groups_raises_403_when_groups_missing(
    guest_user: UserStub,
) -> None:
    dependency = require_groups("admins")

    with pytest.raises(HTTPException) as error:
        await dependency(guest_user)

    assert error.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Requires one of groups" in str(error.value.detail)


@pytest.mark.asyncio
async def test_require_permission_allows_user_with_permission(
    user_factory: Callable[..., UserStub],
) -> None:
    user = user_factory(permissions=["spec:generate"])
    dependency = require_permission("spec:generate")

    result = await dependency(user)

    assert result is user


@pytest.mark.asyncio
async def test_require_permission_raises_403_when_permission_missing(
    guest_user: UserStub,
) -> None:
    dependency = require_permission("spec:generate")

    with pytest.raises(HTTPException) as error:
        await dependency(guest_user)

    assert error.value.status_code == status.HTTP_403_FORBIDDEN
    assert error.value.detail == "Requires permission: spec:generate"
