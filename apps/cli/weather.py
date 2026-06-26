"""Weather CLI commands.

Purpose: expose Weather integration operations locally.
Responsibilities: call WeatherService and render normalized responses.
Dependencies: Typer, Weather factory, and Rich output helpers.
Extension Notes: add JSON output flags when automation needs them.
"""

import typer

from apps.cli.console import console
from apps.cli.output import render_mapping
from services.weather.factory import create_weather_service

weather_app = typer.Typer(help="Weather commands.")


@weather_app.command("current")
def current(city: str, units: str = "metric") -> None:
    """Show current weather."""
    render_mapping(console, "Current Weather", create_weather_service().current(city, None, units))


@weather_app.command("forecast")
def forecast(city: str, days: int = 5, units: str = "metric") -> None:
    """Show daily forecast."""
    render_mapping(console, "Forecast", create_weather_service().forecast(city, days, units))


@weather_app.command("hourly")
def hourly(city: str, units: str = "metric") -> None:
    """Show hourly forecast."""
    render_mapping(console, "Hourly Forecast", create_weather_service().hourly(city, units))


@weather_app.command("air-quality")
def air_quality(city: str) -> None:
    """Show air quality."""
    render_mapping(console, "Air Quality", create_weather_service().air_quality(city))


@weather_app.command("uv")
def uv(city: str, units: str = "metric") -> None:
    """Show UV index."""
    render_mapping(console, "UV Index", create_weather_service().uv(city, units))


@weather_app.command("alerts")
def alerts(city: str, units: str = "metric") -> None:
    """Show weather alerts."""
    render_mapping(console, "Weather Alerts", create_weather_service().alerts(city, units))
