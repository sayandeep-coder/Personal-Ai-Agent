"""Google OAuth scopes.

Purpose: centralize scopes requested during Google login.
Responsibilities: avoid duplicated OAuth scope strings.
Dependencies: none.
Extension Notes: add scopes only when a milestone needs them.
"""

GOOGLE_OAUTH_SCOPES = (
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
)
