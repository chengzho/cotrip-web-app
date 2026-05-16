from common.auth import get_request_id
from common.db import close_connection_if_needed, get_connection, get_database_config
from common.errors import AppError, InternalServerError, NotFoundError
from common.repositories.candidate_repository import VALID_CATEGORIES
from common.repositories.user_repository import resolve_or_create_user
from common.repositories.vote_repository import get_rankings, unvote_candidate, vote_candidate
from common.request import parse_http_event
from common.response import error_response, success_response
from common.validation import validate_enum, validate_uuid_string


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

    if rk == "POST /candidates/{candidateId}/votes":
        return _vote(req, conn, user_id)
    if rk == "DELETE /candidates/{candidateId}/votes":
        return _unvote(req, conn, user_id)
    if rk == "GET /trips/{tripId}/rankings":
        return _rankings(req, conn, user_id)

    raise NotFoundError(f"Route not found: {rk}")


def _vote(req, conn, user_id):
    candidate_id = req.path_parameters.get("candidateId", "")
    validate_uuid_string(candidate_id, "candidateId")
    result = vote_candidate(conn, candidate_id, user_id)
    return result, 200


def _unvote(req, conn, user_id):
    candidate_id = req.path_parameters.get("candidateId", "")
    validate_uuid_string(candidate_id, "candidateId")
    result = unvote_candidate(conn, candidate_id, user_id)
    return result, 200


def _rankings(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    category = req.query_parameters.get("category")
    if category is not None:
        validate_enum(category, VALID_CATEGORIES, "category")

    rankings = get_rankings(conn, trip_id, user_id, category=category)
    return {"rankings": rankings}, 200
