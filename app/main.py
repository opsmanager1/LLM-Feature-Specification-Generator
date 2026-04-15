from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html

from app.api.health import router as health_router
from app.api.openapi import configure_openapi_bearer_auth
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

configure_security_middlewares(app)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(feature_spec_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)

configure_openapi_bearer_auth(app)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js",
    )
