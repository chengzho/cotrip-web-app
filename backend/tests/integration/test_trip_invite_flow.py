"""
Integration Flow A — Trip + Invite + Join

Tests run through real Lambda handler entrypoints against a live PostgreSQL DB.
Requires COTRIP_RUN_INTEGRATION=1 (enforced in conftest.py).
"""

from invite.app import lambda_handler as invite_handler
from trip_group.app import lambda_handler as trip_handler

from .helpers import assert_err, assert_ok, make_event

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ALICE_SUB = "sub-alice-integration"
_ALICE_EMAIL = "alice@cotrip-test.example"

_BOB_SUB = "sub-bob-integration"
_BOB_EMAIL = "bob@cotrip-test.example"

_TRIP_BODY = {
    "title": "Tokyo Adventure",
    "destination": "Tokyo, Japan",
    "start_date": "2026-08-20",
    "end_date": "2026-08-22",
    "description": "Integration test trip",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_trip(sub=_ALICE_SUB, email=_ALICE_EMAIL, body=None):
    return trip_handler(make_event(
        "POST", "/trips", "POST /trips",
        sub=sub, email=email,
        body=body or _TRIP_BODY,
    ), {})


def _create_invite(trip_id, sub=_ALICE_SUB, email=_ALICE_EMAIL, body=None):
    return invite_handler(make_event(
        "POST", f"/trips/{trip_id}/invites",
        "POST /trips/{tripId}/invites",
        sub=sub, email=email,
        path_params={"tripId": trip_id},
        body=body or {},
    ), {})


def _preview_invite(raw_token):
    return invite_handler(make_event(
        "GET", f"/invites/{raw_token}",
        "GET /invites/{inviteToken}",
        path_params={"inviteToken": raw_token},
        public=True,
    ), {})


def _join_invite(raw_token, sub=_BOB_SUB, email=_BOB_EMAIL):
    return invite_handler(make_event(
        "POST", f"/invites/{raw_token}/join",
        "POST /invites/{inviteToken}/join",
        sub=sub, email=email,
        path_params={"inviteToken": raw_token},
    ), {})


def _list_members(trip_id, sub=_ALICE_SUB, email=_ALICE_EMAIL):
    return trip_handler(make_event(
        "GET", f"/trips/{trip_id}/members",
        "GET /trips/{tripId}/members",
        sub=sub, email=email,
        path_params={"tripId": trip_id},
    ), {})


def _raw_token_from_url(invite_url: str) -> str:
    return invite_url.split("/join/")[1]


# ---------------------------------------------------------------------------
# Tests — Create trip
# ---------------------------------------------------------------------------

class TestCreateTrip:
    def test_create_trip_returns_201(self):
        resp = _create_trip()
        data = assert_ok(resp, 201)
        assert "trip_id" in data
        assert data["title"] == "Tokyo Adventure"
        assert data["destination"] == "Tokyo, Japan"
        assert data["role"] == "owner"

    def test_trip_row_exists_in_db(self, pg_conn):
        resp = _create_trip()
        trip_id = assert_ok(resp, 201)["trip_id"]

        with pg_conn.cursor() as cur:
            cur.execute("SELECT title, destination FROM trips WHERE id = %s", (trip_id,))
            row = cur.fetchone()
        assert row is not None
        assert row[0] == "Tokyo Adventure"
        assert row[1] == "Tokyo, Japan"

    def test_owner_membership_created(self, pg_conn):
        resp = _create_trip()
        trip_id = assert_ok(resp, 201)["trip_id"]

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT role FROM trip_members WHERE trip_id = %s", (trip_id,)
            )
            rows = cur.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "owner"

    def test_invalid_date_range_returns_400(self):
        resp = _create_trip(body={**_TRIP_BODY, "start_date": "2026-08-25", "end_date": "2026-08-20"})
        assert_err(resp, 400, "VALIDATION_ERROR")


# ---------------------------------------------------------------------------
# Tests — Create invite
# ---------------------------------------------------------------------------

class TestCreateInvite:
    def test_create_invite_returns_201(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        resp = _create_invite(trip_id)
        data = assert_ok(resp, 201)
        assert "invite" in data
        assert "invite_url" in data["invite"]

    def test_invite_url_contains_join_path(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        data = assert_ok(_create_invite(trip_id), 201)
        assert "/join/" in data["invite"]["invite_url"]

    def test_db_stores_token_hash_not_raw_token(self, pg_conn):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        data = assert_ok(_create_invite(trip_id), 201)
        raw_token = _raw_token_from_url(data["invite"]["invite_url"])

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT token_hash FROM trip_invites WHERE trip_id = %s", (trip_id,)
            )
            row = cur.fetchone()
        assert row is not None
        assert row[0] != raw_token, "Raw token must not be stored — only the hash"
        assert len(row[0]) > 0

    def test_non_member_cannot_create_invite(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        resp = _create_invite(trip_id, sub=_BOB_SUB, email=_BOB_EMAIL)
        assert_err(resp, 403, "FORBIDDEN")


# ---------------------------------------------------------------------------
# Tests — Preview invite (public)
# ---------------------------------------------------------------------------

class TestPreviewInvite:
    def test_preview_returns_200(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        resp = _preview_invite(raw_token)
        assert_ok(resp, 200)

    def test_preview_contains_trip_fields(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        data = assert_ok(_preview_invite(raw_token), 200)
        preview = data["invite_preview"]
        assert preview["trip_title"] == "Tokyo Adventure"
        assert preview["destination"] == "Tokyo, Japan"
        assert preview["start_date"] is not None
        assert preview["end_date"] is not None
        assert "invited_by_display_name" in preview

    def test_invalid_token_returns_404(self):
        assert_err(_preview_invite("no-such-token-xyz"), 404, "NOT_FOUND")


# ---------------------------------------------------------------------------
# Tests — Join invite
# ---------------------------------------------------------------------------

class TestJoinInvite:
    def test_join_returns_200_with_member_role(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        data = assert_ok(_join_invite(raw_token), 200)
        assert data["trip"]["current_user_role"] == "member"

    def test_join_creates_member_row(self, pg_conn):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        _join_invite(raw_token)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT role FROM trip_members WHERE trip_id = %s ORDER BY joined_at",
                (trip_id,),
            )
            rows = cur.fetchall()
        assert len(rows) == 2
        assert {r[0] for r in rows} == {"owner", "member"}

    def test_join_increments_used_count(self, pg_conn):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])

        with pg_conn.cursor() as cur:
            cur.execute("SELECT used_count FROM trip_invites WHERE trip_id = %s", (trip_id,))
            before = cur.fetchone()[0]

        _join_invite(raw_token)

        with pg_conn.cursor() as cur:
            cur.execute("SELECT used_count FROM trip_invites WHERE trip_id = %s", (trip_id,))
            after = cur.fetchone()[0]

        assert after == before + 1

    def test_owner_cannot_join_own_trip(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        resp = _join_invite(raw_token, sub=_ALICE_SUB, email=_ALICE_EMAIL)
        assert_err(resp, 409, "ALREADY_EXISTS")

    def test_bob_cannot_join_twice(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        assert_ok(_join_invite(raw_token), 200)
        resp = _join_invite(raw_token, sub=_BOB_SUB, email=_BOB_EMAIL)
        assert_err(resp, 409, "ALREADY_EXISTS")


# ---------------------------------------------------------------------------
# Tests — List members
# ---------------------------------------------------------------------------

class TestListMembers:
    def test_list_members_shows_owner_only_before_join(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        data = assert_ok(_list_members(trip_id), 200)
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "owner"

    def test_list_members_shows_both_after_join(self):
        trip_id = assert_ok(_create_trip(), 201)["trip_id"]
        raw_token = _raw_token_from_url(assert_ok(_create_invite(trip_id), 201)["invite"]["invite_url"])
        _join_invite(raw_token)

        data = assert_ok(_list_members(trip_id), 200)
        members = data["members"]
        assert len(members) == 2
        assert {m["role"] for m in members} == {"owner", "member"}
        emails = {m["email"] for m in members}
        assert _ALICE_EMAIL in emails
        assert _BOB_EMAIL in emails
