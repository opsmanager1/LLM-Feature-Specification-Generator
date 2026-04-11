
from fastapi_users import schemas
from pydantic import Field

from app.core.settings import settings


class UserRead(schemas.BaseUser[int]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(
        min_length=settings.AUTH_USERNAME_MIN_LENGTH,
        max_length=settings.AUTH_USERNAME_MAX_LENGTH,
    )


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = Field(
        default=None,
        min_length=settings.AUTH_USERNAME_MIN_LENGTH,
        max_length=settings.AUTH_USERNAME_MAX_LENGTH,
    )
