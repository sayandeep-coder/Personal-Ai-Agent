"""Google Maps API routes.

Purpose: expose read-only Google Maps integration endpoints.
Responsibilities: validate HTTP inputs and delegate to MapsService.
Dependencies: FastAPI, Maps service factory, schemas, and envelopes.
Extension Notes: add async route wrappers when transport becomes async.
"""

from collections.abc import Callable
from time import perf_counter

from fastapi import APIRouter, Query
from fastapi.responses import Response

from apps.api.maps_responses import fail, ok
from apps.api.schemas.maps import TravelMode
from core.exceptions import ApplicationException
from services.maps.factory import create_maps_service
from services.maps.types import MapsResult

router = APIRouter(prefix="/maps", tags=["maps"])


def geocode(address: str = Query(..., min_length=1)) -> Response:
    return _run(lambda: create_maps_service().geocode(address))


def reverse_geocode(latitude: float = Query(...), longitude: float = Query(...)) -> Response:
    return _run(lambda: create_maps_service().reverse_geocode(latitude, longitude))


def place_search(query: str = Query(..., min_length=1), page_token: str | None = None) -> Response:
    return _run(lambda: create_maps_service().place_search(query, page_token))


def nearby(latitude: float, longitude: float, radius: int = Query(1000), keyword: str | None = None) -> Response:
    return _run(lambda: create_maps_service().nearby(latitude, longitude, radius, keyword))


def details(place_id: str) -> Response:
    return _run(lambda: create_maps_service().details(place_id))


def autocomplete(input: str = Query(..., min_length=1)) -> Response:
    return _run(lambda: create_maps_service().autocomplete(input))


def directions(origin: str, destination: str, mode: TravelMode = TravelMode.DRIVING) -> Response:
    return _run(lambda: create_maps_service().directions(origin, destination, mode.value))


def distance_matrix(origins: str, destinations: str, mode: TravelMode = TravelMode.DRIVING) -> Response:
    return _run(lambda: create_maps_service().distance_matrix(origins, destinations, mode.value))


def timezone(latitude: float, longitude: float, timestamp: int) -> Response:
    return _run(lambda: create_maps_service().timezone(latitude, longitude, timestamp))


def _run(call: Callable[[], MapsResult]) -> Response:
    started = perf_counter()
    try:
        return ok(call(), started)
    except ApplicationException as exc:
        return fail(exc, started)


router.add_api_route("/geocode", geocode, methods=["GET"])
router.add_api_route("/reverse-geocode", reverse_geocode, methods=["GET"])
router.add_api_route("/places/search", place_search, methods=["GET"])
router.add_api_route("/places/nearby", nearby, methods=["GET"])
router.add_api_route("/places/{place_id}", details, methods=["GET"])
router.add_api_route("/autocomplete", autocomplete, methods=["GET"])
router.add_api_route("/directions", directions, methods=["GET"])
router.add_api_route("/distance-matrix", distance_matrix, methods=["GET"])
router.add_api_route("/timezone", timezone, methods=["GET"])
