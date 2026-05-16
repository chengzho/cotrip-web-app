import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from common.errors import ForbiddenError, NotFoundError
from common.repositories.vote_repository import get_rankings, unvote_candidate, vote_candidate


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
CANDIDATE_ID = str(uuid.uuid4())

_TRIP_UUID = uuid.UUID(TRIP_ID)
_CANDIDATE_UUID = uuid.UUID(CANDIDATE_ID)
_USER_UUID = uuid.UUID(USER_ID)
_TS = datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
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


def _membership_row(role="member"):
    return (_TRIP_UUID, role)


def _count_cur(count):
    return _cursor(fetchone=(count,))


# ---------------------------------------------------------------------------
# vote_candidate
# ---------------------------------------------------------------------------

class TestVoteCandidate:
    def test_first_vote_success(self):
        conn = _conn(
            _cursor(fetchone=_membership_row("member")),
            _cursor(),           # INSERT ON CONFLICT DO NOTHING
            _count_cur(5),       # SELECT COUNT(*)
        )
        result = vote_candidate(conn, CANDIDATE_ID, USER_ID)
        assert result["candidate_id"] == CANDIDATE_ID
        assert result["voted"] is True
        assert result["vote_count"] == 5
        conn.commit.assert_called_once()

    def test_repeated_vote_is_idempotent(self):
        # Even if INSERT does nothing (already voted), result is success
        conn = _conn(
            _cursor(fetchone=_membership_row("member")),
            _cursor(),      # INSERT → no-op due to ON CONFLICT
            _count_cur(5),
        )
        result = vote_candidate(conn, CANDIDATE_ID, USER_ID)
        assert result["voted"] is True
        assert result["vote_count"] == 5

    def test_candidate_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Candidate not found"):
            vote_candidate(conn, CANDIDATE_ID, USER_ID)

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(_TRIP_UUID, None)))
        with pytest.raises(ForbiddenError):
            vote_candidate(conn, CANDIDATE_ID, USER_ID)

    def test_owner_can_vote(self):
        conn = _conn(
            _cursor(fetchone=_membership_row("owner")),
            _cursor(),
            _count_cur(1),
        )
        result = vote_candidate(conn, CANDIDATE_ID, USER_ID)
        assert result["voted"] is True

    def test_commit_not_called_on_error(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError):
            vote_candidate(conn, CANDIDATE_ID, USER_ID)
        conn.commit.assert_not_called()


# ---------------------------------------------------------------------------
# unvote_candidate
# ---------------------------------------------------------------------------

class TestUnvoteCandidate:
    def test_successful_vote_removal(self):
        conn = _conn(
            _cursor(fetchone=_membership_row("member")),
            _cursor(),       # DELETE
            _count_cur(4),   # SELECT COUNT(*)
        )
        result = unvote_candidate(conn, CANDIDATE_ID, USER_ID)
        assert result["candidate_id"] == CANDIDATE_ID
        assert result["voted"] is False
        assert result["vote_count"] == 4
        conn.commit.assert_called_once()

    def test_repeated_unvote_is_idempotent(self):
        # DELETE where no vote exists → 0 rows deleted, still returns success
        conn = _conn(
            _cursor(fetchone=_membership_row("member")),
            _cursor(),       # DELETE → no rows deleted
            _count_cur(0),
        )
        result = unvote_candidate(conn, CANDIDATE_ID, USER_ID)
        assert result["voted"] is False
        assert result["vote_count"] == 0

    def test_candidate_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Candidate not found"):
            unvote_candidate(conn, CANDIDATE_ID, USER_ID)

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(_TRIP_UUID, None)))
        with pytest.raises(ForbiddenError):
            unvote_candidate(conn, CANDIDATE_ID, USER_ID)

    def test_delete_is_called_with_correct_params(self):
        delete_cur = _cursor()
        conn = _conn(
            _cursor(fetchone=_membership_row("member")),
            delete_cur,
            _count_cur(0),
        )
        unvote_candidate(conn, CANDIDATE_ID, USER_ID)
        call_args = delete_cur.execute.call_args[0]
        assert "DELETE FROM candidate_votes" in call_args[0]
        assert CANDIDATE_ID in call_args[1]
        assert USER_ID in call_args[1]

    def test_commit_not_called_on_error(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError):
            unvote_candidate(conn, CANDIDATE_ID, USER_ID)
        conn.commit.assert_not_called()


# ---------------------------------------------------------------------------
# get_rankings
# ---------------------------------------------------------------------------

def _ranking_row(vote_count=7, current_user_voted=True):
    return (
        _CANDIDATE_UUID,     # 0 id
        _TRIP_UUID,          # 1 trip_id
        "attraction",        # 2 category
        "Senso-ji Temple",   # 3 name
        "A classic stop",    # 4 note
        _USER_UUID,          # 5 created_by
        "Sophie",            # 6 display_name
        vote_count,          # 7 vote_count
        current_user_voted,  # 8 current_user_voted
        _TS,                 # 9 created_at
    )


class TestGetRankings:
    def test_returns_rankings_with_rank_field(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[_ranking_row(7), _ranking_row(3, False)])
        conn = _conn(membership_cur, rankings_cur)

        result = get_rankings(conn, TRIP_ID, USER_ID)
        assert len(result) == 2
        assert result[0]["rank"] == 1
        assert result[1]["rank"] == 2

    def test_ranking_fields_match_document(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[_ranking_row()])
        conn = _conn(membership_cur, rankings_cur)

        result = get_rankings(conn, TRIP_ID, USER_ID)
        item = result[0]
        assert item["candidate_id"] == CANDIDATE_ID
        assert item["trip_id"] == TRIP_ID
        assert item["category"] == "attraction"
        assert item["name"] == "Senso-ji Temple"
        assert item["note"] == "A classic stop"
        assert item["created_by"]["user_id"] == USER_ID
        assert item["created_by"]["display_name"] == "Sophie"
        assert item["vote_count"] == 7
        assert item["current_user_voted"] is True

    def test_empty_rankings_returns_empty_list(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[])
        conn = _conn(membership_cur, rankings_cur)

        result = get_rankings(conn, TRIP_ID, USER_ID)
        assert result == []

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(None,)))
        with pytest.raises(ForbiddenError):
            get_rankings(conn, TRIP_ID, USER_ID)

    def test_trip_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            get_rankings(conn, TRIP_ID, USER_ID)

    def test_category_filter_appended_to_query(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[])
        conn = _conn(membership_cur, rankings_cur)

        get_rankings(conn, TRIP_ID, USER_ID, category="attraction")
        call_args = rankings_cur.execute.call_args[0]
        assert "tc.category = %s" in call_args[0]
        assert "attraction" in call_args[1]

    def test_no_category_filter_omits_clause(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[])
        conn = _conn(membership_cur, rankings_cur)

        get_rankings(conn, TRIP_ID, USER_ID)
        call_args = rankings_cur.execute.call_args[0]
        assert "tc.category = %s" not in call_args[0]

    def test_order_by_vote_count_desc_then_created_at_asc(self):
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[])
        conn = _conn(membership_cur, rankings_cur)

        get_rankings(conn, TRIP_ID, USER_ID)
        call_args = rankings_cur.execute.call_args[0]
        assert "vote_count DESC" in call_args[0]
        assert "tc.created_at ASC" in call_args[0]

    def test_null_vote_fields_default_to_zero_and_false(self):
        row = list(_ranking_row())
        row[7] = None
        row[8] = None
        membership_cur = _cursor(fetchone=("member",))
        rankings_cur = _cursor(fetchall=[tuple(row)])
        conn = _conn(membership_cur, rankings_cur)

        result = get_rankings(conn, TRIP_ID, USER_ID)
        assert result[0]["vote_count"] == 0
        assert result[0]["current_user_voted"] is False
