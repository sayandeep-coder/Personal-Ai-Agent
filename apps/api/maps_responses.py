"""Google Maps response envelopes.

Purpose: enforce the Maps-specific API response schema.
Responsibilities: build success and error envelopes with metadata.
Dependencies: FastAPI responses and request context.
Extension Notes: add cache metadata here when Maps caching lands.
"""

from time import perf_counter

from fastapi.responses import JSONResponse

from core.context.request import get_request_id
from core.exceptions import ApplicationException
from services.maps.types import MapsResult


def ok(result: MapsResult, started: float) -> JSONResponse:
    """Return Maps success envelope."""
    return JSONResponse({
        "success": True,
        "data": result.data,
        "error": None,
        "meta": _meta(started, result.pagination),
        "request_id": get_request_id(),
    })


def fail(exc: ApplicationException, started: float) -> JSONResponse:
    """Return Maps error envelope."""
    return JSONResponse(
        {
            "success": False,
            "data": None,
            "error": {"code": _code(exc.code), "message": exc.message, "details": exc.details},
            "meta": _meta(started, None),
            "request_id": get_request_id(),
        },
        status_code=_status(exc),
    )


def _meta(started: float, pagination: dict[str, object] | None) -> dict[str, object]:
    """Return Maps metadata."""
    return {"provider": "google_maps", "cached": False, "response_time_ms": round((perf_counter() - started) * 1000), "pagination": pagination or {"next_page_token": None, "total_results": 0}}


def _code(code: str) -> str:
    """Return public Maps error code."""
    return code.removeprefix("maps.").upper()


def _status(exc: ApplicationException) -> int:
    """Return HTTP status for exception."""
    value = exc.details.get("status_code") if exc.details else None
    return value if isinstance(value, int) else 500
