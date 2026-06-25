"""Identifier helpers.

Purpose: generate correlation identifiers.
Responsibilities: provide stable request id creation.
Dependencies: standard library uuid.
Extension Notes: use ULIDs later if sortable ids become useful.
"""

from uuid import uuid4


def new_request_id() -> str:
    """Return a new request correlation identifier."""
    return str(uuid4())

