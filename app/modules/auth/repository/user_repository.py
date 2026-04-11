from typing import Protocol

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.modules.auth.infrastructure.fastapi_users_adapter import get_user_db
from app.modules.auth.models import User


class UserRepositoryPort(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...


class FastApiUsersUserRepository(UserRepositoryPort):
    def __init__(self, user_db: SQLAlchemyUserDatabase) -> None:
        self._user_db = user_db

    async def get_by_email(self, email: str) -> User | None:
        return await self._user_db.get_by_email(email)


def get_user_repository(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> UserRepositoryPort:
    return FastApiUsersUserRepository(user_db)
