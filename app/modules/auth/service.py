from dataclasses import dataclass
from typing import Protocol

from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.errors import PermissionDeniedError
from app.modules.auth.models import User
from app.modules.auth.repository.user_repository import UserRepositoryPort


class UserAuthenticationPort(Protocol):
    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None: ...

    async def get(self, id): ...


class AccessTokenStrategyPort(Protocol):
    async def write_token(self, user: User) -> str: ...


class RefreshTokenStrategyPort(Protocol):
    async def write_token(self, user: User) -> str: ...

    async def read_token(self, token: str, user_manager: UserAuthenticationPort) -> User | None: ...


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str


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


class AuthSessionService:
    def __init__(
        self,
        user_authentication: UserAuthenticationPort,
        access_token_strategy: AccessTokenStrategyPort,
        refresh_token_strategy: RefreshTokenStrategyPort,
    ) -> None:
        self._user_authentication = user_authentication
        self._access_token_strategy = access_token_strategy
        self._refresh_token_strategy = refresh_token_strategy

    async def login(self, credentials: OAuth2PasswordRequestForm) -> AuthTokens | None:
        user = await self._user_authentication.authenticate(credentials)
        if user is None or not user.is_active:
            return None

        access_token = await self._access_token_strategy.write_token(user)
        refresh_token = await self._refresh_token_strategy.write_token(user)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> AuthTokens | None:
        user = await self._refresh_token_strategy.read_token(
            refresh_token, self._user_authentication
        )
        if user is None or not user.is_active:
            return None

        access_token = await self._access_token_strategy.write_token(user)
        new_refresh_token = await self._refresh_token_strategy.write_token(user)
        return AuthTokens(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, refresh_token: str | None) -> None:
        return None
