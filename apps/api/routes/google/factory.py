"""Google API service factory for routes.

Purpose: build Google service wrappers from request dependencies.
Responsibilities: wire credential resolver and Google REST client.
Dependencies: container, SQLAlchemy session, Google services.
Extension Notes: centralize quota/rate-limit dependencies here later.
"""

from sqlalchemy.orm import Session

from core.container import ServiceContainer
from services.google.factory import credential_resolver, google_client
from services.google.gmail.service import GmailService
from services.google.calendar.service import CalendarService
from services.google.drive.service import DriveService
from services.google.docs.service import DocsService
from services.google.sheets.service import SheetsService


def gmail(container: ServiceContainer, session: Session) -> GmailService:
    """Create Gmail service."""
    return GmailService(credential_resolver(container.settings, session), google_client())


def calendar(container: ServiceContainer, session: Session) -> CalendarService:
    """Create Calendar service."""
    return CalendarService(credential_resolver(container.settings, session), google_client())


def drive(container: ServiceContainer, session: Session) -> DriveService:
    """Create Drive service."""
    return DriveService(credential_resolver(container.settings, session), google_client())


def docs(container: ServiceContainer, session: Session) -> DocsService:
    """Create Docs service."""
    return DocsService(credential_resolver(container.settings, session), google_client())


def sheets(container: ServiceContainer, session: Session) -> SheetsService:
    """Create Sheets service."""
    return SheetsService(credential_resolver(container.settings, session), google_client())

