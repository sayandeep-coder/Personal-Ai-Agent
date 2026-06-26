"""Google API common schemas.

Purpose: define reusable request schemas for Google routes.
Responsibilities: validate email and generic payloads.
Dependencies: Pydantic v2.
Extension Notes: add stricter provider-specific schemas over time.
"""

from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    """Request body containing a user email."""

    email: EmailStr


class JsonPayload(BaseModel):
    """Generic JSON payload request."""

    email: EmailStr
    payload: dict[str, object]


class TextPayload(BaseModel):
    """Text payload request."""

    email: EmailStr
    text: str

