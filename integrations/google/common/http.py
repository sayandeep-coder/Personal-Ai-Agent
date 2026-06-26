"""Google REST HTTP client.

Purpose: provide authorized Google API HTTP operations.
Responsibilities: encode requests, parse JSON responses, expose typed protocol.
Dependencies: urllib and JSON standard library modules.
Extension Notes: inject retries/rate limits here without changing services.
"""

import json
import traceback
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from core.exceptions import ValidationException
from core.logging import get_logger
from integrations.google.common.ssl import google_ssl_context

JsonDict = dict[str, object]

_logger = get_logger(__name__)

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


class GoogleApiPort(Protocol):
    """Protocol for authorized Google API calls."""

    def get(self, url: str, token: str, params: JsonDict | None = None) -> JsonDict:
        """Execute an authorized GET request."""
        ...

    def get_raw(self, url: str, token: str, params: JsonDict | None = None) -> tuple[bytes, str]:
        """Execute an authorized GET and return (raw_bytes, content_type)."""
        ...

    def post(self, url: str, token: str, payload: JsonDict | None = None) -> JsonDict:
        """Execute an authorized POST request."""
        ...

    def patch(self, url: str, token: str, payload: JsonDict) -> JsonDict:
        """Execute an authorized PATCH request."""
        ...

    def delete(self, url: str, token: str) -> JsonDict:
        """Execute an authorized DELETE request."""
        ...


class GoogleApiClient:
    """urllib-backed authorized Google API client."""

    def __init__(self) -> None:
        """Create the API client with a stable Google TLS context."""
        self._ssl_context = google_ssl_context()

    def get(self, url: str, token: str, params: JsonDict | None = None) -> JsonDict:
        """Execute an authorized GET request."""
        query = f"?{urlencode(params or {})}" if params else ""
        return self._request("GET", f"{url}{query}", token)

    def get_raw(self, url: str, token: str, params: JsonDict | None = None) -> tuple[bytes, str]:
        """Execute an authorized GET and return (raw_bytes, content_type).

        Used for binary exports (PDF, DOCX, XLSX, etc.) where the response
        body must not be decoded as JSON or UTF-8 text.
        """
        query = f"?{urlencode(params or {})}" if params else ""
        full_url = f"{url}{query}"
        request = Request(
            full_url,
            method="GET",
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            with urlopen(request, timeout=60, context=self._ssl_context) as response:
                raw = response.read()
                content_type = response.headers.get("Content-Type", "application/octet-stream")
        except HTTPError as exc:
            _handle_google_http_error(exc, "GET", full_url)
        except URLError as exc:
            _logger.exception(
                "google_api_network_error",
                method="GET",
                url=full_url,
                reason=str(exc.reason),
                traceback=traceback.format_exc(),
            )
            raise ValidationException(
                f"Google API is unreachable: {exc.reason}",
                code="google.unavailable",
            ) from exc
        return raw, content_type

    def post(self, url: str, token: str, payload: JsonDict | None = None) -> JsonDict:
        """Execute an authorized POST request."""
        return self._request("POST", url, token, payload)

    def patch(self, url: str, token: str, payload: JsonDict) -> JsonDict:
        """Execute an authorized PATCH request."""
        return self._request("PATCH", url, token, payload)

    def delete(self, url: str, token: str) -> JsonDict:
        """Execute an authorized DELETE request."""
        return self._request("DELETE", url, token)

    def _request(
        self,
        method: str,
        url: str,
        token: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        """Execute a Google API request."""
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30, context=self._ssl_context) as response:
                body = response.read().decode()
        except HTTPError as exc:
            _handle_google_http_error(exc, method, url)
        except URLError as exc:
            _logger.exception(
                "google_api_network_error",
                method=method,
                url=url,
                reason=str(exc.reason),
                traceback=traceback.format_exc(),
            )
            raise ValidationException(
                f"Google API is unreachable: {exc.reason}",
                code="google.unavailable",
            ) from exc
        return json.loads(body) if body else {}


def _handle_google_http_error(exc: HTTPError, method: str, url: str) -> None:
    """Parse the Google HTTPError response body and raise a detailed exception."""
    google_status = exc.code
    google_reason = exc.reason or "unknown"
    raw_body = ""
    error_code = ""
    error_message = ""

    try:
        raw_body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        raw_body = "<unreadable>"

    parsed: JsonDict = {}
    try:
        parsed = json.loads(raw_body) if raw_body else {}
    except Exception:
        pass

    error_block = parsed.get("error", {})
    if isinstance(error_block, dict):
        error_code = str(error_block.get("status", error_block.get("code", "")))
        error_message = str(error_block.get("message", ""))
        errors_list = error_block.get("errors", [])
        if isinstance(errors_list, list) and errors_list:
            first = errors_list[0]
            if isinstance(first, dict):
                error_code = str(first.get("reason", error_code))
                error_message = str(first.get("message", error_message))

    _logger.exception(
        "google_api_http_error",
        method=method,
        url=url,
        google_status=google_status,
        google_reason=google_reason,
        google_error_code=error_code,
        google_error_message=error_message,
        google_response_body=raw_body,
        traceback=traceback.format_exc(),
    )

    human_reason = error_message or google_reason
    if google_status == 401:
        human_reason = "OAuth token is invalid or has been revoked."
    elif google_status == 403 and "insufficientPermissions" in (error_code + raw_body):
        human_reason = (
            f"Insufficient OAuth permissions. "
            f"Ensure the {GMAIL_SEND_SCOPE} scope was granted. "
            f"Google said: {error_message or google_reason}"
        )
    elif google_status == 403:
        human_reason = f"Access forbidden. Google said: {error_message or google_reason}"
    elif google_status == 400:
        human_reason = f"Bad request. Google said: {error_message or google_reason}"
    elif google_status == 429:
        human_reason = "Google API rate limit exceeded. Try again later."

    raise ValidationException(
        human_reason,
        code="google.api_error",
        details={
            "provider": "gmail",
            "google_status": google_status,
            "google_reason": error_code or google_reason,
            "google_message": error_message,
            "google_response_body": raw_body,
        },
    ) from exc
