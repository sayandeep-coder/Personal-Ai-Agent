"""Gmail send payload builder.

Purpose: build RFC 5322 email payloads for Gmail send API.
Responsibilities: validate message fields and base64url encode raw messages.
Dependencies: standard email and base64 libraries.
Extension Notes: add attachments by extending the MIMEMultipart construction here.
"""

import base64
from base64 import urlsafe_b64encode
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

from core.exceptions import ValidationException
from core.logging import get_logger

_logger = get_logger(__name__)


class AttachmentSpec:
    """Descriptor for a single outbound attachment."""

    def __init__(self, filename: str, mime_type: str, content_base64: str) -> None:
        self.filename = filename
        self.mime_type = mime_type
        self.content_base64 = content_base64


def raw_message(
    sender: str,
    recipients: list[str],
    subject: str,
    body_text: str,
    body_html: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[AttachmentSpec] | None = None,
) -> str:
    """Return a Gmail API raw message string (base64url-encoded).

    Uses MIMEMultipart so text/plain and text/html are always present when
    body_html is supplied, which is what Gmail expects for rich messages.
    Attachments are encoded with base64 and appended as MIME parts.
    """
    _validate_fields(sender, recipients, subject)

    if attachments:
        root = MIMEMultipart("mixed")
        _set_headers(root, sender, recipients, subject, cc, bcc)
        body_part = _build_body_part(body_text, body_html)
        root.attach(body_part)
        for att in attachments:
            root.attach(_build_attachment_part(att))
        raw = root.as_bytes()
    elif body_html:
        root_alt = MIMEMultipart("alternative")
        _set_headers(root_alt, sender, recipients, subject, cc, bcc)
        root_alt.attach(MIMEText(body_text, "plain", "utf-8"))
        root_alt.attach(MIMEText(body_html, "html", "utf-8"))
        raw = root_alt.as_bytes()
    else:
        plain = MIMEText(body_text, "plain", "utf-8")
        _set_headers(plain, sender, recipients, subject, cc, bcc)
        raw = plain.as_bytes()

    encoded = urlsafe_b64encode(raw).decode("ascii")
    _logger.warning(
        "gmail_mime_built",
        sender=sender,
        recipient_count=len(recipients),
        subject=subject,
        has_html=body_html is not None,
        attachment_count=len(attachments or []),
        payload_bytes=len(raw),
    )
    return encoded


# ── helpers ──────────────────────────────────────────────────────────────────


def _validate_fields(sender: str, recipients: list[str], subject: str) -> None:
    if not sender:
        raise ValidationException("Sender email is required.", code="gmail.missing_sender")
    if not recipients:
        raise ValidationException("At least one recipient is required.", code="gmail.missing_recipients")
    if not subject or not subject.strip():
        raise ValidationException("Subject is required.", code="gmail.missing_subject")
    for addr in recipients:
        if "@" not in addr:
            raise ValidationException(
                f"Invalid recipient address: {addr!r}",
                code="gmail.invalid_recipient",
            )


def _set_headers(
    msg: MIMEBase | MIMEMultipart,
    sender: str,
    recipients: list[str],
    subject: str,
    cc: list[str] | None,
    bcc: list[str] | None,
) -> None:
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = str(Header(subject, "utf-8"))
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)


def _build_body_part(body_text: str, body_html: str | None) -> MIMEMultipart:
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        alt.attach(MIMEText(body_html, "html", "utf-8"))
    return alt


def _build_attachment_part(att: AttachmentSpec) -> MIMEBase:
    try:
        content = base64.b64decode(att.content_base64)
    except Exception as exc:
        raise ValidationException(
            f"Attachment {att.filename!r} has invalid base64 content: {exc}",
            code="gmail.invalid_attachment_encoding",
        ) from exc

    main_type, _, sub_type = att.mime_type.partition("/")
    part = MIMEBase(main_type or "application", sub_type or "octet-stream")
    part.set_payload(content)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=att.filename)
    return part
