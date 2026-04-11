from app.modules.auth.errors import PermissionDeniedError
from app.modules.auth.models import User
from app.modules.auth.repository.user_repository import UserRepositoryPort


class AuthorizationService:
    def ensure_superuser(self, user: User) -> User:
        if not user.is_superuser:
            raise PermissionDeniedError("Not enough permissions")
        return user

    def ensure_groups(self, user: User, required_groups: set[str]) -> User:
        if not required_groups:
            return user
        if user.is_superuser:
            return user

        user_groups = set(getattr(user, "groups", []) or [])
        if required_groups.isdisjoint(user_groups):
            raise PermissionDeniedError(
                f"Requires one of groups: {', '.join(sorted(required_groups))}"
            )
        return user

    def ensure_permission(self, user: User, permission: str) -> User:
        if not permission:
            return user
        if user.is_superuser:
            return user

        user_permissions = set(getattr(user, "permissions", []) or [])
        if permission not in user_permissions:
            raise PermissionDeniedError(f"Requires permission: {permission}")
        return user


class UserQueryService:
    def __init__(self, repository: UserRepositoryPort) -> None:
        self._repository = repository

    async def user_exists_by_email(self, email: str) -> bool:
        return await self._repository.get_by_email(email) is not None
