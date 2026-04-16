from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.database import AsyncSessionLocal
from app.core.settings import settings
from app.modules.auth.infrastructure.fastapi_users_adapter import (
    UserManager,
    UsernameAwareUserDatabase,
)
from app.modules.auth.models import User


class AdminAuthBackend(AuthenticationBackend):
    def __init__(self) -> None:
        super().__init__(secret_key=settings.SECRET_KEY)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        password = str(form.get("password", "")).strip()
        if not username or not password:
            return False

        credentials = OAuth2PasswordRequestForm(
            username=username,
            password=password,
            scope="",
            client_id=None,
            client_secret=None,
        )

        async with AsyncSessionLocal() as session:
            user_db = UsernameAwareUserDatabase(session, User)
            user_manager = UserManager(user_db)
            user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active or not user.is_superuser:
            return False

        request.session.update({"admin_user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if user_id is None:
            return False

        async with AsyncSessionLocal() as session:
            statement = select(User).where(User.id == int(user_id))
            user = await session.scalar(statement)

        if user is None or not user.is_active or not user.is_superuser:
            request.session.clear()
            return False
        return True


admin_auth_backend = AdminAuthBackend()
