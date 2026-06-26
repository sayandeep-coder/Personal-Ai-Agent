"""Gmail API schemas.

Purpose: define validated Gmail request and response contracts.
Responsibilities: model search filters, messages, labels, and envelopes.
Dependencies: Pydantic v2.
Extension Notes: add attachment download schemas when binary APIs are added.
"""

from datetime import date

from pydantic import BaseModel, EmailStr, Field


class GmailSearchQuery(BaseModel):
    """Structured Gmail search filters."""

    subject: str | None = Field(None, examples=["Invoice"])
    sender: str | None = Field(None, examples=["a@gmail.com"])
    to: str | None = Field(None, examples=["b@gmail.com"])
    label: str | None = Field(None, examples=["INBOX"])
    after: date | None = Field(None, examples=["2026-06-01"])
    before: date | None = Field(None, examples=["2026-07-01"])
    has_attachment: bool = False
    unread: bool = False

    def to_query(self) -> str:
        """Return a Gmail search query string."""
        parts = []
        if self.subject:
            parts.append(f"subject:{self.subject}")
        if self.sender:
            parts.append(f"from:{self.sender}")
        if self.to:
            parts.append(f"to:{self.to}")
        if self.label:
            parts.append(f"label:{self.label}")
        if self.after:
            parts.append(f"after:{self.after.isoformat()}")
        if self.before:
            parts.append(f"before:{self.before.isoformat()}")
        if self.has_attachment:
            parts.append("has:attachment")
        if self.unread:
            parts.append("is:unread")
        return " ".join(parts)


class GmailListItem(BaseModel):
    """Normalized Gmail list item."""

    id: str
    thread_id: str
    subject: str | None = None
    from_: str | None = Field(None, alias="from")
    to: str | None = None
    date: str | None = None
    labels: list[str] = []
    snippet: str = ""
    unread: bool = False
    has_attachments: bool = False


class GmailAttachment(BaseModel):
    """Normalized Gmail attachment metadata."""

    filename: str
    mime_type: str
    size: int
    attachment_id: object | None = None


class GmailMessage(GmailListItem):
    """Normalized decoded Gmail message."""

    cc: str | None = None
    bcc: str | None = None
    body_text: str = ""
    body_html: str = ""
    attachments: list[GmailAttachment] = []


class GmailLabel(BaseModel):
    """Simplified Gmail label."""

    id: str
    name: str
    type: str = ""


class GmailAttachmentInput(BaseModel):
    """Attachment to include in an outbound email."""

    filename: str = Field(..., min_length=1, examples=["report.pdf"])
    mime_type: str = Field(..., min_length=1, examples=["application/pdf"])
    content_base64: str = Field(..., min_length=1, description="Base64-encoded file content")


class GmailSendRequest(BaseModel):
    """Send email request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    to: list[EmailStr] = Field(..., min_length=1, examples=[["friend@example.com"]])
    cc: list[EmailStr] = Field(default_factory=list, examples=[["cc@example.com"]])
    bcc: list[EmailStr] = Field(default_factory=list, examples=[["bcc@example.com"]])
    subject: str = Field(..., min_length=1, examples=["Project update"])
    body_text: str = Field("", examples=["Hello from Personal AI Agent"])
    body_html: str | None = Field(None, examples=["<p>Hello from <b>Personal AI Agent</b></p>"])
    attachments: list[GmailAttachmentInput] = Field(default_factory=list)
