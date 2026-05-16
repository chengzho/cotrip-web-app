import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from invite.app import lambda_handler


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
INVITE_ID = str(uuid.uuid4())
RAW_TOKEN = "fake-invite-token-abc123"

_USER = {
    "id": USER_ID,
    "cognito_sub": "sub-1",
    "email": "alice@example.com",
    "display_name": "Alice",
}

_INVITE = {
    "id": INVITE_ID,
    "trip_id": TRIP_ID,
    "invite_url": f"https://app.example.com/join/{RAW_TOKEN}",
    "expires_at": "2026-05-22T00:00:00+00:00",
    "max_uses": 20,
}

_PREVIEW = {
    "trip_title": "Tokyo Graduation Trip",
    "destination": "Tokyo, Japan",
    "start_date": "2026-08-20",
    "end_date": "2026-08-25",
    "invited_by_display_name": "Alice",
}

_TRIP_SUMMARY = {
    "id": TRIP_ID,
    "title": "Tokyo Graduation Trip",
    "destination": "Tokyo, Japan",
    "current_user_role": "member",
}


def _auth_event(method, path, route_key, path_params=None, query_params=None, body=None):
    return {
        "requestContext": {
            "requestId": "req-test",
            "http": {"method": method, "path": path},
            "authorizer": {"jwt": {"claims": {"sub": "sub-1", "email": "alice@example.com"}}},
        },
        "routeKey": route_key,
        "pathParameters": path_params,
        "queryStringParameters": query_params,
        "body": json.dumps(body) if body else None,
    }


def _public_event(method, path, route_key, path_params=None):
    """Event without JWT authorizer claims (public route)."""
    return {
        "requestContext": {
            "requestId": "req-test",
            "http": {"method": method, "path": path},
        },
        "routeKey": route_key,
        "pathParameters": path_params,
        "queryStringParameters": None,
        "body": None,
    }


@patch("invite.app.close_connection_if_needed")
@patch("invite.app.get_connection")
@patch("invite.app.get_database_config")
@patch("invite.app.resolve_or_create_user")
class TestCreateInviteHandler:
    def test_create_invite_success_returns_201(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("invite.app.create_invite", return_value=_INVITE):
            event = _auth_event(
                "POST",
                f"/trips/{TRIP_ID}/invites",
                "POST /trips/{tripId}/invites",
                path_params={"tripId": TRIP_ID},
                body={"expires_in_days": 7, "max_uses": 20},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 201
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["invite"]["id"] == INVITE_ID

    def test_create_invite_invalid_trip_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _auth_event(
            "POST",
            "/trips/not-a-uuid/invites",
            "POST /trips/{tripId}/invites",
            path_params={"tripId": "not-a-uuid"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_invite_negative_expires_in_days_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _auth_event(
            "POST",
            f"/trips/{TRIP_ID}/invites",
            "POST /trips/{tripId}/invites",
            path_params={"tripId": TRIP_ID},
            body={"expires_in_days": -1},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_invite_non_owner_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("invite.app.create_invite", side_effect=ForbiddenError("Only the trip owner can create invite links")):
            event = _auth_event(
                "POST",
                f"/trips/{TRIP_ID}/invites",
                "POST /trips/{tripId}/invites",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "FORBIDDEN"

    def test_create_invite_unexpected_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("invite.app.create_invite", side_effect=RuntimeError("boom")):
            event = _auth_event(
                "POST",
                f"/trips/{TRIP_ID}/invites",
                "POST /trips/{tripId}/invites",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"


@patch("invite.app.close_connection_if_needed")
@patch("invite.app.get_connection")
@patch("invite.app.get_database_config")
class TestPreviewInviteHandler:
    def test_preview_success_no_jwt_returns_200(self, mock_cfg, mock_conn, mock_close):
        with patch("invite.app.preview_invite", return_value=_PREVIEW):
            event = _public_event(
                "GET",
                f"/invites/{RAW_TOKEN}",
                "GET /invites/{inviteToken}",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["invite_preview"]["trip_title"] == "Tokyo Graduation Trip"

    def test_preview_not_found_returns_404(self, mock_cfg, mock_conn, mock_close):
        from common.errors import NotFoundError
        with patch("invite.app.preview_invite", side_effect=NotFoundError("Invite not found")):
            event = _public_event(
                "GET",
                "/invites/bad-token",
                "GET /invites/{inviteToken}",
                path_params={"inviteToken": "bad-token"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "NOT_FOUND"

    def test_preview_expired_returns_400(self, mock_cfg, mock_conn, mock_close):
        from common.errors import InviteExpiredError
        with patch("invite.app.preview_invite", side_effect=InviteExpiredError()):
            event = _public_event(
                "GET",
                f"/invites/{RAW_TOKEN}",
                "GET /invites/{inviteToken}",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INVITE_EXPIRED"

    def test_preview_revoked_returns_400(self, mock_cfg, mock_conn, mock_close):
        from common.errors import InviteRevokedError
        with patch("invite.app.preview_invite", side_effect=InviteRevokedError()):
            event = _public_event(
                "GET",
                f"/invites/{RAW_TOKEN}",
                "GET /invites/{inviteToken}",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INVITE_REVOKED"


@patch("invite.app.close_connection_if_needed")
@patch("invite.app.get_connection")
@patch("invite.app.get_database_config")
@patch("invite.app.resolve_or_create_user")
class TestJoinInviteHandler:
    def test_join_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("invite.app.join_invite", return_value=_TRIP_SUMMARY):
            event = _auth_event(
                "POST",
                f"/invites/{RAW_TOKEN}/join",
                "POST /invites/{inviteToken}/join",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["trip"]["current_user_role"] == "member"

    def test_join_unauthenticated_returns_401(self, mock_user, mock_cfg, mock_conn, mock_close):
        from common.errors import UnauthorizedError
        mock_user.side_effect = UnauthorizedError()
        event = _public_event(
            "POST",
            f"/invites/{RAW_TOKEN}/join",
            "POST /invites/{inviteToken}/join",
            path_params={"inviteToken": RAW_TOKEN},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 401
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "UNAUTHORIZED"

    def test_join_already_exists_returns_409(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import AlreadyExistsError
        with patch("invite.app.join_invite", side_effect=AlreadyExistsError("already a member")):
            event = _auth_event(
                "POST",
                f"/invites/{RAW_TOKEN}/join",
                "POST /invites/{inviteToken}/join",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 409
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "ALREADY_EXISTS"

    def test_join_invite_expired_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import InviteExpiredError
        with patch("invite.app.join_invite", side_effect=InviteExpiredError()):
            event = _auth_event(
                "POST",
                f"/invites/{RAW_TOKEN}/join",
                "POST /invites/{inviteToken}/join",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INVITE_EXPIRED"

    def test_join_unexpected_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("invite.app.join_invite", side_effect=RuntimeError("unexpected")):
            event = _auth_event(
                "POST",
                f"/invites/{RAW_TOKEN}/join",
                "POST /invites/{inviteToken}/join",
                path_params={"inviteToken": RAW_TOKEN},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
