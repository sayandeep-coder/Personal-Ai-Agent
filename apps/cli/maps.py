"""Google Maps CLI commands.

Purpose: expose Maps integration operations locally.
Responsibilities: call MapsService and render normalized results.
Dependencies: Typer, Maps factory, and Rich output helpers.
Extension Notes: add JSON output flags for automation later.
"""

import typer

from apps.cli.console import console
from apps.cli.output import render_mapping
from services.maps.factory import create_maps_service

maps_app = typer.Typer(help="Google Maps commands.")


@maps_app.command("geocode")
def geocode(address: str) -> None:
    render_mapping(console, "Geocode", create_maps_service().geocode(address).data)


@maps_app.command("reverse-geocode")
def reverse_geocode(latitude: float, longitude: float) -> None:
    render_mapping(console, "Reverse Geocode", create_maps_service().reverse_geocode(latitude, longitude).data)


@maps_app.command("search")
def search(query: str) -> None:
    render_mapping(console, "Places", create_maps_service().place_search(query, None).data)


@maps_app.command("nearby")
def nearby(latitude: float, longitude: float, radius: int = 1000, keyword: str | None = None) -> None:
    render_mapping(console, "Nearby", create_maps_service().nearby(latitude, longitude, radius, keyword).data)


@maps_app.command("details")
def details(place_id: str) -> None:
    render_mapping(console, "Place", create_maps_service().details(place_id).data)


@maps_app.command("autocomplete")
def autocomplete(text: str) -> None:
    render_mapping(console, "Autocomplete", create_maps_service().autocomplete(text).data)


@maps_app.command("directions")
def directions(origin: str, destination: str, mode: str = "driving") -> None:
    render_mapping(console, "Directions", create_maps_service().directions(origin, destination, mode).data)


@maps_app.command("distance-matrix")
def distance_matrix(origins: str, destinations: str, mode: str = "driving") -> None:
    render_mapping(console, "Distance Matrix", create_maps_service().distance_matrix(origins, destinations, mode).data)


@maps_app.command("timezone")
def timezone(latitude: float, longitude: float, timestamp: int) -> None:
    render_mapping(console, "Time Zone", create_maps_service().timezone(latitude, longitude, timestamp).data)
