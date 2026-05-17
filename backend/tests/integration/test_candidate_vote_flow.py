"""
Integration Flow B — Candidate + Vote + Rankings

Tests run through real Lambda handler entrypoints against a live PostgreSQL DB.
Requires COTRIP_RUN_INTEGRATION=1 (enforced in conftest.py).
"""

from candidate.app import lambda_handler as candidate_handler
from trip_group.app import lambda_handler as trip_handler
from vote.app import lambda_handler as vote_handler

from .helpers import assert_err, assert_ok, make_event

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ALICE_SUB = "sub-alice-candidates"
_ALICE_EMAIL = "alice@cotrip-candidates.example"

_BOB_SUB = "sub-bob-candidates"
_BOB_EMAIL = "bob@cotrip-candidates.example"

_TRIP_BODY = {
    "title": "Candidate Flow Trip",
    "destination": "Kyoto, Japan",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_trip(sub=_ALICE_SUB, email=_ALICE_EMAIL):
    resp = trip_handler(make_event(
        "POST", "/trips", "POST /trips",
        sub=sub, email=email,
        body=_TRIP_BODY,
    ), {})
    return assert_ok(resp, 201)["trip_id"]


def _add_member(trip_id, sub, email):
    """Join a second user into the trip via direct DB insert is not available —
    instead we call create_invite + join."""
    from invite.app import lambda_handler as invite_handler
    invite_resp = invite_handler(make_event(
        "POST", f"/trips/{trip_id}/invites",
        "POST /trips/{tripId}/invites",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id},
        body={},
    ), {})
    invite_url = assert_ok(invite_resp, 201)["invite"]["invite_url"]
    raw_token = invite_url.split("/join/")[1]
    join_resp = invite_handler(make_event(
        "POST", f"/invites/{raw_token}/join",
        "POST /invites/{inviteToken}/join",
        sub=sub, email=email,
        path_params={"inviteToken": raw_token},
    ), {})
    assert_ok(join_resp, 200)


def _create_candidate(trip_id, category, name, sub=_ALICE_SUB, email=_ALICE_EMAIL, note=None):
    body = {"category": category, "name": name}
    if note:
        body["note"] = note
    resp = candidate_handler(make_event(
        "POST", f"/trips/{trip_id}/candidates",
        "POST /trips/{tripId}/candidates",
        sub=sub, email=email,
        path_params={"tripId": trip_id},
        body=body,
    ), {})
    return assert_ok(resp, 201)["candidate"]


def _vote(candidate_id, sub=_ALICE_SUB, email=_ALICE_EMAIL):
    return vote_handler(make_event(
        "POST", f"/candidates/{candidate_id}/votes",
        "POST /candidates/{candidateId}/votes",
        sub=sub, email=email,
        path_params={"candidateId": candidate_id},
    ), {})


def _unvote(candidate_id, sub=_ALICE_SUB, email=_ALICE_EMAIL):
    return vote_handler(make_event(
        "DELETE", f"/candidates/{candidate_id}/votes",
        "DELETE /candidates/{candidateId}/votes",
        sub=sub, email=email,
        path_params={"candidateId": candidate_id},
    ), {})


def _rankings(trip_id, sub=_ALICE_SUB, email=_ALICE_EMAIL, category=None):
    qp = {"category": category} if category else None
    return vote_handler(make_event(
        "GET", f"/trips/{trip_id}/rankings",
        "GET /trips/{tripId}/rankings",
        sub=sub, email=email,
        path_params={"tripId": trip_id},
        query_params=qp,
    ), {})


# ---------------------------------------------------------------------------
# Tests — Create candidates
# ---------------------------------------------------------------------------

class TestCreateCandidates:
    def test_create_attraction_returns_201(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Kinkaku-ji")
        assert cand["category"] == "attraction"
        assert cand["name"] == "Kinkaku-ji"
        assert cand["vote_count"] == 0

    def test_create_restaurant_returns_201(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "restaurant", "Nishiki Market")
        assert cand["category"] == "restaurant"

    def test_category_value_persists_in_db(self, pg_conn):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Gion District")

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT category, name FROM trip_candidates WHERE id = %s",
                (cand["candidate_id"],),
            )
            row = cur.fetchone()
        assert row is not None
        assert row[0] == "attraction"
        assert row[1] == "Gion District"

    def test_invalid_category_returns_400(self):
        trip_id = _create_trip()
        resp = candidate_handler(make_event(
            "POST", f"/trips/{trip_id}/candidates",
            "POST /trips/{tripId}/candidates",
            sub=_ALICE_SUB, email=_ALICE_EMAIL,
            path_params={"tripId": trip_id},
            body={"category": "hotel", "name": "Hilton"},
        ), {})
        assert_err(resp, 400, "VALIDATION_ERROR")

    def test_non_member_cannot_create_candidate(self):
        trip_id = _create_trip()
        resp = candidate_handler(make_event(
            "POST", f"/trips/{trip_id}/candidates",
            "POST /trips/{tripId}/candidates",
            sub=_BOB_SUB, email=_BOB_EMAIL,
            path_params={"tripId": trip_id},
            body={"category": "attraction", "name": "Nijo Castle"},
        ), {})
        assert_err(resp, 403, "FORBIDDEN")


# ---------------------------------------------------------------------------
# Tests — Vote (idempotent)
# ---------------------------------------------------------------------------

class TestVote:
    def test_first_vote_succeeds(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Arashiyama")
        resp = _vote(cand["candidate_id"])
        data = assert_ok(resp, 200)
        assert data["voted"] is True
        assert data["vote_count"] == 1

    def test_repeated_vote_is_idempotent(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Fushimi Inari")
        _vote(cand["candidate_id"])
        resp = _vote(cand["candidate_id"])
        data = assert_ok(resp, 200)
        assert data["voted"] is True
        assert data["vote_count"] == 1

    def test_vote_count_in_db(self, pg_conn):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Philosopher's Path")
        _vote(cand["candidate_id"])

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM candidate_votes WHERE candidate_id = %s",
                (cand["candidate_id"],),
            )
            count = cur.fetchone()[0]
        assert count == 1

    def test_two_users_can_both_vote(self):
        trip_id = _create_trip()
        _add_member(trip_id, _BOB_SUB, _BOB_EMAIL)
        cand = _create_candidate(trip_id, "attraction", "Nijo Castle")
        assert_ok(_vote(cand["candidate_id"], _ALICE_SUB, _ALICE_EMAIL), 200)
        resp = _vote(cand["candidate_id"], _BOB_SUB, _BOB_EMAIL)
        data = assert_ok(resp, 200)
        assert data["vote_count"] == 2


# ---------------------------------------------------------------------------
# Tests — Rankings
# ---------------------------------------------------------------------------

class TestRankings:
    def test_rankings_returns_all_candidates(self):
        trip_id = _create_trip()
        _create_candidate(trip_id, "attraction", "Kinkaku-ji")
        _create_candidate(trip_id, "restaurant", "Noodle House")
        data = assert_ok(_rankings(trip_id), 200)
        assert len(data["rankings"]) == 2

    def test_more_voted_candidate_ranks_first(self):
        trip_id = _create_trip()
        _add_member(trip_id, _BOB_SUB, _BOB_EMAIL)
        low = _create_candidate(trip_id, "attraction", "Low Votes Place")
        high = _create_candidate(trip_id, "attraction", "High Votes Place")

        # high gets 2 votes, low gets 1
        _vote(high["candidate_id"], _ALICE_SUB, _ALICE_EMAIL)
        _vote(high["candidate_id"], _BOB_SUB, _BOB_EMAIL)
        _vote(low["candidate_id"], _ALICE_SUB, _ALICE_EMAIL)

        data = assert_ok(_rankings(trip_id), 200)
        rankings = data["rankings"]
        assert rankings[0]["candidate_id"] == high["candidate_id"]
        assert rankings[0]["rank"] == 1
        assert rankings[0]["vote_count"] == 2
        assert rankings[1]["candidate_id"] == low["candidate_id"]
        assert rankings[1]["vote_count"] == 1

    def test_zero_vote_candidates_ordered_by_created_at_asc(self):
        trip_id = _create_trip()
        first = _create_candidate(trip_id, "attraction", "First Created")
        second = _create_candidate(trip_id, "attraction", "Second Created")

        data = assert_ok(_rankings(trip_id), 200)
        rankings = data["rankings"]
        ids = [r["candidate_id"] for r in rankings]
        assert ids.index(first["candidate_id"]) < ids.index(second["candidate_id"])

    def test_category_filter_attraction(self):
        trip_id = _create_trip()
        _create_candidate(trip_id, "attraction", "Temple A")
        _create_candidate(trip_id, "restaurant", "Ramen B")

        data = assert_ok(_rankings(trip_id, category="attraction"), 200)
        assert all(r["category"] == "attraction" for r in data["rankings"])
        assert len(data["rankings"]) == 1

    def test_category_filter_restaurant(self):
        trip_id = _create_trip()
        _create_candidate(trip_id, "attraction", "Temple A")
        _create_candidate(trip_id, "restaurant", "Sushi B")
        _create_candidate(trip_id, "restaurant", "Ramen C")

        data = assert_ok(_rankings(trip_id, category="restaurant"), 200)
        assert len(data["rankings"]) == 2
        assert all(r["category"] == "restaurant" for r in data["rankings"])

    def test_current_user_voted_flag(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Voted Place")
        _vote(cand["candidate_id"], _ALICE_SUB, _ALICE_EMAIL)

        data = assert_ok(_rankings(trip_id, _ALICE_SUB, _ALICE_EMAIL), 200)
        match = next(r for r in data["rankings"] if r["candidate_id"] == cand["candidate_id"])
        assert match["current_user_voted"] is True


# ---------------------------------------------------------------------------
# Tests — Unvote (idempotent)
# ---------------------------------------------------------------------------

class TestUnvote:
    def test_unvote_after_vote_returns_zero(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Bamboo Grove")
        _vote(cand["candidate_id"])
        resp = _unvote(cand["candidate_id"])
        data = assert_ok(resp, 200)
        assert data["voted"] is False
        assert data["vote_count"] == 0

    def test_repeated_unvote_is_idempotent(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Peaceful Garden")
        _vote(cand["candidate_id"])
        _unvote(cand["candidate_id"])
        resp = _unvote(cand["candidate_id"])
        data = assert_ok(resp, 200)
        assert data["voted"] is False
        assert data["vote_count"] == 0

    def test_unvote_without_prior_vote_is_idempotent(self):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Never Voted")
        resp = _unvote(cand["candidate_id"])
        data = assert_ok(resp, 200)
        assert data["vote_count"] == 0

    def test_unvote_removes_row_from_db(self, pg_conn):
        trip_id = _create_trip()
        cand = _create_candidate(trip_id, "attraction", "Temp Vote")
        _vote(cand["candidate_id"])
        _unvote(cand["candidate_id"])

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM candidate_votes WHERE candidate_id = %s",
                (cand["candidate_id"],),
            )
            count = cur.fetchone()[0]
        assert count == 0
