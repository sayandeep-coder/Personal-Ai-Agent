"""API middleware.

Purpose: provide request context for HTTP requests.
Responsibilities: attach correlation identifiers to logs and responses.
Dependencies: FastAPI/Starlette request handling and core context.
Extension Notes: add auth and telemetry middleware as separate classes.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.constants import REQUEST_ID_HEADER
from core.context import clear_request_id, set_request_id
from core.container import ServiceContainer
from core.utils import new_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware that propagates a request id."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Attach request id context for the duration of a request."""
        request_id = request.headers.get(REQUEST_ID_HEADER, new_request_id())
        token = set_request_id(request_id)
        try:
            container: ServiceContainer = request.app.state.container
            container.metrics.record_request()
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_id(token)
