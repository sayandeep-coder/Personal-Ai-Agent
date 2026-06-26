"""Authentication DTOs.

Purpose: define service-level authentication results.
Responsibilities: keep API and CLI independent from ORM models.
Dependencies: dataclasses.
Extension Notes: add fields only when exposed by use cases.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LoginResult:
    """OAuth login URL and state result."""

    authorization_url: str
    state: str


@dataclass(frozen=True)
class AuthResult:
    """Successful authentication result."""

    user_id: UUID
    integration_id: UUID
    email: str
    connected: bool


@dataclass(frozen=True)
class AuthStatus:
    """Authentication status result."""

    authenticated: bool
    connected_services: tuple[str, ...]
    google_email: str | None
    connection_status: str | None
    last_login: str | None = None

