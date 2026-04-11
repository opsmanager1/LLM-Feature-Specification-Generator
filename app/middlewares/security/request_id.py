import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp, header_name: str) -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get(self.header_name) or str(uuid.uuid4())
        scope["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                mutable_headers = MutableHeaders(raw=message["headers"])
                mutable_headers.setdefault(self.header_name, request_id)
            await send(message)

        await self.app(scope, receive, send_with_request_id)
