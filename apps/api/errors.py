"""API exception handlers.

Purpose: convert internal exceptions into stable JSON error contracts.
Responsibilities: map known exceptions and hide unexpected stack traces.
Dependencies: FastAPI, application exceptions, and response helpers.
Extension Notes: add provider-specific HTTP status mapping as policies mature.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from apps.api.responses import error
from core.exceptions import ApplicationException
from core.logging import get_logger

logger = get_logger(__name__)

_GOOGLE_CODES = frozenset({
    "google.api_error",
    "google.missing_scope",
    "google.token_missing",
    "google.refresh_missing",
    "google.refresh_failed",
    "google.not_connected",
    "google.user_missing",
    "google.unavailable",
})

_GITHUB_403_CODES = frozenset({
    "github.private_repository",
    "drive.invalid_share_role",
})

_GITHUB_401_CODES = frozenset({
    "github.token_not_configured",
})

_WEATHER_CODES = frozenset({
    "weather.invalid_request",
    "weather.invalid_key",
    "weather.not_found",
    "weather.rate_limited",
    "weather.unavailable",
    "weather.timeout",
    "weather.provider_error",
})


def register_error_handlers(app: FastAPI) -> None:
    """Register production API error handlers."""

    @app.exception_handler(ApplicationException)
    async def application_error(_: Request, exc: ApplicationException) -> JSONResponse:
        logger.warning(
            "application_error",
            code=exc.code,
            reason=exc.message,
            details=exc.details,
        )
        code = exc.code.upper().replace(".", "_")

        if exc.code in _GOOGLE_CODES and exc.details:
            body: dict[str, object] = {
                "success": False,
                "error": {
                    "code": code,
                    "message": exc.message,
                    **{k: v for k, v in exc.details.items()},
                },
            }
            return JSONResponse(body, _google_http_status(exc))

        if exc.code in _GITHUB_403_CODES:
            return JSONResponse(error(code, exc.message), status.HTTP_403_FORBIDDEN)

        if exc.code in _GITHUB_401_CODES:
            return JSONResponse(error(code, exc.message), status.HTTP_401_UNAUTHORIZED)

        if exc.code in _WEATHER_CODES:
            return JSONResponse(error(code, exc.message), _detail_status(exc, status.HTTP_400_BAD_REQUEST))

        if exc.code == "github.api_error":
            github_status = exc.details.get("github_status") if exc.details else None
            http_status = _github_http_status(int(github_status)) if isinstance(github_status, int) else status.HTTP_400_BAD_REQUEST
            return JSONResponse(error(code, exc.message), http_status)

        return JSONResponse(error(code, exc.message), status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unexpected_api_error", error=str(exc))
        return JSONResponse(
            error("INTERNAL_SERVER_ERROR", "An unexpected server error occurred."),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _github_http_status(github_status: int) -> int:
    """Map a GitHub API HTTP status to the appropriate response status."""
    if github_status == 401:
        return status.HTTP_401_UNAUTHORIZED
    if github_status == 403:
        return status.HTTP_403_FORBIDDEN
    if github_status == 404:
        return status.HTTP_404_NOT_FOUND
    if github_status == 429:
        return status.HTTP_429_TOO_MANY_REQUESTS
    if github_status == 503:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_400_BAD_REQUEST


def _detail_status(exc: ApplicationException, default: int) -> int:
    """Return HTTP status from exception details."""
    value = exc.details.get("status_code") if exc.details else None
    return value if isinstance(value, int) else default


def _google_http_status(exc: ApplicationException) -> int:
    """Map Google error details to an appropriate HTTP response status."""
    google_status = exc.details.get("google_status")
    if isinstance(google_status, int):
        if google_status == 401:
            return status.HTTP_401_UNAUTHORIZED
        if google_status == 403:
            return status.HTTP_403_FORBIDDEN
        if google_status == 429:
            return status.HTTP_429_TOO_MANY_REQUESTS
    if exc.code in {"google.missing_scope", "google.not_connected"}:
        return status.HTTP_403_FORBIDDEN
    if exc.code in {"google.token_missing", "google.refresh_missing", "google.refresh_failed"}:
        return status.HTTP_401_UNAUTHORIZED
    return status.HTTP_400_BAD_REQUEST
