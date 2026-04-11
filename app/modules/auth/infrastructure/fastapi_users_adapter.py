from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.settings import settings
from app.modules.auth.models import User


class UsernameAwareUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return await self._get_user(statement)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> User | None:
        if (user := await self.user_db.get_by_username(credentials.username)) is None:
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None

        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user


async def get_user_db(
    session: AsyncSession = Depends(get_async_db),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield UsernameAwareUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(
    tokenUrl=f"{settings.API_V1_PREFIX}{settings.AUTH_PREFIX}/jwt/login"
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        * settings.ACCESS_TOKEN_MINUTE_IN_SECONDS,
    )


def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.AUTH_REFRESH_TOKEN_EXPIRE_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
