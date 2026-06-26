"""GitHub REST API HTTP client.

Purpose: execute authorized read-only GitHub API requests.
Responsibilities: attach Bearer token, parse JSON, surface structured errors.
Dependencies: urllib standard library only.

Security invariants enforced here:
  - The PAT is NEVER logged, traced, or included in error messages.
  - The Authorization header is constructed at call time inside _request() and
    is NOT stored in any instance attribute that could appear in a log record.
  - _logger.warning() is used everywhere (NOT .exception() / .error()) to
    suppress Loguru's rich traceback, which would print every local variable
    including the Authorization header value.
  - Error details come from the GitHub response body only.
"""

import json
import ssl
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from core.exceptions import ValidationException
from core.logging import get_logger

JsonDict = dict[str, object]

_BASE = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"
_TIMEOUT = 20

_logger = get_logger(__name__)

# Python 3.11 framework builds on macOS ship with an empty cert.pem.
# certifi provides the Mozilla CA bundle so TLS verification works out of the box.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class GitHubApiClient:
    """urllib-backed read-only GitHub REST API client.

    The PAT is accepted at construction and stored only as a private attribute.
    It is scrubbed from every log record and exception message — .warning() is
    used throughout so Loguru never captures a rich traceback that would print
    the Authorization header value.
    """

    def __init__(self, token: str) -> None:
        """Initialise with a Personal Access Token."""
        self._token = token

    def get(self, path: str, params: JsonDict | None = None) -> JsonDict:
        """Execute an authorized GET and return a JSON object."""
        result = self._request(path, params)
        if isinstance(result, dict):
            return result
        raise ValidationException(
            f"GitHub returned a list where an object was expected for {path}",
            code="github.unexpected_response_shape",
        )

    def get_list(self, path: str, params: JsonDict | None = None) -> list[JsonDict]:
        """Execute an authorized GET and return a JSON array."""
        result = self._request(path, params)
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        raise ValidationException(
            f"GitHub returned an object where a list was expected for {path}",
            code="github.unexpected_response_shape",
        )

    # ── internal ──────────────────────────────────────────────────────────────

    def _request(self, path: str, params: JsonDict | None = None) -> object:
        # Strip whitespace from every segment so a username like "octocat "
        # never produces a URL with an embedded space, which http.client rejects.
        clean_path = "/".join(seg.strip() for seg in path.split("/"))
        query = f"?{urlencode({k: v for k, v in (params or {}).items() if v is not None})}"
        url = f"{_BASE}{clean_path}{query if params else ''}"
        request = Request(
            url,
            method="GET",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": _ACCEPT,
                "X-GitHub-Api-Version": _API_VERSION,
                "User-Agent": "PersonalAIAgent/1.0",
            },
        )
        body = ""
        try:
            with urlopen(request, timeout=_TIMEOUT, context=_SSL_CONTEXT) as response:
                body = response.read().decode("utf-8")
                rate_remaining = response.headers.get("X-RateLimit-Remaining", "?")
                _logger.warning(
                    "github_api_request",
                    path=clean_path,
                    status=response.status,
                    rate_remaining=rate_remaining,
                )
        except HTTPError as exc:
            _handle_github_error(exc, clean_path)
        except Exception as exc:
            # Catches URLError (network), InvalidURL (bad chars), and anything
            # else from urllib/http.client.
            # .warning() — NOT .exception() — so Loguru never emits a rich
            # traceback that would expose the Authorization header from the
            # 'request' local variable above.
            _logger.warning(
                "github_api_error",
                path=clean_path,
                reason=str(exc),
            )
            raise ValidationException(
                "GitHub request failed. Check network connectivity or input values.",
                code="github.unavailable",
            ) from exc
        return json.loads(body) if body else {}


def _handle_github_error(exc: HTTPError, path: str) -> None:
    """Parse GitHub error body and raise a ValidationException.

    Uses .warning() — NOT .exception() — so Loguru does NOT emit a rich
    traceback that would expose the Authorization header from the caller's
    frame.  Only the path, HTTP status, and GitHub's own error message are
    recorded.
    """
    status = exc.code
    message = ""
    documentation_url = ""

    try:
        raw_body = exc.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw_body) if raw_body else {}
        message = str(parsed.get("message", ""))
        documentation_url = str(parsed.get("documentation_url", ""))
    except Exception:
        pass

    _logger.warning(
        "github_api_http_error",
        path=path,
        github_status=status,
        github_message=message,
        documentation_url=documentation_url,
    )

    if status == 401:
        human = "GitHub token is invalid or expired. Rotate GITHUB_TOKEN."
    elif status == 403:
        human = f"GitHub access forbidden: {message or 'rate limit or permission error'}."
    elif status == 404:
        human = f"GitHub resource not found: {path}."
    elif status == 422:
        human = f"GitHub rejected the request: {message}."
    elif status == 429:
        human = "GitHub rate limit exceeded. Retry after the X-RateLimit-Reset window."
    elif status == 503:
        human = "GitHub is temporarily unavailable."
    else:
        human = f"GitHub API error {status}: {message or 'unknown error'}."

    raise ValidationException(
        human,
        code="github.api_error",
        details={
            "github_status": status,
            "github_message": message,
            "path": path,
        },
    ) from exc
