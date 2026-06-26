"""Google OAuth endpoint constants.

Purpose: centralize provider endpoint URLs.
Responsibilities: avoid duplicated Google OAuth endpoints.
Dependencies: none.
Extension Notes: change endpoints here for emulator/testing support.
"""

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
PROFILE_URL = "https://openidconnect.googleapis.com/v1/userinfo"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

