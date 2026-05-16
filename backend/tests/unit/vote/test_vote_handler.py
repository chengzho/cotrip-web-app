import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from vote.app import lambda_handler


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
CANDIDATE_ID = str(uuid.uuid4())

_USER = {
    "id": USER_ID,
    "cognito_sub": "sub-1",
    "email": "alice@example.com",
    "display_name": "Alice",
}

_VOTE_RESULT = {
    "candidate_id": CANDIDATE_ID,
    "voted": True,
    "vote_count": 5,
}

_UNVOTE_RESULT = {
    "candidate_id": CANDIDATE_ID,
    "voted": False,
    "vote_count": 4,
}

_RANKING_ITEM = {
    "rank": 1,
    "candidate_id": CANDIDATE_ID,
    "trip_id": TRIP_ID,
    "category": "attraction",
    "name": "Senso-ji Temple",
    "note": "A classic stop",
    "created_by": {"user_id": USER_ID, "display_name": "Alice"},
    "vote_count": 7,
    "current_user_voted": True,
    "created_at": "2026-08-01T10:00:00+00:00",
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


@patch("vote.app.close_connection_if_needed")
@patch("vote.app.get_connection")
@patch("vote.app.get_database_config")
@patch("vote.app.resolve_or_create_user")
class TestVoteHandler:
    def test_vote_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.vote_candidate", return_value=_VOTE_RESULT):
            event = _event(
                "POST", f"/candidates/{CANDIDATE_ID}/votes",
                "POST /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["voted"] is True
        assert body["data"]["vote_count"] == 5
        assert body["data"]["candidate_id"] == CANDIDATE_ID

    def test_repeated_vote_also_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        # Idempotent: same result shape regardless of whether row was inserted or not
        with patch("vote.app.vote_candidate", return_value=_VOTE_RESULT):
            event = _event(
                "POST", f"/candidates/{CANDIDATE_ID}/votes",
                "POST /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["data"]["voted"] is True

    def test_vote_invalid_uuid_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "POST", "/candidates/not-a-uuid/votes",
            "POST /candidates/{candidateId}/votes",
            path_params={"candidateId": "not-a-uuid"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_vote_candidate_not_found_returns_404(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import NotFoundError
        with patch("vote.app.vote_candidate", side_effect=NotFoundError("Candidate not found")):
            event = _event(
                "POST", f"/candidates/{CANDIDATE_ID}/votes",
                "POST /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 404

    def test_vote_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("vote.app.vote_candidate", side_effect=ForbiddenError("not a member")):
            event = _event(
                "POST", f"/candidates/{CANDIDATE_ID}/votes",
                "POST /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "FORBIDDEN"


@patch("vote.app.close_connection_if_needed")
@patch("vote.app.get_connection")
@patch("vote.app.get_database_config")
@patch("vote.app.resolve_or_create_user")
class TestUnvoteHandler:
    def test_unvote_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.unvote_candidate", return_value=_UNVOTE_RESULT):
            event = _event(
                "DELETE", f"/candidates/{CANDIDATE_ID}/votes",
                "DELETE /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert body["data"]["voted"] is False
        assert body["data"]["vote_count"] == 4

    def test_delete_does_not_return_204(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.unvote_candidate", return_value=_UNVOTE_RESULT):
            event = _event(
                "DELETE", f"/candidates/{CANDIDATE_ID}/votes",
                "DELETE /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] != 204

    def test_repeated_unvote_also_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        repeated_result = {"candidate_id": CANDIDATE_ID, "voted": False, "vote_count": 0}
        with patch("vote.app.unvote_candidate", return_value=repeated_result):
            event = _event(
                "DELETE", f"/candidates/{CANDIDATE_ID}/votes",
                "DELETE /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["data"]["voted"] is False

    def test_unvote_invalid_uuid_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "DELETE", "/candidates/bad/votes",
            "DELETE /candidates/{candidateId}/votes",
            path_params={"candidateId": "bad"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_unvote_unexpected_error_returns_500(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.unvote_candidate", side_effect=RuntimeError("boom")):
            event = _event(
                "DELETE", f"/candidates/{CANDIDATE_ID}/votes",
                "DELETE /candidates/{candidateId}/votes",
                path_params={"candidateId": CANDIDATE_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"


@patch("vote.app.close_connection_if_needed")
@patch("vote.app.get_connection")
@patch("vote.app.get_database_config")
@patch("vote.app.resolve_or_create_user")
class TestRankingsHandler:
    def test_rankings_success_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.get_rankings", return_value=[_RANKING_ITEM]):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/rankings",
                "GET /trips/{tripId}/rankings",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["success"] is True
        assert len(body["data"]["rankings"]) == 1
        assert body["data"]["rankings"][0]["rank"] == 1

    def test_rankings_with_valid_category_filter(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.get_rankings", return_value=[]) as mock_rankings:
            event = _event(
                "GET", f"/trips/{TRIP_ID}/rankings",
                "GET /trips/{tripId}/rankings",
                path_params={"tripId": TRIP_ID},
                query_params={"category": "restaurant"},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        mock_rankings.assert_called_once()
        assert mock_rankings.call_args[1]["category"] == "restaurant"

    def test_rankings_invalid_category_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "GET", f"/trips/{TRIP_ID}/rankings",
            "GET /trips/{tripId}/rankings",
            path_params={"tripId": TRIP_ID},
            query_params={"category": "hotel"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_rankings_invalid_trip_id_returns_400(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        event = _event(
            "GET", "/trips/not-a-uuid/rankings",
            "GET /trips/{tripId}/rankings",
            path_params={"tripId": "not-a-uuid"},
        )
        resp = lambda_handler(event, {})
        assert resp["statusCode"] == 400

    def test_rankings_forbidden_returns_403(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        from common.errors import ForbiddenError
        with patch("vote.app.get_rankings", side_effect=ForbiddenError("not a member")):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/rankings",
                "GET /trips/{tripId}/rankings",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 403

    def test_rankings_empty_returns_200(self, mock_user, mock_cfg, mock_conn, mock_close):
        mock_user.return_value = _USER
        with patch("vote.app.get_rankings", return_value=[]):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/rankings",
                "GET /trips/{tripId}/rankings",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["data"]["rankings"] == []

    def test_apperror_conversion(self, mock_user, mock_cfg, mock_conn, mock_close):
        from common.errors import InternalServerError
        mock_user.return_value = _USER
        with patch("vote.app.get_rankings", side_effect=InternalServerError()):
            event = _event(
                "GET", f"/trips/{TRIP_ID}/rankings",
                "GET /trips/{tripId}/rankings",
                path_params={"tripId": TRIP_ID},
            )
            resp = lambda_handler(event, {})
        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
