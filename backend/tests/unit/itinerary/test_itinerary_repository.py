import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest

from common.errors import (
    ConflictError,
    ForbiddenError,
    ItineraryAlreadyExistsError,
    NotFoundError,
    ValidationError,
)
from common.repositories.itinerary_repository import (
    delete_itinerary_item,
    generate_itinerary,
    get_itinerary,
    update_itinerary_item,
)


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
ITEM_ID = str(uuid.uuid4())
CAND_ID = str(uuid.uuid4())

_TRIP_UUID = uuid.UUID(TRIP_ID)
_ITEM_UUID = uuid.UUID(ITEM_ID)
_CAND_UUID = uuid.UUID(CAND_ID)
_START = date(2026, 8, 20)
_END = date(2026, 8, 21)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cursor(fetchone=None, fetchall=None):
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    return cur


def _conn(*cursors):
    conn = MagicMock()
    conn.cursor.side_effect = list(cursors)
    return conn


def _trip_cur(role="member"):
    return _cursor(fetchone=(_START, _END, role))


def _count_cur(n):
    return _cursor(fetchone=(n,))


def _candidate_rows(n_attr=1, n_rest=1):
    rows = []
    for i in range(n_attr):
        rows.append((uuid.uuid4(), "attraction", f"Attraction {i}", f"Note A{i}"))
    for i in range(n_rest):
        rows.append((uuid.uuid4(), "restaurant", f"Restaurant {i}", f"Note R{i}"))
    return rows


def _item_row():
    return (
        _ITEM_UUID,   # 0 id
        _TRIP_UUID,   # 1 trip_id
        1,            # 2 day_number
        "morning",    # 3 slot
        _CAND_UUID,   # 4 candidate_id
        "attraction", # 5 category
        "Senso-ji",   # 6 title
        "historic",   # 7 note
        1,            # 8 sort_order
    )


# ---------------------------------------------------------------------------
# generate_itinerary
# ---------------------------------------------------------------------------

class TestGenerateItinerary:
    def test_successful_generation_returns_grouped_response(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=_candidate_rows()),
            _cursor(),  # INSERT
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID)
        assert result["trip_id"] == TRIP_ID
        assert len(result["days"]) >= 1
        conn.commit.assert_called_once()

    def test_day_count_computed_correctly(self):
        # _START=Aug 20, _END=Aug 21 → 2 days
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=_candidate_rows(4, 4)),
            _cursor(),
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID)
        day_numbers = [d["day_number"] for d in result["days"]]
        assert max(day_numbers) <= 2

    def test_day_date_correct_for_day_one(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=_candidate_rows(1, 0)),
            _cursor(),
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID)
        assert result["days"][0]["date"] == "2026-08-20"

    def test_category_snapshot_in_generated_items(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=[(uuid.uuid4(), "attraction", "Temple", "note")]),
            _cursor(),
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID)
        items = result["days"][0]["items"]
        assert any(i["category"] == "attraction" for i in items)

    def test_existing_no_overwrite_raises_conflict(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(3),
        )
        with pytest.raises(ItineraryAlreadyExistsError):
            generate_itinerary(conn, TRIP_ID, USER_ID, overwrite_existing=False)
        conn.commit.assert_not_called()

    def test_overwrite_true_deletes_existing_then_inserts(self):
        delete_cur = _cursor()
        conn = _conn(
            _trip_cur("member"),
            _count_cur(2),
            _cursor(fetchall=_candidate_rows()),
            delete_cur,
            _cursor(),  # INSERT
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID, overwrite_existing=True)
        assert result["trip_id"] == TRIP_ID
        conn.commit.assert_called_once()
        delete_sql = delete_cur.execute.call_args[0][0]
        assert "DELETE" in delete_sql
        assert TRIP_ID in delete_cur.execute.call_args[0][1]

    def test_overwrite_true_no_existing_does_not_delete(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=_candidate_rows()),
            _cursor(),  # INSERT only — no DELETE cursor
        )
        result = generate_itinerary(conn, TRIP_ID, USER_ID, overwrite_existing=True)
        assert result["trip_id"] == TRIP_ID

    def test_no_candidates_raises_conflict(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=[]),
        )
        with pytest.raises(ConflictError):
            generate_itinerary(conn, TRIP_ID, USER_ID)
        conn.commit.assert_not_called()

    def test_trip_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            generate_itinerary(conn, TRIP_ID, USER_ID)

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(_START, _END, None)))
        with pytest.raises(ForbiddenError):
            generate_itinerary(conn, TRIP_ID, USER_ID)

    def test_commit_not_called_on_no_candidates(self):
        conn = _conn(
            _trip_cur("member"),
            _count_cur(0),
            _cursor(fetchall=[]),
        )
        with pytest.raises(ConflictError):
            generate_itinerary(conn, TRIP_ID, USER_ID)
        conn.commit.assert_not_called()


# ---------------------------------------------------------------------------
# get_itinerary
# ---------------------------------------------------------------------------

class TestGetItinerary:
    def test_returns_grouped_days(self):
        conn = _conn(
            _trip_cur("member"),
            _cursor(fetchall=[_item_row()]),
        )
        result = get_itinerary(conn, TRIP_ID, USER_ID)
        assert result["trip_id"] == TRIP_ID
        assert len(result["days"]) == 1
        assert result["days"][0]["day_number"] == 1
        assert len(result["days"][0]["items"]) == 1

    def test_empty_itinerary_returns_empty_days_list(self):
        conn = _conn(
            _trip_cur("member"),
            _cursor(fetchall=[]),
        )
        result = get_itinerary(conn, TRIP_ID, USER_ID)
        assert result["days"] == []
        assert result["trip_id"] == TRIP_ID

    def test_item_fields_match_spec(self):
        conn = _conn(
            _trip_cur("member"),
            _cursor(fetchall=[_item_row()]),
        )
        result = get_itinerary(conn, TRIP_ID, USER_ID)
        item = result["days"][0]["items"][0]
        assert item["item_id"] == ITEM_ID
        assert item["slot"] == "morning"
        assert item["title"] == "Senso-ji"
        assert item["category"] == "attraction"
        assert item["note"] == "historic"
        assert item["sort_order"] == 1
        assert item["candidate_id"] == CAND_ID

    def test_day_date_computed_from_start_date(self):
        conn = _conn(
            _trip_cur("member"),
            _cursor(fetchall=[_item_row()]),
        )
        result = get_itinerary(conn, TRIP_ID, USER_ID)
        assert result["days"][0]["date"] == "2026-08-20"

    def test_null_candidate_id_maps_to_none(self):
        row = list(_item_row())
        row[4] = None
        conn = _conn(
            _trip_cur("member"),
            _cursor(fetchall=[tuple(row)]),
        )
        result = get_itinerary(conn, TRIP_ID, USER_ID)
        assert result["days"][0]["items"][0]["candidate_id"] is None

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(_START, _END, None)))
        with pytest.raises(ForbiddenError):
            get_itinerary(conn, TRIP_ID, USER_ID)

    def test_trip_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            get_itinerary(conn, TRIP_ID, USER_ID)


# ---------------------------------------------------------------------------
# update_itinerary_item
# ---------------------------------------------------------------------------

class TestUpdateItineraryItem:
    def test_successful_update_returns_item(self):
        updated = list(_item_row())
        updated[3] = "afternoon"
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            _cursor(fetchone=tuple(updated)),  # UPDATE RETURNING
        )
        result = update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "afternoon"})
        assert result["item_id"] == ITEM_ID
        assert result["slot"] == "afternoon"
        conn.commit.assert_called_once()

    def test_item_not_found_raises(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=None),
        )
        with pytest.raises(NotFoundError, match="Itinerary item not found"):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "afternoon"})

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(None,)))
        with pytest.raises(ForbiddenError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "afternoon"})

    def test_trip_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "afternoon"})

    def test_category_in_patch_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError, match="category cannot be updated"):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"category": "restaurant"})

    def test_no_valid_fields_in_patch_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"unknown_field": "value"})

    def test_invalid_slot_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "midnight"})

    def test_day_number_zero_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"day_number": 0})

    def test_sort_order_negative_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"sort_order": -1})

    def test_empty_title_raises_validation_error(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
        )
        with pytest.raises(ValidationError):
            update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"title": ""})

    def test_category_unchanged_after_update(self):
        updated = list(_item_row())
        updated[3] = "afternoon"
        updated[5] = "attraction"  # category stays "attraction"
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            _cursor(fetchone=tuple(updated)),
        )
        result = update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "afternoon"})
        assert result["category"] == "attraction"

    def test_note_can_be_set_to_none(self):
        updated = list(_item_row())
        updated[7] = None
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            _cursor(fetchone=tuple(updated)),
        )
        result = update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"note": None})
        assert result["note"] is None

    def test_valid_slot_evening_accepted(self):
        updated = list(_item_row())
        updated[3] = "evening"
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            _cursor(fetchone=tuple(updated)),
        )
        result = update_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID, {"slot": "evening"})
        assert result["slot"] == "evening"


# ---------------------------------------------------------------------------
# delete_itinerary_item
# ---------------------------------------------------------------------------

class TestDeleteItineraryItem:
    def test_successful_delete_returns_item_id(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            _cursor(),  # DELETE
        )
        result = delete_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID)
        assert result == ITEM_ID
        conn.commit.assert_called_once()

    def test_item_not_found_raises(self):
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=None),
        )
        with pytest.raises(NotFoundError, match="Itinerary item not found"):
            delete_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID)
        conn.commit.assert_not_called()

    def test_non_member_raises_forbidden(self):
        conn = _conn(_cursor(fetchone=(None,)))
        with pytest.raises(ForbiddenError):
            delete_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID)

    def test_trip_not_found_raises(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            delete_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID)

    def test_delete_sql_targets_correct_item(self):
        delete_cur = _cursor()
        conn = _conn(
            _cursor(fetchone=("member",)),
            _cursor(fetchone=_item_row()),
            delete_cur,
        )
        delete_itinerary_item(conn, TRIP_ID, ITEM_ID, USER_ID)
        call_args = delete_cur.execute.call_args[0]
        assert "DELETE FROM itinerary_items" in call_args[0]
        assert ITEM_ID in call_args[1]
        assert TRIP_ID in call_args[1]
