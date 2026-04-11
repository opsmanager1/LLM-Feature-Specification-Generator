from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.openapi import configure_openapi_bearer_auth
from app.core.settings import settings
from app.core.startup import lifespan
from app.middlewares import configure_security_middlewares
from app.modules.auth.router import router as auth_router
from app.modules.llm.router import router as llm_router


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

configure_security_middlewares(app)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(llm_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)

configure_openapi_bearer_auth(app)
