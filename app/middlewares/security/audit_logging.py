import logging
import time

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class SecurityLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        started_at = time.time()

        async def send_with_security_log(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                if status_code in {401, 403, 429}:
                    duration_ms = int((time.time() - started_at) * 1000)
                    ip = request.client.host if request.client else "unknown"
                    logger.warning(
                        "security_event status=%s method=%s path=%s ip=%s request_id=%s ua=%s duration_ms=%s",
                        status_code,
                        request.method,
                        request.url.path,
                        ip,
                        scope.get("request_id", ""),
                        request.headers.get("user-agent", "-"),
                        duration_ms,
                    )
            await send(message)

        await self.app(scope, receive, send_with_security_log)
