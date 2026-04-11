from fastapi import APIRouter

from app.core.settings import settings
from app.modules.auth.infrastructure.fastapi_users_adapter import auth_backend, fastapi_users
from app.modules.auth.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix=settings.AUTH_PREFIX, tags=[settings.AUTH_TAG])

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt")
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="")
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users")
