import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from common.errors import ForbiddenError, NotFoundError, ValidationError
from common.repositories.candidate_repository import (
    create_candidate,
    delete_candidate,
    list_candidates,
    update_candidate,
)


TRIP_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
OTHER_USER_ID = str(uuid.uuid4())
CANDIDATE_ID = str(uuid.uuid4())

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


def _membership_cur(role="member"):
    # Always return a row — (None,) means trip exists but user is not a member
    return _cursor(fetchone=(role,))


def _candidate_row_minimal():
    return (
        uuid.UUID(CANDIDATE_ID),
        uuid.UUID(TRIP_ID),
        uuid.UUID(USER_ID),
    )


def _enriched_row(
    vote_count=3, current_user_voted=True, category="attraction",
    meal_times=None, area_label=None,
):
    return (
        uuid.UUID(CANDIDATE_ID),  # 0 id
        uuid.UUID(TRIP_ID),        # 1 trip_id
        category,                  # 2 category
        "Tokyo Skytree",           # 3 name
        "1-1-2 Oshiage",           # 4 address
        "Nice views",              # 5 note
        "https://example.com",     # 6 source_url
        uuid.UUID(USER_ID),        # 7 created_by
        "Sophie",                  # 8 display_name
        vote_count,                # 9 vote_count
        current_user_voted,        # 10 current_user_voted
        _TS,                       # 11 created_at
        _TS,                       # 12 updated_at
        meal_times,                # 13 restaurant_meal_times
        area_label,                # 14 area_label
    )


# ---------------------------------------------------------------------------
# create_candidate
# ---------------------------------------------------------------------------

class TestCreateCandidate:
    def _insert_row(self, meal_times=None, area_label=None):
        return (
            uuid.UUID(CANDIDATE_ID),   # 0 id
            uuid.UUID(TRIP_ID),        # 1 trip_id
            "attraction",              # 2 category
            "Tokyo Skytree",           # 3 name
            "1-1-2 Oshiage",           # 4 address
            "Nice views",              # 5 note
            "https://example.com",     # 6 source_url
            _TS,                       # 7 created_at
            _TS,                       # 8 updated_at
            meal_times,                # 9 restaurant_meal_times
            area_label,                # 10 area_label
        )

    def test_success_inserts_candidate(self):
        conn = _conn(_membership_cur("member"), _cursor(fetchone=self._insert_row()))
        result = create_candidate(conn, TRIP_ID, USER_ID, "Sophie", "attraction", "Tokyo Skytree")
        assert result["candidate_id"] == CANDIDATE_ID
        assert result["trip_id"] == TRIP_ID
        assert result["category"] == "attraction"
        assert result["name"] == "Tokyo Skytree"
        assert result["vote_count"] == 0
        assert result["current_user_voted"] is False
        assert result["created_by"]["user_id"] == USER_ID
        assert result["created_by"]["display_name"] == "Sophie"
        assert result["restaurant_meal_times"] is None
        conn.commit.assert_called_once()

    def test_not_a_member_raises_forbidden(self):
        conn = _conn(_membership_cur(None))
        with pytest.raises(ForbiddenError, match="not a member"):
            create_candidate(conn, TRIP_ID, USER_ID, "Sophie", "attraction", "Name")

    def test_trip_not_found_raises_not_found(self):
        # No row returned → trip does not exist
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError, match="Trip not found"):
            create_candidate(conn, TRIP_ID, USER_ID, "Sophie", "attraction", "Name")

    def test_optional_fields_accepted(self):
        conn = _conn(_membership_cur("owner"), _cursor(fetchone=self._insert_row()))
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Good Eats",
            address="123 Main St", note="Lunch", source_url="https://example.com",
        )
        assert result["address"] == "1-1-2 Oshiage"

    def test_accommodation_category_accepted(self):
        conn = _conn(_membership_cur("member"), _cursor(fetchone=self._insert_row()))
        result = create_candidate(conn, TRIP_ID, USER_ID, "Sophie", "accommodation", "Grand Hotel")
        assert result["candidate_id"] == CANDIDATE_ID

    def test_transport_category_accepted(self):
        conn = _conn(_membership_cur("member"), _cursor(fetchone=self._insert_row()))
        result = create_candidate(conn, TRIP_ID, USER_ID, "Sophie", "transport", "Airport Shuttle")
        assert result["candidate_id"] == CANDIDATE_ID

    def test_restaurant_with_meal_times(self):
        row = self._insert_row(meal_times=["lunch", "dinner"])
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Ramen Shop",
            restaurant_meal_times=["lunch", "dinner"],
        )
        assert result["restaurant_meal_times"] == ["lunch", "dinner"]

    def test_restaurant_meal_times_any(self):
        row = self._insert_row(meal_times=["any"])
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "restaurant", "All Day Diner",
            restaurant_meal_times=["any"],
        )
        assert result["restaurant_meal_times"] == ["any"]

    def test_non_restaurant_with_meal_times_raises(self):
        conn = _conn(_membership_cur("member"))
        with pytest.raises(ValidationError, match="restaurant candidates"):
            create_candidate(
                conn, TRIP_ID, USER_ID, "Alice", "attraction", "Temple",
                restaurant_meal_times=["lunch"],
            )

    def test_invalid_meal_time_raises(self):
        conn = _conn(_membership_cur("member"))
        with pytest.raises(ValidationError):
            create_candidate(
                conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Shop",
                restaurant_meal_times=["brunch"],
            )

    def test_any_combined_with_others_raises(self):
        conn = _conn(_membership_cur("member"))
        with pytest.raises(ValidationError, match="'any' cannot be combined"):
            create_candidate(
                conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Shop",
                restaurant_meal_times=["any", "lunch"],
            )

    def test_duplicate_meal_times_normalized(self):
        row = self._insert_row(meal_times=["lunch"])
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        # duplicates are silently deduplicated before hitting the DB
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Shop",
            restaurant_meal_times=["lunch", "lunch"],
        )
        # the normalized value passed to DB was ["lunch"]; row returns ["lunch"]
        assert result["restaurant_meal_times"] == ["lunch"]

    def test_empty_meal_times_treated_as_none(self):
        row = self._insert_row(meal_times=None)
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "restaurant", "Shop",
            restaurant_meal_times=[],
        )
        assert result["restaurant_meal_times"] is None

    def test_area_label_stored_and_returned(self):
        row = self._insert_row(area_label="Kyoto Station")
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        result = create_candidate(
            conn, TRIP_ID, USER_ID, "Alice", "attraction", "Fushimi Inari",
            area_label="Kyoto Station",
        )
        assert result["area_label"] == "Kyoto Station"

    def test_area_label_none_when_not_provided(self):
        row = self._insert_row(area_label=None)
        conn = _conn(_membership_cur("member"), _cursor(fetchone=row))
        result = create_candidate(conn, TRIP_ID, USER_ID, "Alice", "attraction", "Temple")
        assert result["area_label"] is None


# ---------------------------------------------------------------------------
# list_candidates
# ---------------------------------------------------------------------------

class TestListCandidates:
    def test_returns_candidate_list(self):
        rows = [_enriched_row(vote_count=3, current_user_voted=True)]
        conn = _conn(_membership_cur("member"), _cursor(fetchall=rows))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert len(result) == 1
        assert result[0]["candidate_id"] == CANDIDATE_ID
        assert result[0]["vote_count"] == 3
        assert result[0]["current_user_voted"] is True

    def test_empty_trip_returns_empty_list(self):
        conn = _conn(_membership_cur("member"), _cursor(fetchall=[]))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result == []

    def test_non_member_raises_forbidden(self):
        conn = _conn(_membership_cur(None))
        with pytest.raises(ForbiddenError):
            list_candidates(conn, TRIP_ID, USER_ID)

    def test_trip_not_found_raises_not_found(self):
        conn = _conn(_cursor(fetchone=None))
        with pytest.raises(NotFoundError):
            list_candidates(conn, TRIP_ID, USER_ID)

    def test_category_filter_passes_to_query(self):
        list_cur = _cursor(fetchall=[])
        conn = _conn(_membership_cur("member"), list_cur)
        list_candidates(conn, TRIP_ID, USER_ID, category="attraction")
        call_args = list_cur.execute.call_args[0]
        assert "tc.category = %s" in call_args[0]
        assert "attraction" in call_args[1]

    def test_transport_filter_passes_to_query(self):
        list_cur = _cursor(fetchall=[])
        conn = _conn(_membership_cur("member"), list_cur)
        list_candidates(conn, TRIP_ID, USER_ID, category="transport")
        call_args = list_cur.execute.call_args[0]
        assert "tc.category = %s" in call_args[0]
        assert "transport" in call_args[1]

    def test_other_filter_passes_to_query(self):
        list_cur = _cursor(fetchall=[])
        conn = _conn(_membership_cur("member"), list_cur)
        list_candidates(conn, TRIP_ID, USER_ID, category="other")
        call_args = list_cur.execute.call_args[0]
        assert "tc.category = %s" in call_args[0]
        assert "other" in call_args[1]

    def test_no_category_filter_omits_clause(self):
        list_cur = _cursor(fetchall=[])
        conn = _conn(_membership_cur("member"), list_cur)
        list_candidates(conn, TRIP_ID, USER_ID)
        call_args = list_cur.execute.call_args[0]
        assert "tc.category = %s" not in call_args[0]

    def test_null_vote_fields_default_to_zero_and_false(self):
        row_with_nulls = list(_enriched_row())
        row_with_nulls[9] = None
        row_with_nulls[10] = None
        conn = _conn(_membership_cur("member"), _cursor(fetchall=[tuple(row_with_nulls)]))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result[0]["vote_count"] == 0
        assert result[0]["current_user_voted"] is False

    def test_restaurant_meal_times_returned(self):
        rows = [_enriched_row(category="restaurant", meal_times=["breakfast"])]
        conn = _conn(_membership_cur("member"), _cursor(fetchall=rows))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result[0]["restaurant_meal_times"] == ["breakfast"]

    def test_null_meal_times_returned_as_none(self):
        rows = [_enriched_row(category="restaurant", meal_times=None)]
        conn = _conn(_membership_cur("member"), _cursor(fetchall=rows))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result[0]["restaurant_meal_times"] is None

    def test_area_label_returned_in_list(self):
        rows = [_enriched_row(area_label="Shinjuku")]
        conn = _conn(_membership_cur("member"), _cursor(fetchall=rows))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result[0]["area_label"] == "Shinjuku"

    def test_null_area_label_returned_as_none(self):
        rows = [_enriched_row(area_label=None)]
        conn = _conn(_membership_cur("member"), _cursor(fetchall=rows))
        result = list_candidates(conn, TRIP_ID, USER_ID)
        assert result[0]["area_label"] is None


# ---------------------------------------------------------------------------
# update_candidate
# ---------------------------------------------------------------------------

class TestUpdateCandidate:
    def _minimal_candidate_row(self, created_by=None, category="attraction"):
        return (
            uuid.UUID(CANDIDATE_ID),
            uuid.UUID(TRIP_ID),
            uuid.UUID(created_by or USER_ID),
            category,
        )

    def test_creator_can_update(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"note": "Updated"})
        assert result["candidate_id"] == CANDIDATE_ID
        conn.commit.assert_called_once()

    def test_owner_can_update_others_candidate(self):
        membership_cur = _membership_cur("owner")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row(created_by=OTHER_USER_ID))
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"name": "New Name"})
        assert result["candidate_id"] == CANDIDATE_ID

    def test_non_creator_member_raises_forbidden(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row(created_by=OTHER_USER_ID))
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ForbiddenError, match="not authorized"):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"note": "x"})

    def test_candidate_not_found_raises(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=None)
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(NotFoundError, match="Candidate not found"):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"note": "x"})

    def test_non_member_raises_forbidden(self):
        conn = _conn(_membership_cur(None))
        with pytest.raises(ForbiddenError):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"note": "x"})

    def test_no_valid_fields_raises_validation_error(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError, match="No valid fields"):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"unknown_field": "x"})

    def test_invalid_category_raises_validation_error(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"category": "hotel"})

    def test_accommodation_category_is_valid(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"category": "accommodation"})
        assert result["candidate_id"] == CANDIDATE_ID

    def test_transport_category_is_valid(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"category": "transport"})
        assert result["candidate_id"] == CANDIDATE_ID

    def test_other_category_is_valid(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"category": "other"})
        assert result["candidate_id"] == CANDIDATE_ID

    def test_empty_name_raises_validation_error(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError):
            update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"name": "  "})

    def test_updated_field_in_sql(self):
        update_cur = _cursor(fetchone=_enriched_row())
        conn = _conn(_membership_cur("member"), _cursor(fetchone=self._minimal_candidate_row()), update_cur)

        update_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"note": "New note"})
        call_args = update_cur.execute.call_args[0]
        assert "note = %s" in call_args[0]
        assert "New note" in call_args[1]

    def test_update_meal_times_for_restaurant(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row(category="restaurant"))
        update_cur = _cursor(fetchone=_enriched_row(category="restaurant", meal_times=["lunch"]))
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(
            conn, TRIP_ID, CANDIDATE_ID, USER_ID,
            {"restaurant_meal_times": ["lunch"]},
        )
        assert result["restaurant_meal_times"] == ["lunch"]

    def test_meal_times_on_non_restaurant_existing_candidate_raises(self):
        # Patch only restaurant_meal_times, no category in patch.
        # Existing candidate is attraction — must be rejected at app layer.
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row(category="attraction"))
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError, match="restaurant candidates"):
            update_candidate(
                conn, TRIP_ID, CANDIDATE_ID, USER_ID,
                {"restaurant_meal_times": ["lunch"]},
            )

    def test_invalid_meal_time_in_update_raises(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError):
            update_candidate(
                conn, TRIP_ID, CANDIDATE_ID, USER_ID,
                {"restaurant_meal_times": ["brunch"]},
            )

    def test_any_combined_in_update_raises(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError, match="'any' cannot be combined"):
            update_candidate(
                conn, TRIP_ID, CANDIDATE_ID, USER_ID,
                {"restaurant_meal_times": ["any", "dinner"]},
            )

    def test_changing_category_away_from_restaurant_clears_meal_times(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row(category="attraction", meal_times=None))
        conn = _conn(membership_cur, candidate_cur, update_cur)

        update_candidate(
            conn, TRIP_ID, CANDIDATE_ID, USER_ID,
            {"category": "attraction"},
        )
        # Verify SQL includes restaurant_meal_times = NULL
        call_args = update_cur.execute.call_args[0]
        assert "restaurant_meal_times = %s" in call_args[0]
        # None should appear in the params
        assert None in call_args[1]

    def test_meal_times_for_non_restaurant_category_in_same_patch_raises(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        conn = _conn(membership_cur, candidate_cur)

        with pytest.raises(ValidationError, match="restaurant candidates"):
            update_candidate(
                conn, TRIP_ID, CANDIDATE_ID, USER_ID,
                {"category": "attraction", "restaurant_meal_times": ["lunch"]},
            )

    def test_update_area_label(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row(area_label="Osaka Castle"))
        conn = _conn(membership_cur, candidate_cur, update_cur)

        result = update_candidate(
            conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"area_label": "Osaka Castle"}
        )
        assert result["area_label"] == "Osaka Castle"

    def test_area_label_whitespace_normalized(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row(area_label="Osaka Castle"))
        conn = _conn(membership_cur, candidate_cur, update_cur)

        update_candidate(
            conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"area_label": "  Osaka Castle  "}
        )
        call_args = update_cur.execute.call_args[0]
        assert "Osaka Castle" in call_args[1]

    def test_area_label_empty_string_becomes_null(self):
        membership_cur = _membership_cur("member")
        candidate_cur = _cursor(fetchone=self._minimal_candidate_row())
        update_cur = _cursor(fetchone=_enriched_row(area_label=None))
        conn = _conn(membership_cur, candidate_cur, update_cur)

        update_candidate(
            conn, TRIP_ID, CANDIDATE_ID, USER_ID, {"area_label": "  "}
        )
        call_args = update_cur.execute.call_args[0]
        assert None in call_args[1]


# ---------------------------------------------------------------------------
# delete_candidate
# ---------------------------------------------------------------------------

class TestDeleteCandidate:
    def _minimal_candidate_row(self, created_by=None, category="attraction"):
        return (
            uuid.UUID(CANDIDATE_ID),
            uuid.UUID(TRIP_ID),
            uuid.UUID(created_by or USER_ID),
            category,
        )

    def test_creator_can_delete(self):
        conn = _conn(
            _membership_cur("member"),
            _cursor(fetchone=self._minimal_candidate_row()),
            _cursor(),
        )
        result = delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)
        assert result == CANDIDATE_ID
        conn.commit.assert_called_once()

    def test_owner_can_delete_others_candidate(self):
        conn = _conn(
            _membership_cur("owner"),
            _cursor(fetchone=self._minimal_candidate_row(created_by=OTHER_USER_ID)),
            _cursor(),
        )
        result = delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)
        assert result == CANDIDATE_ID

    def test_non_creator_member_raises_forbidden(self):
        conn = _conn(
            _membership_cur("member"),
            _cursor(fetchone=self._minimal_candidate_row(created_by=OTHER_USER_ID)),
        )
        with pytest.raises(ForbiddenError, match="not authorized"):
            delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)

    def test_candidate_not_found_raises(self):
        conn = _conn(
            _membership_cur("member"),
            _cursor(fetchone=None),
        )
        with pytest.raises(NotFoundError, match="Candidate not found"):
            delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)

    def test_non_member_raises_forbidden(self):
        conn = _conn(_membership_cur(None))
        with pytest.raises(ForbiddenError):
            delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)

    def test_commit_not_called_on_error(self):
        conn = _conn(_membership_cur(None))
        with pytest.raises(ForbiddenError):
            delete_candidate(conn, TRIP_ID, CANDIDATE_ID, USER_ID)
        conn.commit.assert_not_called()
