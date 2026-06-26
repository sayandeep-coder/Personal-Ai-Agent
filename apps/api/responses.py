"""API response envelope helpers.

Purpose: standardize JSON responses across product routes.
Responsibilities: build success and metadata envelopes.
Dependencies: standard library typing only.
Extension Notes: add pagination links here when public clients need them.
"""

from collections.abc import Mapping

from core.context.request import get_request_id


def success(data: object, meta: Mapping[str, object] | None = None) -> dict[str, object]:
    """Return a successful API envelope."""
    return {"success": True, "data": data, "meta": dict(meta or {}), "request_id": get_request_id()}


def error(code: str, message: str) -> dict[str, object]:
    """Return a failed API envelope."""
    return {"success": False, "error": {"code": code, "message": message}, "request_id": get_request_id()}
