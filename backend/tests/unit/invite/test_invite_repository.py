import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from common.errors import (
    AlreadyExistsError,
    ForbiddenError,
    InternalServerError,
    InviteExpiredError,
    InviteRevokedError,
    InviteUsageLimitReachedError,
    NotFoundError,
)
from common.repositories.invite_repository import create_invite, join_invite, preview_invite


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
INVITE_ID = str(uuid.uuid4())
INVITER_UUID = uuid.UUID(USER_ID)
TRIP_UUID = uuid.UUID(TRIP_ID)
INVITE_UUID = uuid.UUID(INVITE_ID)

_NOW = datetime.now(timezone.utc)
_FUTURE = _NOW + timedelta(days=7)
_PAST = _NOW - timedelta(days=1)


# ---------------------------------------------------------------------------
# Cursor/connection helpers
# ---------------------------------------------------------------------------

def _cursor(fetchone=None, fetchall=None, fetchone_side_effect=None):
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    if fetchone_side_effect is not None:
        cur.fetchone.side_effect = fetchone_side_effect
    else:
        cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    return cur


def _conn(*cursors):
    conn = MagicMock()
    conn.cursor.side_effect = list(cursors)
    return conn


# ---------------------------------------------------------------------------
# create_invite
# ---------------------------------------------------------------------------

class TestCreateInvite:
    def _invite_row(self):
        return (INVITE_UUID, TRIP_UUID, _FUTURE, 20)

    @patch("common.repositories.invite_repository.generate_invite_token", return_value="raw-tok")
    @patch("common.repositories.invite_repository._build_invite_url", return_value="https://app.example.com/join/raw-tok")
    def test_success_owner(self, mock_url, mock_gen):
        owner_cur = _cursor(fetchone=("owner",))
        insert_cur = _cursor(fetchone=self._invite_row())
        conn = _conn(owner_cur, insert_cur)

        result = create_invite(conn, TRIP_ID, USER_ID)

        assert result["trip_id"] == TRIP_ID
        assert result["invite_url"] == "https://app.example.com/join/raw-tok"
        assert result["max_uses"] == 20
        conn.commit.assert_called_once()

    @patch("common.repositories.invite_repository.generate_invite_token", return_value="raw-tok")
    @patch("common.repositories.invite_repository._build_invite_url", return_value="https://app.example.com/join/raw-tok")
    def test_stores_hash_not_raw_token(self, mock_url, mock_gen):
        owner_cur = _cursor(fetchone=("owner",))
        insert_cur = _cursor(fetchone=self._invite_row())
        conn = _conn(owner_cur, insert_cur)

        create_invite(conn, TRIP_ID, USER_ID)

        # Verify that the INSERT was called with a hash, not the raw token
        insert_call_args = insert_cur.execute.call_args
        params = insert_call_args[0][1]
        raw_token = "raw-tok"
        assert raw_token not in params, "Raw token must not be stored in DB"

    def test_non_owner_member_raises_forbidden(self):
        member_cur = _cursor(fetchone=("member",))
        conn = _conn(member_cur)

        with pytest.raises(ForbiddenError, match="Only the trip owner"):
            create_invite(conn, TRIP_ID, USER_ID)

    def test_not_a_member_trip_exists_raises_forbidden(self):
        no_member_cur = _cursor(fetchone=None)
        trip_exists_cur = _cursor(fetchone=(1,))
        conn = _conn(no_member_cur, trip_exists_cur)

        with pytest.raises(ForbiddenError, match="not a member"):
            create_invite(conn, TRIP_ID, USER_ID)

    def test_not_a_member_trip_missing_raises_not_found(self):
        no_member_cur = _cursor(fetchone=None)
        no_trip_cur = _cursor(fetchone=None)
        conn = _conn(no_member_cur, no_trip_cur)

        with pytest.raises(NotFoundError, match="Trip not found"):
            create_invite(conn, TRIP_ID, USER_ID)

    @patch("common.repositories.invite_repository.generate_invite_token", return_value="raw-tok")
    def test_missing_frontend_base_url_raises_internal_error(self, mock_gen):
        owner_cur = _cursor(fetchone=("owner",))
        insert_cur = _cursor(fetchone=self._invite_row())
        conn = _conn(owner_cur, insert_cur)

        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("FRONTEND_BASE_URL", None)
            with pytest.raises(InternalServerError, match="FRONTEND_BASE_URL"):
                create_invite(conn, TRIP_ID, USER_ID)


# ---------------------------------------------------------------------------
# preview_invite
# ---------------------------------------------------------------------------

class TestPreviewInvite:
    def _active_row(self, used_count=0, max_uses=20, revoked_at=None, expires_at=None):
        return (
            expires_at or _FUTURE,
            revoked_at,
            used_count,
            max_uses,
            "Tokyo Graduation Trip",
            "Tokyo, Japan",
            "2026-08-20",
            "2026-08-25",
            "Alice",
        )

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_active_invite_returns_preview(self, mock_hash):
        cur = _cursor(fetchone=self._active_row())
        conn = _conn(cur)

        result = preview_invite(conn, "raw-tok")

        assert result["trip_title"] == "Tokyo Graduation Trip"
        assert result["destination"] == "Tokyo, Japan"
        assert result["start_date"] == "2026-08-20"
        assert result["end_date"] == "2026-08-25"
        assert result["invited_by_display_name"] == "Alice"

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_not_found_raises(self, mock_hash):
        cur = _cursor(fetchone=None)
        conn = _conn(cur)

        with pytest.raises(NotFoundError, match="Invite not found"):
            preview_invite(conn, "bad-token")

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_expired_invite_raises(self, mock_hash):
        cur = _cursor(fetchone=self._active_row(expires_at=_PAST))
        conn = _conn(cur)

        with pytest.raises(InviteExpiredError):
            preview_invite(conn, "raw-tok")

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_revoked_invite_raises(self, mock_hash):
        cur = _cursor(fetchone=self._active_row(revoked_at=_NOW))
        conn = _conn(cur)

        with pytest.raises(InviteRevokedError):
            preview_invite(conn, "raw-tok")

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_usage_limit_reached_raises(self, mock_hash):
        cur = _cursor(fetchone=self._active_row(used_count=20, max_uses=20))
        conn = _conn(cur)

        with pytest.raises(InviteUsageLimitReachedError):
            preview_invite(conn, "raw-tok")


# ---------------------------------------------------------------------------
# join_invite
# ---------------------------------------------------------------------------

class TestJoinInvite:
    def _invite_row(self, used_count=5, max_uses=20, revoked_at=None, expires_at=None):
        return (
            INVITE_UUID,
            TRIP_UUID,
            expires_at or _FUTURE,
            revoked_at,
            used_count,
            max_uses,
            "Tokyo Graduation Trip",
            "Tokyo, Japan",
        )

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_success_inserts_member_and_increments_count(self, mock_hash):
        cur = _cursor(fetchone_side_effect=[self._invite_row(), None])
        conn = _conn(cur)

        result = join_invite(conn, "raw-tok", USER_ID)

        assert result["id"] == TRIP_ID
        assert result["title"] == "Tokyo Graduation Trip"
        assert result["current_user_role"] == "member"
        conn.commit.assert_called_once()

        calls = [str(c) for c in cur.execute.call_args_list]
        assert any("INSERT INTO trip_members" in c for c in calls)
        assert any("used_count = used_count + 1" in c for c in calls)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_not_found_raises(self, mock_hash):
        cur = _cursor(fetchone=None)
        conn = _conn(cur)

        with pytest.raises(NotFoundError, match="Invite not found"):
            join_invite(conn, "bad-tok", USER_ID)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_expired_invite_raises(self, mock_hash):
        cur = _cursor(fetchone=self._invite_row(expires_at=_PAST))
        conn = _conn(cur)

        with pytest.raises(InviteExpiredError):
            join_invite(conn, "raw-tok", USER_ID)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_revoked_invite_raises(self, mock_hash):
        cur = _cursor(fetchone=self._invite_row(revoked_at=_NOW))
        conn = _conn(cur)

        with pytest.raises(InviteRevokedError):
            join_invite(conn, "raw-tok", USER_ID)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_usage_limit_reached_raises(self, mock_hash):
        cur = _cursor(fetchone=self._invite_row(used_count=20, max_uses=20))
        conn = _conn(cur)

        with pytest.raises(InviteUsageLimitReachedError):
            join_invite(conn, "raw-tok", USER_ID)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_already_member_raises_conflict(self, mock_hash):
        cur = _cursor(fetchone_side_effect=[self._invite_row(), (1,)])
        conn = _conn(cur)

        with pytest.raises(AlreadyExistsError, match="already a member"):
            join_invite(conn, "raw-tok", USER_ID)

    @patch("common.repositories.invite_repository.hash_invite_token", return_value="hash-abc")
    def test_commit_not_called_on_error(self, mock_hash):
        cur = _cursor(fetchone=None)
        conn = _conn(cur)

        with pytest.raises(NotFoundError):
            join_invite(conn, "raw-tok", USER_ID)

        conn.commit.assert_not_called()
