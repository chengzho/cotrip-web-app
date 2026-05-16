from common.auth import get_request_id
from common.db import close_connection_if_needed, get_connection, get_database_config
from common.errors import AppError, InternalServerError, NotFoundError, ValidationError
from common.repositories.candidate_repository import (
    VALID_CATEGORIES,
    create_candidate,
    delete_candidate,
    list_candidates,
    update_candidate,
)
from common.repositories.user_repository import resolve_or_create_user
from common.request import parse_http_event
from common.response import error_response, success_response
from common.validation import require_non_empty_string, validate_enum, validate_uuid_string


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

    if rk == "POST /trips/{tripId}/candidates":
        return _create_candidate(req, conn, user)
    if rk == "GET /trips/{tripId}/candidates":
        return _list_candidates(req, conn, user_id)
    if rk == "PATCH /trips/{tripId}/candidates/{candidateId}":
        return _update_candidate(req, conn, user_id)
    if rk == "DELETE /trips/{tripId}/candidates/{candidateId}":
        return _delete_candidate(req, conn, user_id)

    raise NotFoundError(f"Route not found: {rk}")


def _create_candidate(req, conn, user):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    body = req.body or {}
    category = body.get("category")
    name = body.get("name")
    address = body.get("address")
    note = body.get("note")
    source_url = body.get("source_url")

    validate_enum(category, VALID_CATEGORIES, "category")
    require_non_empty_string(name, "name")

    if source_url is not None and (not isinstance(source_url, str) or not source_url.strip()):
        raise ValidationError("source_url must not be empty if provided")

    candidate = create_candidate(
        conn,
        trip_id,
        str(user["id"]),
        user.get("display_name", ""),
        category,
        name,
        address=address,
        note=note,
        source_url=source_url,
    )
    return {"candidate": candidate}, 201


def _list_candidates(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    category = req.query_parameters.get("category")
    if category is not None:
        validate_enum(category, VALID_CATEGORIES, "category")

    candidates = list_candidates(conn, trip_id, user_id, category=category)
    return {"candidates": candidates}, 200


def _update_candidate(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    candidate_id = req.path_parameters.get("candidateId", "")
    validate_uuid_string(trip_id, "tripId")
    validate_uuid_string(candidate_id, "candidateId")

    if not req.body:
        raise ValidationError("Request body must contain at least one field to update")

    candidate = update_candidate(conn, trip_id, candidate_id, user_id, req.body)
    return {"candidate": candidate}, 200


def _delete_candidate(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    candidate_id = req.path_parameters.get("candidateId", "")
    validate_uuid_string(trip_id, "tripId")
    validate_uuid_string(candidate_id, "candidateId")

    deleted_id = delete_candidate(conn, trip_id, candidate_id, user_id)
    return {"deleted_candidate_id": deleted_id}, 200
