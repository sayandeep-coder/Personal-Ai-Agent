"""Google auth API schemas.

Purpose: define request and response schemas for Google OAuth routes.
Responsibilities: validate user-facing auth payloads.
Dependencies: Pydantic v2.
Extension Notes: never add token fields to response schemas.
"""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class AuthActionRequest(BaseModel):
    """Request body for user-scoped auth actions."""

    email: EmailStr


class AuthResultResponse(BaseModel):
    """Authentication success response."""

    user_id: UUID
    integration_id: UUID
    email: EmailStr
    connected: bool


class AuthStatusResponse(BaseModel):
    """Authentication status response."""

    authenticated: bool
    connected_services: tuple[str, ...] = Field(default_factory=tuple)
    google_email: EmailStr | None
    connection_status: str | None
    last_login: str | None = None

