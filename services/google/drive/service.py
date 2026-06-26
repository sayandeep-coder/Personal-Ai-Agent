"""Google Drive service wrapper.

Purpose: provide Drive API operations.
Responsibilities: list/search files, upload/download/delete/move, metadata.
Dependencies: Google credentials and REST client protocol.
Extension Notes: binary streaming can be added behind the same service.
"""

from integrations.google.common.http import GoogleApiPort, JsonDict
from services.google.drive.normalizer import file_item, file_page
from services.google.protocols import AccessTokenProvider

BASE = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3"


class DriveService:
    """Service wrapper for Google Drive APIs."""

    def __init__(self, credentials: AccessTokenProvider, client: GoogleApiPort) -> None:
        """Create a Drive service."""
        self._credentials = credentials
        self._client = client

    def list_files(self, email: str, page_token: str | None = None) -> JsonDict:
        """List normalized files with pagination."""
        fields = "nextPageToken,files(id,name,mimeType,size,owners,createdTime,modifiedTime,"
        params: JsonDict = {"fields": fields + "webContentLink,thumbnailLink)"}
        if page_token:
            params["pageToken"] = page_token
        return file_page(self._client.get(f"{BASE}/files", self._token(email), params))

    def search_files(self, email: str, query: str) -> JsonDict:
        """Search normalized Drive files."""
        return file_page(self._client.get(f"{BASE}/files", self._token(email), {"q": query}))

    def file_details(self, email: str, file_id: str) -> JsonDict:
        """Return normalized file metadata."""
        payload = self._client.get(f"{BASE}/files/{file_id}", self._token(email), {"fields": "*"})
        return file_item(payload)

    def download(self, email: str, file_id: str) -> tuple[bytes, str, str]:
        """Download a Drive file and return (raw_bytes, content_type, filename).

        Fetches the filename first via a metadata call, then streams the binary
        content using alt=media. Google Workspace native files (Docs, Sheets, Slides)
        cannot be downloaded this way — use export_document / export_spreadsheet instead.
        """
        meta = self._client.get(
            f"{BASE}/files/{file_id}",
            self._token(email),
            {"fields": "name,mimeType"},
        )
        filename = str(meta.get("name", file_id))
        raw, content_type = self._client.get_raw(
            f"{BASE}/files/{file_id}",
            self._token(email),
            {"alt": "media"},
        )
        return raw, content_type or str(meta.get("mimeType", "application/octet-stream")), filename

    def upload(self, email: str, metadata: JsonDict, content: str = "") -> JsonDict:
        """Upload a small file or create a folder."""
        payload: JsonDict = {"metadata": metadata, "content": content}
        result = self._client.post(f"{UPLOAD}/files?uploadType=multipart", self._token(email), payload)
        return file_item(result)

    def delete(self, email: str, file_id: str) -> JsonDict:
        """Delete a Drive file."""
        self._client.delete(f"{BASE}/files/{file_id}", self._token(email))
        return {"deleted": True, "id": file_id}

    def move(self, email: str, file_id: str, folder_id: str) -> JsonDict:
        """Move a file to a folder."""
        return self._client.patch(
            f"{BASE}/files/{file_id}",
            self._token(email),
            {"addParents": folder_id},
        )

    def folder_listing(self, email: str, folder_id: str) -> JsonDict:
        """List files in a folder."""
        return self.search_files(email, f"'{folder_id}' in parents")

    def share_file(self, email: str, file_id: str, target_email: str, role: str = "reader") -> JsonDict:
        """Grant a Drive permission on file_id to target_email.

        role must be one of: writer, commenter, reader.
        'owner' and 'organizer' are rejected — ownership transfer is a
        destructive operation that requires explicit user intent.
        sendNotificationEmail=false suppresses the Google share notification email.
        """
        _ALLOWED_ROLES = {"writer", "commenter", "reader"}
        if role not in _ALLOWED_ROLES:
            from core.exceptions import ValidationException
            raise ValidationException(
                f"Share role {role!r} is not allowed. "
                f"Use one of: {', '.join(sorted(_ALLOWED_ROLES))}. "
                "Ownership transfer ('owner') requires explicit Drive API parameters and is not supported here.",
                code="drive.invalid_share_role",
            )
        url = f"{BASE}/files/{file_id}/permissions?sendNotificationEmail=false"
        payload: JsonDict = {"type": "user", "role": role, "emailAddress": target_email}
        result = self._client.post(url, self._token(email), payload)
        return {
            "shared": True,
            "file_id": file_id,
            "target_email": target_email,
            "role": role,
            "permission_id": result.get("id", ""),
        }

    def _token(self, email: str) -> str:
        """Return access token for user email."""
        return self._credentials.access_token(email)
