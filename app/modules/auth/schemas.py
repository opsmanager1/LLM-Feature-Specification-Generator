
from fastapi_users import schemas
from pydantic import Field, BaseModel, EmailStr


class UserRead(schemas.BaseUser[int]):
    username: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str = Field(min_length=3, max_length=100)


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = Field(default=None, min_length=3, max_length=100)
