import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from trip_group.app import lambda_handler


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())

_USER = {
    "id": USER_ID,
    "cognito_sub": "sub-1",
    "email": "alice@example.com",
    "display_name": "Alice",
    "created_at": "2025-01-01",
    "updated_at": "2025-01-01",
}

_TRIP = {
    "trip_id": TRIP_ID,
    "title": "Beach Trip",
    "destination": "Maui",
    "start_date": "2025-06-01",
    "end_date": "2025-06-10",
    "description": None,
    "role": "owner",
    "created_at": "2025-01-01",
    "updated_at": "2025-01-01",
}


def _event(method, path, route_key, path_params=None, query_params=None, body=None):
    event = {
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
    return event


def _mock_conn():
    conn = MagicMock()
    return conn


@patch("trip_group.app.close_connection_if_needed")
@patch("trip_group.app.get_connection")
@patch("trip_group.app.get_database_config")
@patch("trip_group.app.resolve_or_create_user")
class TestTripGroupHandler:
    def test_create_trip_returns_201(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("trip_group.app.create_trip", return_value=_TRIP):
            event = _event(
                "POST", "/trips", "POST /trips",
                body={"title": "Beach Trip", "destination": "Maui",
                      "start_date": "2025-06-01", "end_date": "2025-06-10"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["data"]["title"] == "Beach Trip"

    def test_create_trip_missing_title_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", "/trips", "POST /trips",
            body={"destination": "Maui", "start_date": "2025-06-01", "end_date": "2025-06-10"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_list_trips_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("trip_group.app.list_trips", return_value=[_TRIP]):
            event = _event("GET", "/trips", "GET /trips", query_params={"scope": "upcoming"})
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data["data"]["trips"]) == 1

    def test_list_trips_invalid_scope_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("trip_group.app.list_trips", side_effect=__import__("common.errors", fromlist=["ValidationError"]).ValidationError("scope must be")):
            event = _event("GET", "/trips", "GET /trips", query_params={"scope": "bogus"})
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_get_trip_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        detail = {**_TRIP, "current_user_role": "owner", "summary": {}}
        with patch("trip_group.app.get_trip_detail", return_value=detail):
            event = _event("GET", f"/trips/{TRIP_ID}", "GET /trips/{tripId}",
                           path_params={"tripId": TRIP_ID})
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200

    def test_get_trip_invalid_uuid_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event("GET", "/trips/not-a-uuid", "GET /trips/{tripId}",
                       path_params={"tripId": "not-a-uuid"})
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_update_trip_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        updated = {**_TRIP, "title": "New Title"}
        with patch("trip_group.app.update_trip", return_value=updated):
            event = _event("PATCH", f"/trips/{TRIP_ID}", "PATCH /trips/{tripId}",
                           path_params={"tripId": TRIP_ID},
                           body={"title": "New Title"})
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["data"]["title"] == "New Title"

    def test_update_trip_empty_body_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event("PATCH", f"/trips/{TRIP_ID}", "PATCH /trips/{tripId}",
                       path_params={"tripId": TRIP_ID})
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_list_members_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        members = [{"user_id": USER_ID, "display_name": "Alice",
                    "email": "alice@example.com", "role": "owner", "joined_at": "2025-01-01"}]
        with patch("trip_group.app.list_members", return_value=members):
            event = _event("GET", f"/trips/{TRIP_ID}/members", "GET /trips/{tripId}/members",
                           path_params={"tripId": TRIP_ID})
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data["data"]["members"]) == 1

    def test_unknown_route_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event("DELETE", "/trips", "DELETE /trips")
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404

    def test_internal_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.side_effect = RuntimeError("db exploded")
        event = _event("GET", "/trips", "GET /trips")
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
