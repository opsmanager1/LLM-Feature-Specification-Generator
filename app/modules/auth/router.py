from fastapi import APIRouter

from app.core.settings import settings
from app.modules.auth.infrastructure.fastapi_users_adapter import (
    fastapi_users,
)
from app.modules.auth.jwt_router import router as jwt_router
from app.modules.auth.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix=settings.AUTH_PREFIX, tags=[settings.AUTH_TAG])

router.include_router(jwt_router)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix=""
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users"
)
