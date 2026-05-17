from common.auth import get_request_id
from common.db import close_connection_if_needed, get_connection, get_database_config
from common.errors import AppError, InternalServerError, NotFoundError, ValidationError
from common.repositories.itinerary_repository import (
    delete_itinerary_item,
    generate_itinerary,
    get_itinerary,
    update_itinerary_item,
)
from common.repositories.user_repository import resolve_or_create_user
from common.request import parse_http_event
from common.response import error_response, success_response
from common.validation import ensure_non_empty_patch_payload, validate_uuid_string


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

    if rk == "POST /trips/{tripId}/itinerary/generate":
        return _generate_itinerary(req, conn, user_id)
    if rk == "GET /trips/{tripId}/itinerary":
        return _get_itinerary(req, conn, user_id)
    if rk == "PATCH /trips/{tripId}/itinerary/items/{itemId}":
        return _update_item(req, conn, user_id)
    if rk == "DELETE /trips/{tripId}/itinerary/items/{itemId}":
        return _delete_item(req, conn, user_id)

    raise NotFoundError(f"Route not found: {rk}")


def _generate_itinerary(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    body = req.body or {}
    overwrite_existing = body.get("overwrite_existing", False)
    if not isinstance(overwrite_existing, bool):
        raise ValidationError("overwrite_existing must be a boolean")

    itinerary = generate_itinerary(conn, trip_id, user_id, overwrite_existing=overwrite_existing)
    return {"itinerary": itinerary}, 200


def _get_itinerary(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    itinerary = get_itinerary(conn, trip_id, user_id)
    return {"itinerary": itinerary}, 200


def _update_item(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    item_id = req.path_parameters.get("itemId", "")
    validate_uuid_string(trip_id, "tripId")
    validate_uuid_string(item_id, "itemId")

    patch = req.body or {}
    ensure_non_empty_patch_payload(patch)

    item = update_itinerary_item(conn, trip_id, item_id, user_id, patch)
    return {"item": item}, 200


def _delete_item(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    item_id = req.path_parameters.get("itemId", "")
    validate_uuid_string(trip_id, "tripId")
    validate_uuid_string(item_id, "itemId")

    deleted_id = delete_itinerary_item(conn, trip_id, item_id, user_id)
    return {"deleted_item_id": deleted_id}, 200
