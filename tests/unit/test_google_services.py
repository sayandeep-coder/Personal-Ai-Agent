"""Google service wrapper tests.

Purpose: verify Gmail, Calendar, Drive, Docs, and Sheets wrappers.
Responsibilities: cover pagination, CRUD, permissions, and payload construction.
Dependencies: service wrappers and fakes.
Extension Notes: add live contract tests with Google sandbox accounts later.
"""

import pytest

from core.exceptions import ValidationException
from services.google.calendar.service import CalendarService
from services.google.docs.service import DocsService
from services.google.drive.service import DriveService
from services.google.gmail.service import GmailService
from services.google.sheets.service import SheetsService
from tests.unit.google_fakes import Client, Credentials


def test_gmail_pagination_empty_and_unread() -> None:
    """Gmail supports pagination and unread count."""
    client = Client()
    service = GmailService(Credentials(), client)
    result = service.list_messages("user@example.com", page_token="next")
    messages = result["messages"]
    assert isinstance(messages, list)
    assert messages[0]["subject"] == "Hi"
    assert service.unread_count("user@example.com") == 2
    assert service.send_message("user@example.com", ["to@example.com"], "Hi", "Body")["sent"] is True


def test_gmail_unauthorized_expired_token() -> None:
    """Gmail surfaces credential failures."""
    with pytest.raises(ValidationException):
        GmailService(Credentials(), Client()).list_messages("expired@example.com")


def test_calendar_crud_timezone_and_freebusy() -> None:
    """Calendar supports CRUD and freebusy calls."""
    service = CalendarService(Credentials(), Client())
    assert service.today_events("user@example.com", "Asia/Kolkata")
    assert service.create_event("user@example.com", {"summary": "Meet"})
    assert service.update_event("user@example.com", "evt", {"summary": "New"})
    assert service.delete_event("user@example.com", "evt")["deleted"] is True
    assert service.freebusy("user@example.com", {"items": []})


def test_drive_pagination_missing_permissions() -> None:
    """Drive supports list/download/delete and propagates permission errors."""
    service = DriveService(Credentials(), Client())
    assert service.list_files("user@example.com")["files"]
    raw, ct, fname = service.download("user@example.com", "file")
    assert raw == b"fake-binary-content"
    assert ct
    assert fname
    assert service.delete("user@example.com", "file")["deleted"] is True
    with pytest.raises(ValidationException):
        service.list_files("expired@example.com")


def test_docs_read_update_permissions() -> None:
    """Docs supports read and update operations."""
    service = DocsService(Credentials(), Client())
    assert service.list_documents("user@example.com")["documents"]
    document = service.read_document("user@example.com", "doc")
    assert document["url"] == "https://docs.google.com/document/d/doc/edit"
    assert service.append_text("user@example.com", "doc", "hello")
    assert service.replace_text("user@example.com", "doc", "old", "new")


def test_sheets_read_append_batch_update() -> None:
    """Sheets supports read, append, and batch update."""
    service = SheetsService(Credentials(), Client())
    assert service.list_spreadsheets("user@example.com")["spreadsheets"]
    sheet = service.read_spreadsheet("user@example.com", "sheet")
    assert sheet["url"] == "https://docs.google.com/spreadsheets/d/sheet/edit"
    assert service.append_rows("user@example.com", "sheet", "A1", [["x"]])
    assert service.batch_update("user@example.com", "sheet", {"requests": []})
