"""Google OAuth transport helpers.

Purpose: execute HTTPS OAuth requests safely.
Responsibilities: use certifi-backed TLS and map network errors.
Dependencies: urllib and application validation exceptions.
Extension Notes: replace with injected async HTTP transport when needed.
"""

from ssl import SSLContext
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from core.exceptions import ValidationException


def read_json(request: Request, context: SSLContext, code: str, message: str) -> dict[str, object]:
    """Execute an HTTPS request and decode JSON."""
    try:
        with urlopen(request, timeout=10, context=context) as response:
            return dict(json.loads(response.read().decode()))
    except (HTTPError, URLError) as exc:
        raise ValidationException(message, code=code) from exc


def send(request: Request, context: SSLContext, code: str, message: str) -> None:
    """Execute an HTTPS request with no response body."""
    try:
        with urlopen(request, timeout=10, context=context):
            return
    except (HTTPError, URLError) as exc:
        raise ValidationException(message, code=code) from exc
