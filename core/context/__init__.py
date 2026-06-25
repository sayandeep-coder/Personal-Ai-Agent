"""Request context package.

Purpose: expose request-scoped context helpers.
Responsibilities: propagate correlation identifiers.
Dependencies: contextvars.
Extension Notes: add tenant/user context only after auth exists.
"""

from core.context.request import clear_request_id, get_request_id, set_request_id

__all__ = ["clear_request_id", "get_request_id", "set_request_id"]

