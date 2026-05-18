import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from user_profile.app import lambda_handler


USER_ID = str(uuid.uuid4())

_USER = {
    "id": USER_ID,
    "cognito_sub": "cognito-sub-alice-001",
    "email": "alice@example.com",
    "display_name": "Alice",
}

_UPDATED_USER = {
    "id": USER_ID,
    "cognito_sub": "cognito-sub-alice-001",
    "email": "alice@example.com",
    "display_name": "小周",
}


def _event(method, route_key, body=None):
    return {
        "requestContext": {
            "requestId": "req-test",
            "http": {"method": method, "path": "/me"},
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "cognito-sub-alice-001",
                        "email": "alice@example.com",
                        "name": "Alice",
                    }
                }
            },
        },
        "routeKey": route_key,
        "pathParameters": None,
        "queryStringParameters": None,
        "body": json.dumps(body) if body is not None else None,
    }


@patch("user_profile.app.close_connection_if_needed")
@patch("user_profile.app.get_connection")
@patch("user_profile.app.get_database_config")
@patch("user_profile.app.resolve_or_create_user")
class TestGetMeHandler:
    def test_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("GET", "GET /me"), {})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["success"] is True
        assert data["data"]["user"]["user_id"] == USER_ID
        assert data["data"]["user"]["email"] == "alice@example.com"
        assert data["data"]["user"]["display_name"] == "Alice"

    def test_response_envelope_shape(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("GET", "GET /me"), {})
        body = json.loads(resp["body"])
        assert "success" in body
        assert "data" in body
        assert "error" in body
        assert "request_id" in body

    def test_unknown_route_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event("DELETE", "DELETE /me")
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404

    def test_unexpected_exception_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.side_effect = RuntimeError("db exploded")
        resp = lambda_handler(_event("GET", "GET /me"), {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"


@patch("user_profile.app.close_connection_if_needed")
@patch("user_profile.app.get_connection")
@patch("user_profile.app.get_database_config")
@patch("user_profile.app.resolve_or_create_user")
class TestUpdateMeHandler:
    def test_success_trims_and_persists(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("user_profile.app.update_user_display_name", return_value=_UPDATED_USER):
            resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": "  小周  "}), {})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["success"] is True
        assert data["data"]["user"]["display_name"] == "小周"

    def test_missing_body_display_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("PATCH", "PATCH /me", {}), {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_null_display_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": None}), {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_blank_display_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": "   "}), {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_empty_display_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": ""}), {})
        assert resp["statusCode"] == 400

    def test_display_name_too_long_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        long_name = "A" * 51
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": long_name}), {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_display_name_at_max_length_succeeds(self, mock_user, mock_cfg, mock_conn, mock_close):
        exact_name = "A" * 50
        updated = {**_USER, "display_name": exact_name}
        mock_user.return_value = _USER
        with patch("user_profile.app.update_user_display_name", return_value=updated):
            resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": exact_name}), {})
        assert resp["statusCode"] == 200

    def test_non_string_display_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": 123}), {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_no_body_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event("PATCH", "PATCH /me")
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_unexpected_exception_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.side_effect = RuntimeError("unexpected")
        resp = lambda_handler(_event("PATCH", "PATCH /me", {"display_name": "小周"}), {})
        assert resp["statusCode"] == 500
