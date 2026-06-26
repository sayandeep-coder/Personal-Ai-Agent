"""Weather service factory.

Purpose: assemble Weather integration dependencies.
Responsibilities: wire settings, provider, transport, and service.
Dependencies: settings, OpenWeather provider, and urllib transport.
Extension Notes: swap provider implementations here without route changes.
"""

from core.config import Settings, settings
from integrations.weather.provider import OpenWeatherProvider
from integrations.weather.transport import UrllibWeatherTransport
from services.weather.service import WeatherService


def create_weather_service(app_settings: Settings = settings) -> WeatherService:
    """Create a production Weather service."""
    provider = OpenWeatherProvider(app_settings, UrllibWeatherTransport())
    return WeatherService(provider)
