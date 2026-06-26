"""Google API route smoke tests.

Purpose: verify Google API routers are registered.
Responsibilities: assert expected route paths exist on the FastAPI app.
Dependencies: app factory with fake container.
Extension Notes: add full route fakes when request/response contracts harden.
"""

from apps.api.app import create_app
from core.factory import create_container


def test_google_routes_are_registered() -> None:
    """Google integration routes are present."""
    app = create_app(create_container())
    paths = set(app.openapi()["paths"])
    assert "/api/v1/gmail/messages" in paths
    assert "/api/v1/gmail/send" in paths
    assert "/api/v1/calendar/events" in paths
    assert "/api/v1/drive/files" in paths
    assert "/api/v1/docs" in paths
    assert "/api/v1/docs/{id}" in paths
    assert "/api/v1/sheets" in paths
    assert "/api/v1/sheets/{id}" in paths
    assert "/api/v1/weather/current" in paths
    assert "/api/v1/weather/forecast" in paths
    assert "/api/v1/weather/hourly" in paths
    assert "/api/v1/weather/air-quality" in paths
    assert "/api/v1/weather/uv" in paths
    assert "/api/v1/weather/alerts" in paths
    assert "/api/v1/maps/geocode" in paths
    assert "/api/v1/maps/reverse-geocode" in paths
    assert "/api/v1/maps/places/search" in paths
    assert "/api/v1/maps/places/nearby" in paths
    assert "/api/v1/maps/places/{place_id}" in paths
    assert "/api/v1/maps/autocomplete" in paths
    assert "/api/v1/maps/directions" in paths
    assert "/api/v1/maps/distance-matrix" in paths
    assert "/api/v1/maps/timezone" in paths
