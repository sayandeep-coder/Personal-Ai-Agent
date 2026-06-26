"""Google OAuth protocols.

Purpose: define injectable Google OAuth provider contracts.
Responsibilities: decouple auth services from HTTP implementation.
Dependencies: typing protocols and Google OAuth types.
Extension Notes: add narrower protocols if services need less surface area.
"""

from typing import Protocol

from integrations.google.auth.types import GoogleProfile, GoogleTokenSet


class GoogleOAuthPort(Protocol):
    """Protocol for Google OAuth provider operations."""

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        """Return a Google authorization URL."""
        ...

    def exchange_code(self, code: str, redirect_uri: str) -> GoogleTokenSet:
        """Exchange an authorization code for tokens."""
        ...

    def refresh_token(self, refresh_token: str) -> GoogleTokenSet:
        """Refresh an access token."""
        ...

    def profile(self, access_token: str) -> GoogleProfile:
        """Return the Google profile for an access token."""
        ...

    def revoke(self, token: str) -> None:
        """Revoke a Google OAuth token."""
        ...

