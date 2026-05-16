from common.auth import get_request_id
from common.db import get_connection, get_database_config, close_connection_if_needed
from common.errors import AppError, ErrorCode, ForbiddenError, InternalServerError, NotFoundError, ValidationError
from common.repositories.trip_repository import (
    create_trip,
    get_trip_detail,
    list_members,
    list_trips,
    update_trip,
)
from common.repositories.user_repository import resolve_or_create_user
from common.request import parse_http_event
from common.response import error_response, success_response
from common.validation import require_non_empty_string, validate_date_range, validate_date_string, validate_uuid_string


def lambda_handler(event, context):
    request_id = get_request_id(event)
    conn = None
    try:
        req = parse_http_event(event)
        conn = get_connection(get_database_config())
        user = resolve_or_create_user(conn, req.claims)
        result, status_code = _dispatch(req, conn, user)
        return success_response(result, status_code=status_code, request_id=request_id)
    except AppError as exc:
        return error_response(exc.code, exc.message, exc.status_code, request_id=request_id)
    except Exception as exc:
        err = InternalServerError(str(exc))
        return error_response(err.code, err.message, err.status_code, request_id=request_id)
    finally:
        close_connection_if_needed(conn)


def _dispatch(req, conn, user):
    user_id = str(user["id"])
    rk = req.route_key

    if rk == "POST /trips":
        return _create_trip(req, conn, user_id)
    if rk == "GET /trips":
        return _list_trips(req, conn, user_id)
    if rk == "GET /trips/{tripId}":
        return _get_trip(req, conn, user_id)
    if rk == "PATCH /trips/{tripId}":
        return _update_trip(req, conn, user_id)
    if rk == "GET /trips/{tripId}/members":
        return _list_members(req, conn, user_id)

    raise NotFoundError(f"Route not found: {rk}")


def _create_trip(req, conn, user_id):
    body = req.body or {}
    title = body.get("title")
    destination = body.get("destination")
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    description = body.get("description")

    require_non_empty_string(title, "title")
    require_non_empty_string(destination, "destination")
    require_non_empty_string(start_date, "start_date")
    require_non_empty_string(end_date, "end_date")
    validate_date_string(start_date, "start_date")
    validate_date_string(end_date, "end_date")
    validate_date_range(start_date, end_date)

    trip = create_trip(conn, user_id, title, destination, start_date, end_date, description)
    return trip, 201


def _list_trips(req, conn, user_id):
    scope = req.query_parameters.get("scope", "upcoming")
    trips = list_trips(conn, user_id, scope)
    return {"trips": trips}, 200


def _get_trip(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")
    trip = get_trip_detail(conn, trip_id, user_id)
    return trip, 200


def _update_trip(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")
    if not req.body:
        raise ValidationError("Request body must contain at least one field to update")
    trip = update_trip(conn, trip_id, user_id, req.body)
    return trip, 200


def _list_members(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")
    members = list_members(conn, trip_id, user_id)
    return {"members": members}, 200
