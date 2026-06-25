"""Request context management.

Purpose: store correlation data for the current execution context.
Responsibilities: manage request identifiers for logs and responses.
Dependencies: contextvars.
Extension Notes: keep context values serializable and non-sensitive.
"""

from contextvars import ContextVar, Token

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> Token[str | None]:
    """Set the request id for the current execution context."""
    return _request_id.set(request_id)


def get_request_id() -> str | None:
    """Return the request id for the current execution context."""
    return _request_id.get()


def clear_request_id(token: Token[str | None]) -> None:
    """Restore the previous request id context value."""
    _request_id.reset(token)

