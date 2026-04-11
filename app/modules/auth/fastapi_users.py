"""Backward-compatible re-export for moved fastapi-users wiring.

Prefer importing from app.modules.auth.infrastructure.fastapi_users_adapter.
"""

from app.modules.auth.infrastructure.fastapi_users_adapter import (
    auth_backend,
    current_active_user,
    fastapi_users,
    get_jwt_strategy,
    get_user_db,
    get_user_manager,
)