from common.auth import get_request_id
from common.db import close_connection_if_needed, get_connection, get_database_config
from common.errors import AppError, InternalServerError, UnauthorizedError
from common.repositories.invite_repository import create_invite, join_invite, preview_invite
from common.repositories.user_repository import resolve_or_create_user
from common.request import parse_http_event
from common.response import error_response, success_response
from common.validation import validate_uuid_string


def lambda_handler(event, context):
    request_id = get_request_id(event)
    conn = None
    try:
        req = parse_http_event(event)
        conn = get_connection(get_database_config())

        if req.route_key == "GET /invites/{inviteToken}":
            result, status_code = _preview_invite(req, conn)
        else:
            user = resolve_or_create_user(conn, req.claims)
            result, status_code = _dispatch_protected(req, conn, user)

        return success_response(result, status_code=status_code, request_id=request_id)
    except AppError as exc:
        return error_response(exc.code, exc.message, exc.status_code, request_id=request_id)
    except Exception as exc:
        err = InternalServerError(str(exc))
        return error_response(err.code, err.message, err.status_code, request_id=request_id)
    finally:
        close_connection_if_needed(conn)


def _dispatch_protected(req, conn, user):
    user_id = str(user["id"])
    rk = req.route_key

    if rk == "POST /trips/{tripId}/invites":
        return _create_invite(req, conn, user_id)
    if rk == "POST /invites/{inviteToken}/join":
        return _join_invite(req, conn, user_id)

    from common.errors import NotFoundError
    raise NotFoundError(f"Route not found: {rk}")


def _create_invite(req, conn, user_id):
    trip_id = req.path_parameters.get("tripId", "")
    validate_uuid_string(trip_id, "tripId")

    body = req.body or {}
    expires_in_days = body.get("expires_in_days")
    max_uses = body.get("max_uses")

    from common.errors import ValidationError
    if expires_in_days is not None:
        if not isinstance(expires_in_days, int) or expires_in_days <= 0:
            raise ValidationError("expires_in_days must be a positive integer")
    if max_uses is not None:
        if not isinstance(max_uses, int) or max_uses <= 0:
            raise ValidationError("max_uses must be a positive integer")

    kwargs = {}
    if expires_in_days is not None:
        kwargs["expires_in_days"] = expires_in_days
    if max_uses is not None:
        kwargs["max_uses"] = max_uses

    invite = create_invite(conn, trip_id, user_id, **kwargs)
    return {"invite": invite}, 201


def _preview_invite(req, conn):
    raw_token = req.path_parameters.get("inviteToken", "")
    from common.errors import ValidationError
    if not raw_token:
        raise ValidationError("inviteToken is required")
    result = preview_invite(conn, raw_token)
    return {"invite_preview": result}, 200


def _join_invite(req, conn, user_id):
    raw_token = req.path_parameters.get("inviteToken", "")
    from common.errors import ValidationError
    if not raw_token:
        raise ValidationError("inviteToken is required")
    result = join_invite(conn, raw_token, user_id)
    return {"trip": result}, 200
