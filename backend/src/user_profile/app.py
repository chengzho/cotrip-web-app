from common.auth import get_request_id
from common.db import close_connection_if_needed, get_connection, get_database_config
from common.errors import AppError, InternalServerError, NotFoundError, ValidationError
from common.repositories.user_repository import resolve_or_create_user, update_user_display_name
from common.request import parse_http_event
from common.response import error_response, success_response

_MAX_DISPLAY_NAME_LEN = 50


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
    rk = req.route_key

    if rk == "GET /me":
        return _get_me(user)
    if rk == "PATCH /me":
        return _update_me(req, conn, user)

    raise NotFoundError(f"Route not found: {rk}")


def _user_payload(user: dict) -> dict:
    return {
        "user": {
            "user_id": str(user["id"]),
            "email": user["email"],
            "display_name": user["display_name"],
        }
    }


def _get_me(user):
    return _user_payload(user), 200


def _update_me(req, conn, user):
    body = req.body or {}
    raw = body.get("display_name")

    if not isinstance(raw, str):
        raise ValidationError("display_name is required")
    trimmed = raw.strip()
    if not trimmed:
        raise ValidationError("display_name must not be empty")
    if len(trimmed) > _MAX_DISPLAY_NAME_LEN:
        raise ValidationError(
            f"display_name must not exceed {_MAX_DISPLAY_NAME_LEN} characters"
        )

    updated = update_user_display_name(conn, str(user["id"]), trimmed)
    return _user_payload(updated), 200
