"""API middleware.

Purpose: provide request context for HTTP requests.
Responsibilities: attach correlation identifiers to logs and responses.
Dependencies: FastAPI/Starlette request handling and core context.
Extension Notes: add auth and telemetry middleware as separate classes.
"""

from collections.abc import Awaitable, Callable, MutableMapping

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.constants import REQUEST_ID_HEADER
from core.context import clear_request_id, set_request_id
from core.container import ServiceContainer
from core.utils import new_request_id

Header = tuple[bytes, bytes]


class RequestContextMiddleware:
    """Middleware that propagates a request id."""

    def __init__(self, app: ASGIApp) -> None:
        """Create middleware for an ASGI application."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Attach request context for HTTP requests."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = self._headers(scope)
        request_id = headers.get(REQUEST_ID_HEADER.lower(), new_request_id())
        token = set_request_id(request_id)
        try:
            self._record_request(scope)
            await self.app(scope, receive, self._send_with_request_id(send, request_id))
        finally:
            clear_request_id(token)

    def _send_with_request_id(
        self,
        send: Send,
        request_id: str,
    ) -> Callable[[Message], Awaitable[None]]:
        """Return a send wrapper that adds the request id header."""

        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER.encode(), request_id.encode()))
                message["headers"] = headers
            await send(message)

        return wrapped_send

    def _headers(self, scope: Scope) -> dict[str, str]:
        """Return request headers as lower-case strings."""
        raw_headers = scope.get("headers", [])
        return {key.decode().lower(): value.decode() for key, value in raw_headers}

    def _record_request(self, scope: MutableMapping[str, object]) -> None:
        """Increment request metrics when a container is attached."""
        app = scope.get("app")
        state = getattr(app, "state", None)
        container = getattr(state, "container", None)
        if isinstance(container, ServiceContainer):
            container.metrics.record_request()
