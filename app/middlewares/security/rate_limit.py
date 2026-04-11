from __future__ import annotations

import logging
import time
from collections import defaultdict, deque

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.settings import settings

logger = logging.getLogger(__name__)


class InMemoryRateLimitMiddleware:
    def __init__(self, app: ASGIApp, limit: int, window_seconds: int) -> None:
        self.app = app
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def _is_limited(self, key: str, now: float) -> bool:
        timestamps = self._requests[key]
        window_start = now - self.window_seconds

        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        if len(timestamps) >= self.limit:
            return True

        timestamps.append(now)
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/health"):
            await self.app(scope, receive, send)
            return

        rate_limit_paths = settings.SECURITY_RATE_LIMIT_PATHS
        if rate_limit_paths and not any(path.startswith(prefix) for prefix in rate_limit_paths):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        ip = client[0] if client else "unknown"
        now = time.time()

        if self._is_limited(ip, now):
            request_id = scope.get("request_id", "")
            logger.warning("rate_limit_exceeded ip=%s path=%s request_id=%s", ip, path, request_id)
            response = PlainTextResponse("Too Many Requests", status_code=429)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
