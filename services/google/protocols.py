"""Google service protocols.

Purpose: define shared service-layer contracts.
Responsibilities: keep Google wrappers decoupled from credential implementation.
Dependencies: typing protocols.
Extension Notes: add quota or tenant protocols when needed.
"""

from typing import Protocol


class AccessTokenProvider(Protocol):
    """Protocol for resolving Google access tokens."""

    def access_token(self, email: str, required_scopes: list[str] | None = None) -> str:
        """Return access token for a user email, optionally verifying required scopes."""
        ...

