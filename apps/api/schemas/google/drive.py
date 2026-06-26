"""Drive API schemas.

Purpose: validate Drive requests and document file contracts.
Responsibilities: model upload and search inputs.
Dependencies: Pydantic v2.
Extension Notes: replace content strings with multipart uploads for large files.
"""

from pydantic import BaseModel, EmailStr, Field


class DriveUploadRequest(BaseModel):
    """Drive upload request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    name: str = Field(..., min_length=1, examples=["notes.txt"])
    content: str = Field("", description="Text content for small uploads.")
    folder: bool = Field(False, description="Create a folder instead of a file.")
    parent_folder: str | None = Field(None, examples=["drive-folder-id"])
    mime_type: str = Field("text/plain", examples=["text/plain"])
    rename: str | None = Field(None, examples=["AI Notes.txt"])
    description: str | None = Field(None, examples=["AI Agent notes"])

    def metadata(self) -> dict[str, object]:
        """Return Google Drive metadata."""
        mime = "application/vnd.google-apps.folder" if self.folder else self.mime_type
        body: dict[str, object] = {"name": self.rename or self.name, "mimeType": mime}
        if self.parent_folder:
            body["parents"] = [self.parent_folder]
        if self.description:
            body["description"] = self.description
        return body


class DriveSearchQuery(BaseModel):
    """Drive search filters."""

    name: str | None = None
    mime_type: str | None = None
    folder: str | None = None
    owner: str | None = None

    def to_query(self) -> str:
        """Return a Drive search query."""
        parts = []
        if self.name:
            parts.append(f"name contains '{self.name}'")
        if self.mime_type:
            parts.append(f"mimeType = '{self.mime_type}'")
        if self.folder:
            parts.append(f"'{self.folder}' in parents")
        if self.owner:
            parts.append(f"'{self.owner}' in owners")
        return " and ".join(parts)
