from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import admin_auth_backend
from app.admin.views import (
    FeatureSpecRunAdmin,
    PromptTemplateAdmin,
    RefreshTokenAdmin,
    UserAdmin,
)
from app.core.database import engine


def setup_admin(app: FastAPI) -> None:
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=admin_auth_backend,
        title="Specification Generator Admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(PromptTemplateAdmin)
    admin.add_view(FeatureSpecRunAdmin)
