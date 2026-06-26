"""Google OAuth client.

Purpose: perform Google OAuth provider operations.
Responsibilities: build auth URLs and call token/profile/revoke endpoints.
Dependencies: urllib, settings, and Google OAuth value objects.
Extension Notes: replace transport with injected HTTP client if needed.
"""

from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import Request

from core.config import Settings
from core.utils import utc_now
from integrations.google.auth.constants import AUTH_URL, PROFILE_URL, REVOKE_URL, TOKEN_URL
from integrations.google.auth.scopes import GOOGLE_OAUTH_SCOPES
from integrations.google.auth.transport import read_json, send
from integrations.google.auth.types import GoogleProfile, GoogleTokenSet
from integrations.google.common.ssl import google_ssl_context


class GoogleOAuthClient:
    """HTTP implementation of Google OAuth provider operations."""

    def __init__(self, settings: Settings) -> None:
        """Create a Google OAuth client from settings."""
        self._settings = settings
        self._ssl_context = google_ssl_context()

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        """Return a Google authorization URL."""
        params = {
            "client_id": self._settings.google_client_id or "",
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_OAUTH_SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str) -> GoogleTokenSet:
        """Exchange an authorization code for tokens."""
        payload = {
            "code": code,
            "client_id": self._settings.google_client_id,
            "client_secret": self._secret(),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        return self._token_request(payload)

    def refresh_token(self, refresh_token: str) -> GoogleTokenSet:
        """Refresh an access token."""
        payload = {
            "refresh_token": refresh_token,
            "client_id": self._settings.google_client_id,
            "client_secret": self._secret(),
            "grant_type": "refresh_token",
        }
        return self._token_request(payload)

    def profile(self, access_token: str) -> GoogleProfile:
        """Return the Google profile for an access token."""
        request = Request(PROFILE_URL, headers={"Authorization": f"Bearer {access_token}"})
        data = read_json(request, self._ssl_context, "google.profile", "Google profile request failed")
        return GoogleProfile(
            email=str(data["email"]),
            full_name=str(data.get("name") or data["email"]),
            email_verified=bool(data.get("email_verified", False)),
        )

    def revoke(self, token: str) -> None:
        """Revoke a Google OAuth token."""
        data = urlencode({"token": token}).encode()
        request = Request(REVOKE_URL, data=data, method="POST")
        send(request, self._ssl_context, "google.revoke", "Google token revoke failed")

    def _token_request(self, payload: dict[str, str | None]) -> GoogleTokenSet:
        """Execute a token endpoint request."""
        data = urlencode({key: value or "" for key, value in payload.items()}).encode()
        request = Request(TOKEN_URL, data=data, method="POST")
        body = read_json(request, self._ssl_context, "google.token", "Google token exchange failed")
        raw_expires = body.get("expires_in", 0)
        expires_in = int(raw_expires) if isinstance(raw_expires, int | str) else 0
        expires_at = utc_now() + timedelta(seconds=expires_in) if expires_in else None
        refresh_token = body.get("refresh_token")
        return GoogleTokenSet(
            access_token=str(body["access_token"]),
            refresh_token=str(refresh_token) if refresh_token else None,
            token_type=str(body.get("token_type", "Bearer")),
            scope=str(body.get("scope", "")),
            expires_at=expires_at,
        )

    def _secret(self) -> str:
        """Return the configured Google client secret."""
        secret = self._settings.google_client_secret
        return secret.get_secret_value() if secret else ""
