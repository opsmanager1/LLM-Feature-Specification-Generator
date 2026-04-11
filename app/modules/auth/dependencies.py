from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.modules.auth.errors import PermissionDeniedError
from app.modules.auth.infrastructure.fastapi_users_adapter import current_active_user
from app.modules.auth.models import User
from app.modules.auth.service import AuthorizationService

authz = AuthorizationService()


async def get_current_user(
    current_user: User = Depends(current_active_user),
) -> User:
    return current_user


def _map_permission_denied(exc: PermissionDeniedError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=str(exc),
    )


def require_groups(*required_groups: str) -> Callable[[User], User]:
    required = set(required_groups)

    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        try:
            return authz.ensure_groups(current_user, required)
        except PermissionDeniedError as exc:
            raise _map_permission_denied(exc) from exc

    return dependency


def require_permission(permission: str) -> Callable[[User], User]:
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        try:
            return authz.ensure_permission(current_user, permission)
        except PermissionDeniedError as exc:
            raise _map_permission_denied(exc) from exc

    return dependency
