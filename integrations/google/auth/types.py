"""Google OAuth value objects.

Purpose: define typed data returned by Google auth operations.
Responsibilities: keep provider payloads normalized.
Dependencies: dataclasses.
Extension Notes: extend only for OAuth authentication needs.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GoogleTokenSet:
    """Normalized OAuth token response."""

    access_token: str
    refresh_token: str | None
    token_type: str
    scope: str
    expires_at: datetime | None


@dataclass(frozen=True)
class GoogleProfile:
    """Normalized Google profile response."""

    email: str
    full_name: str
    email_verified: bool

