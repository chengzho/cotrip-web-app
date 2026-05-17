import uuid

import pytest

from common.repositories.itinerary_repository import build_itinerary_rows


TRIP_ID = str(uuid.uuid4())


def _attr(name="Temple A", note=None):
    return {"id": str(uuid.uuid4()), "category": "attraction", "name": name, "note": note}


def _rest(name="Restaurant A", note=None):
    return {"id": str(uuid.uuid4()), "category": "restaurant", "name": name, "note": note}


class TestBuildItineraryRows:
    def test_single_day_all_four_slots(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr("A1"), _attr("A2")], [_rest("R1"), _rest("R2")])
        assert len(rows) == 4
        assert [r["slot"] for r in rows] == ["morning", "lunch", "afternoon", "dinner"]

    def test_category_snapshot_copied_from_candidate(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr("Temple")], [_rest("Noodle")])
        morning = next(r for r in rows if r["slot"] == "morning")
        lunch = next(r for r in rows if r["slot"] == "lunch")
        assert morning["category"] == "attraction"
        assert morning["title"] == "Temple"
        assert lunch["category"] == "restaurant"
        assert lunch["title"] == "Noodle"

    def test_exhausted_attractions_skips_those_slots(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr()], [_rest(), _rest()])
        slots = [r["slot"] for r in rows]
        assert "morning" in slots
        assert "lunch" in slots
        assert "dinner" in slots
        assert "afternoon" not in slots

    def test_exhausted_restaurants_skips_those_slots(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [_rest()])
        slots = [r["slot"] for r in rows]
        assert "morning" in slots
        assert "afternoon" in slots
        assert "lunch" in slots
        assert "dinner" not in slots

    def test_sort_order_resets_per_day(self):
        attrs = [_attr(f"A{i}") for i in range(4)]
        rests = [_rest(f"R{i}") for i in range(4)]
        rows = build_itinerary_rows(TRIP_ID, 2, attrs, rests)
        day1 = [r for r in rows if r["day_number"] == 1]
        day2 = [r for r in rows if r["day_number"] == 2]
        assert [r["sort_order"] for r in day1] == list(range(1, len(day1) + 1))
        assert [r["sort_order"] for r in day2] == list(range(1, len(day2) + 1))

    def test_two_days_distributes_candidates_across_days(self):
        attrs = [_attr(f"A{i}") for i in range(4)]
        rests = [_rest(f"R{i}") for i in range(4)]
        rows = build_itinerary_rows(TRIP_ID, 2, attrs, rests)
        day1 = [r for r in rows if r["day_number"] == 1]
        day2 = [r for r in rows if r["day_number"] == 2]
        assert len(day1) == 4
        assert len(day2) == 4

    def test_empty_candidates_returns_empty_list(self):
        assert build_itinerary_rows(TRIP_ID, 3, [], []) == []

    def test_trip_id_preserved_in_every_row(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr()], [_rest()])
        assert all(r["trip_id"] == TRIP_ID for r in rows)

    def test_each_row_has_unique_id(self):
        attrs = [_attr(f"A{i}") for i in range(4)]
        rests = [_rest(f"R{i}") for i in range(4)]
        rows = build_itinerary_rows(TRIP_ID, 2, attrs, rests)
        ids = [r["id"] for r in rows]
        assert len(ids) == len(set(ids))

    def test_note_copied_from_candidate(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr("Temple", note="Very old")], [])
        assert rows[0]["note"] == "Very old"

    def test_none_note_preserved(self):
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr("Temple", note=None)], [])
        assert rows[0]["note"] is None

    def test_candidates_consumed_in_order(self):
        a1, a2 = _attr("First"), _attr("Second")
        rows = build_itinerary_rows(TRIP_ID, 1, [a1, a2], [])
        morning = next(r for r in rows if r["slot"] == "morning")
        afternoon = next(r for r in rows if r["slot"] == "afternoon")
        assert morning["title"] == "First"
        assert afternoon["title"] == "Second"
