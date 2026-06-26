"""Google Maps service factory.

Purpose: assemble Maps integration dependencies.
Responsibilities: wire settings, provider, transport, and service.
Dependencies: settings, GoogleMapsProvider, and transport.
Extension Notes: swap provider implementations here without route changes.
"""

from core.config import Settings, settings
from integrations.maps.provider import GoogleMapsProvider
from integrations.maps.transport import UrllibMapsTransport
from services.maps.service import MapsService


def create_maps_service(app_settings: Settings = settings) -> MapsService:
    """Create a production Google Maps service."""
    return MapsService(GoogleMapsProvider(app_settings, UrllibMapsTransport()))
