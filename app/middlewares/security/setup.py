from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.settings import settings
from app.middlewares.security.audit_logging import SecurityLoggingMiddleware
from app.middlewares.security.headers import SecurityHeadersMiddleware
from app.middlewares.security.rate_limit import InMemoryRateLimitMiddleware
from app.middlewares.security.request_id import RequestIDMiddleware


def configure_security_middlewares(app: FastAPI) -> None:

    if settings.SECURITY_ENABLE_HTTPS_REDIRECT:
        app.add_middleware(HTTPSRedirectMiddleware)

    app.add_middleware(
        RequestIDMiddleware, header_name=settings.SECURITY_REQUEST_ID_HEADER
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.SECURITY_TRUSTED_HOSTS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.SECURITY_CORS_ALLOW_METHODS,
        allow_headers=settings.SECURITY_CORS_ALLOW_HEADERS,
        expose_headers=[settings.SECURITY_REQUEST_ID_HEADER],
    )

    if settings.SECURITY_RATE_LIMIT_ENABLED:
        app.add_middleware(
            InMemoryRateLimitMiddleware,
            limit=settings.SECURITY_RATE_LIMIT_REQUESTS,
            window_seconds=settings.SECURITY_RATE_LIMIT_WINDOW_SECONDS,
        )

    if settings.SECURITY_LOG_SUSPICIOUS:
        app.add_middleware(SecurityLoggingMiddleware)

    app.add_middleware(SecurityHeadersMiddleware)
