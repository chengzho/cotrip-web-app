import json
import uuid
from unittest.mock import patch

import pytest

from itinerary.app import lambda_handler


TRIP_ID = str(uuid.uuid4())
ITEM_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
CAND_ID = str(uuid.uuid4())

_USER = {
    "id": USER_ID,
    "cognito_sub": "sub-1",
    "email": "alice@example.com",
    "display_name": "Alice",
}

_ITINERARY = {
    "trip_id": TRIP_ID,
    "days": [
        {
            "day_number": 1,
            "date": "2026-08-20",
            "items": [
                {
                    "item_id": ITEM_ID,
                    "slot": "morning",
                    "title": "Senso-ji",
                    "candidate_id": CAND_ID,
                    "category": "attraction",
                    "note": None,
                    "sort_order": 1,
                }
            ],
        }
    ],
}

_ITEM = {
    "item_id": ITEM_ID,
    "trip_id": TRIP_ID,
    "day_number": 1,
    "slot": "afternoon",
    "title": "Senso-ji",
    "candidate_id": CAND_ID,
    "category": "attraction",
    "note": None,
    "sort_order": 2,
}


def _event(method, path, route_key, path_params=None, query_params=None, body=None):
    return {
        "requestContext": {
            "requestId": "req-test",
            "http": {"method": method, "path": path},
            "authorizer": {"jwt": {"claims": {"sub": "sub-1", "email": "alice@example.com"}}},
        },
        "routeKey": route_key,
        "pathParameters": path_params,
        "queryStringParameters": query_params,
        "body": json.dumps(body) if body is not None else None,
    }


@patch("itinerary.app.close_connection_if_needed")
@patch("itinerary.app.get_connection")
@patch("itinerary.app.get_database_config")
@patch("itinerary.app.resolve_or_create_user")
class TestGenerateItineraryHandler:
    def test_generate_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.generate_itinerary", return_value=_ITINERARY):
            resp = lambda_handler(_event(
                "POST", f"/trips/{TRIP_ID}/itinerary/generate",
                "POST /trips/{tripId}/itinerary/generate",
                path_params={"tripId": TRIP_ID},
                body={},
            ), {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["itinerary"]["trip_id"] == TRIP_ID

    def test_generate_passes_overwrite_true(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.generate_itinerary", return_value=_ITINERARY) as mock_gen:
            lambda_handler(_event(
                "POST", f"/trips/{TRIP_ID}/itinerary/generate",
                "POST /trips/{tripId}/itinerary/generate",
                path_params={"tripId": TRIP_ID},
                body={"overwrite_existing": True},
            ), {})
        mock_gen.assert_called_once()
        assert mock_gen.call_args[1]["overwrite_existing"] is True

    def test_generate_already_exists_returns_409(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ItineraryAlreadyExistsError
        with patch("itinerary.app.generate_itinerary", side_effect=ItineraryAlreadyExistsError()):
            resp = lambda_handler(_event(
                "POST", f"/trips/{TRIP_ID}/itinerary/generate",
                "POST /trips/{tripId}/itinerary/generate",
                path_params={"tripId": TRIP_ID},
                body={},
            ), {})
        assert resp["statusCode"] == 409
        assert json.loads(resp["body"])["error"]["code"] == "ITINERARY_ALREADY_EXISTS"

    def test_generate_no_candidates_returns_409_conflict(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ConflictError
        with patch("itinerary.app.generate_itinerary", side_effect=ConflictError("No candidates")):
            resp = lambda_handler(_event(
                "POST", f"/trips/{TRIP_ID}/itinerary/generate",
                "POST /trips/{tripId}/itinerary/generate",
                path_params={"tripId": TRIP_ID},
                body={},
            ), {})
        assert resp["statusCode"] == 409
        assert json.loads(resp["body"])["error"]["code"] == "CONFLICT"

    def test_invalid_overwrite_type_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event(
            "POST", f"/trips/{TRIP_ID}/itinerary/generate",
            "POST /trips/{tripId}/itinerary/generate",
            path_params={"tripId": TRIP_ID},
            body={"overwrite_existing": "yes"},
        ), {})
        assert resp["statusCode"] == 400
        assert json.loads(resp["body"])["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_trip_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event(
            "POST", "/trips/not-a-uuid/itinerary/generate",
            "POST /trips/{tripId}/itinerary/generate",
            path_params={"tripId": "not-a-uuid"},
            body={},
        ), {})
        assert resp["statusCode"] == 400

    def test_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("itinerary.app.generate_itinerary", side_effect=ForbiddenError()):
            resp = lambda_handler(_event(
                "POST", f"/trips/{TRIP_ID}/itinerary/generate",
                "POST /trips/{tripId}/itinerary/generate",
                path_params={"tripId": TRIP_ID},
                body={},
            ), {})
        assert resp["statusCode"] == 403


@patch("itinerary.app.close_connection_if_needed")
@patch("itinerary.app.get_connection")
@patch("itinerary.app.get_database_config")
@patch("itinerary.app.resolve_or_create_user")
class TestGetItineraryHandler:
    def test_get_itinerary_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.get_itinerary", return_value=_ITINERARY):
            resp = lambda_handler(_event(
                "GET", f"/trips/{TRIP_ID}/itinerary",
                "GET /trips/{tripId}/itinerary",
                path_params={"tripId": TRIP_ID},
            ), {})
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["data"]["itinerary"]["trip_id"] == TRIP_ID

    def test_get_itinerary_empty_returns_200_with_empty_days(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.get_itinerary", return_value={"trip_id": TRIP_ID, "days": []}):
            resp = lambda_handler(_event(
                "GET", f"/trips/{TRIP_ID}/itinerary",
                "GET /trips/{tripId}/itinerary",
                path_params={"tripId": TRIP_ID},
            ), {})
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["data"]["itinerary"]["days"] == []

    def test_get_itinerary_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("itinerary.app.get_itinerary", side_effect=ForbiddenError()):
            resp = lambda_handler(_event(
                "GET", f"/trips/{TRIP_ID}/itinerary",
                "GET /trips/{tripId}/itinerary",
                path_params={"tripId": TRIP_ID},
            ), {})
        assert resp["statusCode"] == 403

    def test_get_itinerary_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("itinerary.app.get_itinerary", side_effect=NotFoundError("Trip not found")):
            resp = lambda_handler(_event(
                "GET", f"/trips/{TRIP_ID}/itinerary",
                "GET /trips/{tripId}/itinerary",
                path_params={"tripId": TRIP_ID},
            ), {})
        assert resp["statusCode"] == 404


@patch("itinerary.app.close_connection_if_needed")
@patch("itinerary.app.get_connection")
@patch("itinerary.app.get_database_config")
@patch("itinerary.app.resolve_or_create_user")
class TestUpdateItemHandler:
    def test_update_item_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.update_itinerary_item", return_value=_ITEM):
            resp = lambda_handler(_event(
                "PATCH", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "PATCH /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
                body={"slot": "afternoon"},
            ), {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["item"]["item_id"] == ITEM_ID

    def test_update_item_empty_patch_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event(
            "PATCH", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
            "PATCH /trips/{tripId}/itinerary/items/{itemId}",
            path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            body={},
        ), {})
        assert resp["statusCode"] == 400
        assert json.loads(resp["body"])["error"]["code"] == "VALIDATION_ERROR"

    def test_update_item_category_edit_rejected(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ValidationError
        with patch("itinerary.app.update_itinerary_item",
                   side_effect=ValidationError("category cannot be updated")):
            resp = lambda_handler(_event(
                "PATCH", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "PATCH /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
                body={"category": "restaurant"},
            ), {})
        assert resp["statusCode"] == 400
        assert json.loads(resp["body"])["error"]["code"] == "VALIDATION_ERROR"

    def test_update_item_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("itinerary.app.update_itinerary_item", side_effect=NotFoundError("not found")):
            resp = lambda_handler(_event(
                "PATCH", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "PATCH /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
                body={"slot": "afternoon"},
            ), {})
        assert resp["statusCode"] == 404

    def test_update_item_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("itinerary.app.update_itinerary_item", side_effect=ForbiddenError()):
            resp = lambda_handler(_event(
                "PATCH", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "PATCH /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
                body={"slot": "afternoon"},
            ), {})
        assert resp["statusCode"] == 403

    def test_invalid_item_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        resp = lambda_handler(_event(
            "PATCH", f"/trips/{TRIP_ID}/itinerary/items/bad-id",
            "PATCH /trips/{tripId}/itinerary/items/{itemId}",
            path_params={"tripId": TRIP_ID, "itemId": "bad-id"},
            body={"slot": "afternoon"},
        ), {})
        assert resp["statusCode"] == 400


@patch("itinerary.app.close_connection_if_needed")
@patch("itinerary.app.get_connection")
@patch("itinerary.app.get_database_config")
@patch("itinerary.app.resolve_or_create_user")
class TestDeleteItemHandler:
    def test_delete_item_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.delete_itinerary_item", return_value=ITEM_ID):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["deleted_item_id"] == ITEM_ID

    def test_delete_does_not_return_204(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.delete_itinerary_item", return_value=ITEM_ID):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] != 204

    def test_delete_item_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("itinerary.app.delete_itinerary_item", side_effect=NotFoundError("not found")):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] == 404

    def test_delete_item_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("itinerary.app.delete_itinerary_item", side_effect=ForbiddenError()):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] == 403

    def test_unexpected_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("itinerary.app.delete_itinerary_item", side_effect=RuntimeError("boom")):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] == 500
        assert json.loads(resp["body"])["error"]["code"] == "INTERNAL_SERVER_ERROR"

    def test_apperror_conversion(self, mock_user, mock_cfg, mock_conn, mock_close):
        from common.errors import InternalServerError
        mock_user.return_value = _USER
        with patch("itinerary.app.delete_itinerary_item", side_effect=InternalServerError()):
            resp = lambda_handler(_event(
                "DELETE", f"/trips/{TRIP_ID}/itinerary/items/{ITEM_ID}",
                "DELETE /trips/{tripId}/itinerary/items/{itemId}",
                path_params={"tripId": TRIP_ID, "itemId": ITEM_ID},
            ), {})
        assert resp["statusCode"] == 500
        assert json.loads(resp["body"])["error"]["code"] == "INTERNAL_SERVER_ERROR"
