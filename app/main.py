from fastapi import FastAPI

from app.admin import setup_admin
from app.api.health import router as health_router
from app.api.openapi import configure_openapi_bearer_auth, configure_redoc_route
from app.core.settings import settings
from app.core.startup import lifespan
from app.middlewares import configure_security_middlewares
from app.modules.auth.router import router as auth_router
from app.modules.feature_spec.router import router as feature_spec_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    redoc_url=None,
)

setup_admin(app)

configure_security_middlewares(app)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(feature_spec_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)

configure_openapi_bearer_auth(app)
configure_redoc_route(app)
