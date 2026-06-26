"""Google test payload builders.

Purpose: provide realistic Google API payloads for unit fakes.
Responsibilities: keep fake clients small and product payloads reusable.
Dependencies: typed Google JSON alias.
Extension Notes: add edge-case payloads as normalizers grow.
"""

from integrations.google.common.http import JsonDict


def gmail_message() -> JsonDict:
    """Return a realistic Gmail message."""
    return {
        "id": "m1",
        "threadId": "t1",
        "labelIds": ["INBOX", "UNREAD"],
        "snippet": "Hello",
        "payload": {"mimeType": "text/plain", "headers": [{"name": "Subject", "value": "Hi"}], "body": {"data": "SGVsbG8="}},
    }


def drive_file() -> JsonDict:
    """Return a realistic Drive file."""
    return {"id": "file", "name": "notes.txt", "mimeType": "text/plain", "size": "12"}


def doc_file() -> JsonDict:
    """Return a Drive file entry for a Google Doc."""
    return {"id": "doc", "name": "Doc", "createdTime": "2026-06-01T00:00:00Z"}


def sheet_file() -> JsonDict:
    """Return a Drive file entry for a Google Sheet."""
    return {"id": "sheet", "name": "Expenses", "modifiedTime": "2026-06-01T00:00:00Z"}


def doc() -> JsonDict:
    """Return a realistic Docs document."""
    text = {"textRun": {"content": "Hello world"}}
    return {"documentId": "doc", "title": "Doc", "body": {"content": [{"paragraph": {"elements": [text]}}]}}


def sheet() -> JsonDict:
    """Return a realistic spreadsheet."""
    props = {"title": "Sheet1", "gridProperties": {"rowCount": 10, "columnCount": 5}}
    return {"spreadsheetId": "sheet", "properties": {"title": "Expenses"}, "sheets": [{"properties": props}]}


def event() -> JsonDict:
    """Return a realistic calendar event."""
    return {"id": "evt", "summary": "Meet", "start": {"dateTime": "2026-06-30T10:00:00+05:30"}}
