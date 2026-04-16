
from fastapi_users import schemas
from pydantic import ConfigDict, Field, model_validator

from app.core.settings import settings


class UserRead(schemas.BaseUser[int]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(
        min_length=settings.AUTH_USERNAME_MIN_LENGTH,
        max_length=settings.AUTH_USERNAME_MAX_LENGTH,
    )
    is_superuser: bool = Field(default=False, exclude=True)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_superuser_registration(self):
        if self.is_superuser:
            raise ValueError("Setting is_superuser via public registration is forbidden")
        return self

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        properties = schema.get("properties", {})
        properties.pop("is_superuser", None)

        required = schema.get("required")
        if isinstance(required, list) and "is_superuser" in required:
            required.remove("is_superuser")
        return schema


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = Field(
        default=None,
        min_length=settings.AUTH_USERNAME_MIN_LENGTH,
        max_length=settings.AUTH_USERNAME_MAX_LENGTH,
    )
