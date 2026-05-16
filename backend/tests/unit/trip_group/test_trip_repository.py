import uuid
from unittest.mock import MagicMock, call, patch

import pytest

from common.errors import ForbiddenError, NotFoundError, ValidationError
from common.repositories.trip_repository import (
    create_trip,
    get_trip_detail,
    list_members,
    list_trips,
    update_trip,
)


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())


def _cursor(fetchone=None, fetchall=None):
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    return cur


def _conn_with_cursors(*cursors):
    conn = MagicMock()
    conn.cursor.side_effect = list(cursors)
    return conn


# ---------------------------------------------------------------------------
# create_trip
# ---------------------------------------------------------------------------

class TestCreateTrip:
    def test_returns_trip_dict_with_owner_role(self):
        tid = uuid.UUID(TRIP_ID)
        row = (tid, "Beach Getaway", "Maui", "2025-06-01", "2025-06-10", "Sun & sand", "2025-01-01", "2025-01-01")
        cur = _cursor(fetchone=row)
        conn = _conn_with_cursors(cur)
        result = create_trip(conn, USER_ID, "Beach Getaway", "Maui", "2025-06-01", "2025-06-10", "Sun & sand")
        assert result["title"] == "Beach Getaway"
        assert result["role"] == "owner"
        conn.commit.assert_called_once()

    def test_description_optional(self):
        tid = uuid.UUID(TRIP_ID)
        row = (tid, "Trip", "Tokyo", "2025-08-01", "2025-08-07", None, "2025-01-01", "2025-01-01")
        cur = _cursor(fetchone=row)
        conn = _conn_with_cursors(cur)
        result = create_trip(conn, USER_ID, "Trip", "Tokyo", "2025-08-01", "2025-08-07")
        assert result["description"] is None


# ---------------------------------------------------------------------------
# list_trips
# ---------------------------------------------------------------------------

class TestListTrips:
    def _row(self, scope="upcoming"):
        tid = uuid.UUID(TRIP_ID)
        return (tid, "A Trip", "Paris", "2025-07-01", "2025-07-10", "owner", 2, 3, 5)

    def test_returns_list(self):
        cur = _cursor(fetchall=[self._row()])
        conn = _conn_with_cursors(cur)
        result = list_trips(conn, USER_ID, scope="upcoming")
        assert len(result) == 1
        assert result[0]["title"] == "A Trip"

    def test_invalid_scope_raises(self):
        conn = MagicMock()
        with pytest.raises(ValidationError, match="scope must be"):
            list_trips(conn, USER_ID, scope="invalid")

    def test_empty_list_returns_empty(self):
        cur = _cursor(fetchall=[])
        conn = _conn_with_cursors(cur)
        result = list_trips(conn, USER_ID, scope="past")
        assert result == []

    def test_all_scope_accepted(self):
        cur = _cursor(fetchall=[])
        conn = _conn_with_cursors(cur)
        result = list_trips(conn, USER_ID, scope="all")
        assert result == []


# ---------------------------------------------------------------------------
# get_trip_detail
# ---------------------------------------------------------------------------

class TestGetTripDetail:
    def _membership_row(self, role="member"):
        tid = uuid.UUID(TRIP_ID)
        uid = uuid.UUID(USER_ID)
        return (tid, "Trip", "Rome", "2025-09-01", "2025-09-07", "desc", uid, "2025-01-01", "2025-01-01", role)

    def _counts_row(self):
        return (3, 5, 10, 4)

    def test_returns_trip_detail(self):
        cur1 = _cursor(fetchone=self._membership_row())
        cur2 = _cursor(fetchone=self._counts_row())
        conn = _conn_with_cursors(cur1, cur2)
        result = get_trip_detail(conn, TRIP_ID, USER_ID)
        assert result["title"] == "Trip"
        assert result["current_user_role"] == "member"
        assert result["summary"]["member_count"] == 3

    def test_raises_not_found_when_trip_missing(self):
        cur1 = _cursor(fetchone=None)
        conn = _conn_with_cursors(cur1)
        with pytest.raises(NotFoundError):
            get_trip_detail(conn, TRIP_ID, USER_ID)

    def test_raises_forbidden_when_not_member(self):
        cur1 = _cursor(fetchone=self._membership_row(role=None))
        conn = _conn_with_cursors(cur1)
        with pytest.raises(ForbiddenError):
            get_trip_detail(conn, TRIP_ID, USER_ID)


# ---------------------------------------------------------------------------
# update_trip
# ---------------------------------------------------------------------------

class TestUpdateTrip:
    def _membership_row(self, role="owner"):
        tid = uuid.UUID(TRIP_ID)
        uid = uuid.UUID(USER_ID)
        return (tid, "Old Title", "Old Dest", "2025-06-01", "2025-06-10", "desc", uid, "2025-01-01", "2025-01-01", role)

    def _update_row(self):
        tid = uuid.UUID(TRIP_ID)
        return (tid, "New Title", "New Dest", "2025-06-01", "2025-06-10", "desc", "2025-01-02")

    def test_updates_title(self):
        cur1 = _cursor(fetchone=self._membership_row())
        cur2 = _cursor(fetchone=self._update_row())
        conn = _conn_with_cursors(cur1, cur2)
        result = update_trip(conn, TRIP_ID, USER_ID, {"title": "New Title"})
        assert result["title"] == "New Title"
        conn.commit.assert_called_once()

    def test_raises_validation_when_empty_patch(self):
        conn = MagicMock()
        with pytest.raises(ValidationError):
            update_trip(conn, TRIP_ID, USER_ID, {})

    def test_raises_forbidden_when_not_owner(self):
        cur1 = _cursor(fetchone=self._membership_row(role="member"))
        conn = _conn_with_cursors(cur1)
        with pytest.raises(ForbiddenError, match="owner"):
            update_trip(conn, TRIP_ID, USER_ID, {"title": "X"})

    def test_raises_not_found_when_trip_missing(self):
        cur1 = _cursor(fetchone=None)
        conn = _conn_with_cursors(cur1)
        with pytest.raises(NotFoundError):
            update_trip(conn, TRIP_ID, USER_ID, {"title": "X"})

    def test_raises_validation_on_bad_date(self):
        cur1 = _cursor(fetchone=self._membership_row())
        conn = _conn_with_cursors(cur1)
        with pytest.raises(ValidationError):
            update_trip(conn, TRIP_ID, USER_ID, {"start_date": "not-a-date"})

    def test_raises_validation_when_start_after_end(self):
        cur1 = _cursor(fetchone=self._membership_row())
        conn = _conn_with_cursors(cur1)
        with pytest.raises(ValidationError):
            update_trip(conn, TRIP_ID, USER_ID, {"start_date": "2025-12-31"})


# ---------------------------------------------------------------------------
# list_members
# ---------------------------------------------------------------------------

class TestListMembers:
    def _member_row(self):
        uid = uuid.UUID(USER_ID)
        return (uid, "Alice", "alice@example.com", "owner", "2025-01-01")

    def test_returns_members(self):
        cur_trip = _cursor(fetchone=(1,))
        cur_membership = _cursor(fetchone=(1,))
        cur_members = _cursor(fetchall=[self._member_row()])
        conn = _conn_with_cursors(cur_trip, cur_membership, cur_members)
        result = list_members(conn, TRIP_ID, USER_ID)
        assert len(result) == 1
        assert result[0]["display_name"] == "Alice"

    def test_raises_not_found_when_trip_missing(self):
        cur_trip = _cursor(fetchone=None)
        conn = _conn_with_cursors(cur_trip)
        with pytest.raises(NotFoundError):
            list_members(conn, TRIP_ID, USER_ID)

    def test_raises_forbidden_when_not_member(self):
        cur_trip = _cursor(fetchone=(1,))
        cur_membership = _cursor(fetchone=None)
        conn = _conn_with_cursors(cur_trip, cur_membership)
        with pytest.raises(ForbiddenError):
            list_members(conn, TRIP_ID, USER_ID)
