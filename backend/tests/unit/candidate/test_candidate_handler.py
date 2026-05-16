import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from candidate.app import lambda_handler


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
CANDIDATE_ID = str(uuid.uuid4())

_USER = {
    "id": USER_ID,
    "cognito_sub": "sub-1",
    "email": "alice@example.com",
    "display_name": "Alice",
}

_CANDIDATE = {
    "candidate_id": CANDIDATE_ID,
    "trip_id": TRIP_ID,
    "category": "attraction",
    "name": "Tokyo Skytree",
    "address": "1-1-2 Oshiage",
    "note": "Nice views",
    "source_url": "https://example.com",
    "created_by": {"user_id": USER_ID, "display_name": "Alice"},
    "vote_count": 0,
    "current_user_voted": False,
    "created_at": "2026-08-01T10:00:00+00:00",
    "updated_at": "2026-08-01T10:00:00+00:00",
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
        "body": json.dumps(body) if body else None,
    }


@patch("candidate.app.close_connection_if_needed")
@patch("candidate.app.get_connection")
@patch("candidate.app.get_database_config")
@patch("candidate.app.resolve_or_create_user")
class TestCreateCandidateHandler:
    def test_success_returns_201(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.create_candidate", return_value=_CANDIDATE):
            event = _event(
                "POST", f"/trips/{TRIP_ID}/candidates",
                "POST /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
                body={"category": "attraction", "name": "Tokyo Skytree"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 201
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["candidate"]["candidate_id"] == CANDIDATE_ID

    def test_missing_category_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", f"/trips/{TRIP_ID}/candidates",
            "POST /trips/{tripId}/candidates",
            path_params={"tripId": TRIP_ID},
            body={"name": "Tokyo Skytree"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_category_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", f"/trips/{TRIP_ID}/candidates",
            "POST /trips/{tripId}/candidates",
            path_params={"tripId": TRIP_ID},
            body={"category": "hotel", "name": "Tokyo Skytree"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_missing_name_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", f"/trips/{TRIP_ID}/candidates",
            "POST /trips/{tripId}/candidates",
            path_params={"tripId": TRIP_ID},
            body={"category": "attraction"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_invalid_trip_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", "/trips/not-a-uuid/candidates",
            "POST /trips/{tripId}/candidates",
            path_params={"tripId": "not-a-uuid"},
            body={"category": "attraction", "name": "X"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_non_member_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("candidate.app.create_candidate", side_effect=ForbiddenError("not a member")):
            event = _event(
                "POST", f"/trips/{TRIP_ID}/candidates",
                "POST /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
                body={"category": "attraction", "name": "X"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403

    def test_unexpected_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.create_candidate", side_effect=RuntimeError("boom")):
            event = _event(
                "POST", f"/trips/{TRIP_ID}/candidates",
                "POST /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
                body={"category": "attraction", "name": "X"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"


@patch("candidate.app.close_connection_if_needed")
@patch("candidate.app.get_connection")
@patch("candidate.app.get_database_config")
@patch("candidate.app.resolve_or_create_user")
class TestListCandidatesHandler:
    def test_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.list_candidates", return_value=[_CANDIDATE]):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/candidates",
                "GET /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert len(body["data"]["candidates"]) == 1

    def test_with_valid_category_filter(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.list_candidates", return_value=[]) as mock_list:
            event = _event(
                "GET", f"/trips/{TRIP_ID}/candidates",
                "GET /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
                query_params={"category": "restaurant"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args
        assert call_kwargs[1]["category"] == "restaurant"

    def test_invalid_category_filter_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "GET", f"/trips/{TRIP_ID}/candidates",
            "GET /trips/{tripId}/candidates",
            path_params={"tripId": TRIP_ID},
            query_params={"category": "hotel"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_empty_list_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.list_candidates", return_value=[]):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/candidates",
                "GET /trips/{tripId}/candidates",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["data"]["candidates"] == []


@patch("candidate.app.close_connection_if_needed")
@patch("candidate.app.get_connection")
@patch("candidate.app.get_database_config")
@patch("candidate.app.resolve_or_create_user")
class TestUpdateCandidateHandler:
    def test_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        updated = {**_CANDIDATE, "note": "Updated note"}
        with patch("candidate.app.update_candidate", return_value=updated):
            event = _event(
                "PATCH", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "PATCH /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
                body={"note": "Updated note"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["data"]["candidate"]["note"] == "Updated note"

    def test_empty_body_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "PATCH", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
            "PATCH /trips/{tripId}/candidates/{candidateId}",
            path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("candidate.app.update_candidate", side_effect=ForbiddenError("not authorized")):
            event = _event(
                "PATCH", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "PATCH /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
                body={"note": "x"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403

    def test_invalid_candidate_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "PATCH", f"/trips/{TRIP_ID}/candidates/bad-id",
            "PATCH /trips/{tripId}/candidates/{candidateId}",
            path_params={"tripId": TRIP_ID, "candidateId": "bad-id"},
            body={"note": "x"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("candidate.app.update_candidate", side_effect=NotFoundError("Candidate not found")):
            event = _event(
                "PATCH", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "PATCH /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
                body={"note": "x"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404


@patch("candidate.app.close_connection_if_needed")
@patch("candidate.app.get_connection")
@patch("candidate.app.get_database_config")
@patch("candidate.app.resolve_or_create_user")
class TestDeleteCandidateHandler:
    def test_success_returns_200_with_deleted_id(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.delete_candidate", return_value=CANDIDATE_ID):
            event = _event(
                "DELETE", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "DELETE /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["deleted_candidate_id"] == CANDIDATE_ID

    def test_does_not_return_204(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("candidate.app.delete_candidate", return_value=CANDIDATE_ID):
            event = _event(
                "DELETE", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "DELETE /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] != 204

    def test_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("candidate.app.delete_candidate", side_effect=ForbiddenError("not authorized")):
            event = _event(
                "DELETE", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "DELETE /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "FORBIDDEN"

    def test_candidate_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("candidate.app.delete_candidate", side_effect=NotFoundError("Candidate not found")):
            event = _event(
                "DELETE", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "DELETE /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404

    def test_apperror_conversion(self, mock_user, mock_cfg, mock_conn, mock_close):
        from common.errors import InternalServerError
        mock_user.return_value = _USER
        with patch("candidate.app.delete_candidate", side_effect=InternalServerError()):
            event = _event(
                "DELETE", f"/trips/{TRIP_ID}/candidates/{CANDIDATE_ID}",
                "DELETE /trips/{tripId}/candidates/{candidateId}",
                path_params={"tripId": TRIP_ID, "candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
