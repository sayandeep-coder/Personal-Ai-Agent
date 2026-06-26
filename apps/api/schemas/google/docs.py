"""Docs API schemas.

Purpose: validate document creation and editing requests.
Responsibilities: model create and patch operations.
Dependencies: Pydantic v2.
Extension Notes: add collaborative comment operations later.
"""

from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator

_ALLOWED_SHARE_ROLES = {"writer", "commenter", "reader"}


class DocsOperation(StrEnum):
    """Supported document patch operations."""

    APPEND = "append"
    REPLACE = "replace"
    INSERT = "insert"
    DELETE = "delete"
    BATCH = "batch"


class DocShareEntry(BaseModel):
    """A single sharing permission entry for a document."""

    email: EmailStr
    role: str = Field("reader", examples=["writer", "reader", "commenter"])

    @field_validator("role")
    @classmethod
    def role_must_be_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_SHARE_ROLES:
            raise ValueError(f"role {v!r} is not allowed; use one of: {', '.join(sorted(_ALLOWED_SHARE_ROLES))}")
        return v


class DocPermissions(BaseModel):
    """Fine-grained permission flags (informational — stored in metadata only)."""

    discoverable: bool = False
    copy_allowed: bool = True
    download_allowed: bool = True
    print_allowed: bool = True


class DocMetadata(BaseModel):
    """Arbitrary key/value metadata to embed in the document body."""

    project: str | None = None
    version: str | None = None
    author: str | None = None
    department: str | None = None
    classification: str | None = None


class CreateDocumentRequest(BaseModel):
    """Create document request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    title: str = Field(..., examples=["AI Notes"])
    content: str = Field("", examples=["Full markdown or plain text"])
    folder_id: str | None = Field(None, examples=["drive-folder-id"])

    # Formatting & structure flags
    document_type: str = Field("general", examples=["technical_document", "report", "notes"])
    format: str = Field("plain", examples=["markdown", "plain"])
    locale: str = Field("en-US", examples=["en-IN", "en-US"])
    timezone: str = Field("UTC", examples=["Asia/Kolkata"])
    tags: list[str] = Field(default_factory=list, examples=[["architecture", "backend"]])

    create_table_of_contents: bool = Field(False, description="Prepend a Table of Contents section")
    page_break_between_sections: bool = Field(False, description="Insert page breaks between Markdown headings")
    generate_title_page: bool = Field(False, description="Prepend a formatted title page")

    add_header: bool = Field(False, description="Prepend a header line to the body")
    header_text: str = Field("", examples=["Personal AI Agent Architecture"])
    add_footer: bool = Field(False, description="Append a footer line to the body")
    footer_text: str = Field("", examples=["Confidential • Version 1.0"])

    # Sharing
    share_with: list[str | DocShareEntry] = Field(default_factory=list)

    # Metadata block
    metadata: DocMetadata | None = None
    permissions: DocPermissions | None = None


class PatchDocumentRequest(BaseModel):
    """Patch document request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    operation: DocsOperation = Field(DocsOperation.APPEND)
    text: str | None = Field(None, examples=["New content"])
    old_text: str | None = Field(None, examples=["old"])
    new_text: str | None = Field(None, examples=["new"])
    index: int = Field(1, ge=1)
    end_index: int | None = Field(None, ge=1)
    requests: list[dict[str, object]] = Field(default_factory=list)

    def to_batch(self) -> dict[str, object]:
        """Return Docs batch update payload."""
        if self.operation == DocsOperation.BATCH:
            return {"requests": self.requests}
        if self.operation == DocsOperation.REPLACE:
            contains = {"text": self.old_text or ""}
            return {"requests": [{"replaceAllText": {"containsText": contains, "replaceText": self.new_text or ""}}]}
        if self.operation == DocsOperation.DELETE:
            return {"requests": [{"deleteContentRange": {"range": {"startIndex": self.index, "endIndex": self.end_index}}}]}
        return {"requests": [{"insertText": {"location": {"index": self.index}, "text": self.text or ""}}]}
