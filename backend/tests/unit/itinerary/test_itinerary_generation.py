import uuid

import pytest

from common.repositories.itinerary_repository import build_itinerary_rows


TRIP_ID = str(uuid.uuid4())


def _attr(name="Temple A", note=None):
    return {"id": str(uuid.uuid4()), "category": "attraction", "name": name, "note": note}


def _rest(name="Restaurant A", note=None, meal_times=None, area_label=None):
    return {
        "id": str(uuid.uuid4()),
        "category": "restaurant",
        "name": name,
        "note": note,
        "restaurant_meal_times": meal_times,
        "area_label": area_label,
    }


class TestBuildItineraryRows:
    def test_single_day_all_four_legacy_slots(self):
        # Unspecified (legacy) restaurants land in lunch/dinner only
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

    # -----------------------------------------------------------------------
    # Meal-time aware scheduling
    # -----------------------------------------------------------------------

    def test_unspecified_restaurant_eligible_for_lunch_and_dinner(self):
        r = _rest("Legacy", meal_times=None)
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r, r])
        slots = [row["slot"] for row in rows if row["category"] == "restaurant"]
        assert "lunch" in slots

    def test_lunch_only_restaurant_placed_in_lunch_slot(self):
        r = _rest("Lunch Place", meal_times=["lunch"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        assert len(restaurant_rows) == 1
        assert restaurant_rows[0]["slot"] == "lunch"

    def test_lunch_only_restaurant_not_placed_in_dinner_slot(self):
        lunch_only = _rest("Lunch Only", meal_times=["lunch"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [lunch_only])
        dinner_rows = [row for row in rows if row["slot"] == "dinner"]
        assert len(dinner_rows) == 0

    def test_dinner_only_restaurant_placed_in_dinner_slot(self):
        r = _rest("Dinner Place", meal_times=["dinner"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        assert len(restaurant_rows) == 1
        assert restaurant_rows[0]["slot"] == "dinner"

    def test_dinner_only_restaurant_not_placed_in_lunch_slot(self):
        dinner_only = _rest("Dinner Only", meal_times=["dinner"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [dinner_only])
        lunch_rows = [row for row in rows if row["slot"] == "lunch"]
        assert len(lunch_rows) == 0

    def test_breakfast_only_restaurant_not_placed_in_lunch_or_dinner(self):
        breakfast_only = _rest("Morning Stall", meal_times=["breakfast"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [breakfast_only])
        meal_slot_rows = [r for r in rows if r["slot"] in ("lunch", "dinner") and r["category"] == "restaurant"]
        assert len(meal_slot_rows) == 0

    def test_snack_only_restaurant_not_placed_in_lunch_or_dinner(self):
        snack_only = _rest("Snack Bar", meal_times=["snack"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [snack_only])
        meal_slot_rows = [r for r in rows if r["slot"] in ("lunch", "dinner") and r["category"] == "restaurant"]
        assert len(meal_slot_rows) == 0

    def test_late_night_only_restaurant_not_placed_in_lunch_or_dinner(self):
        late = _rest("Night Spot", meal_times=["late_night"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [late])
        meal_slot_rows = [r for r in rows if r["slot"] in ("lunch", "dinner") and r["category"] == "restaurant"]
        assert len(meal_slot_rows) == 0

    def test_any_restaurant_eligible_for_both_lunch_and_dinner(self):
        r = _rest("All Day", meal_times=["any"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r, _rest("Other")])
        slots = [row["slot"] for row in rows if row["category"] == "restaurant"]
        # r is consumed for lunch first; "Other" (unspecified) goes to dinner
        assert "lunch" in slots
        assert "dinner" in slots

    def test_restaurant_not_scheduled_twice_across_slots(self):
        r = _rest("Versatile", meal_times=["lunch", "dinner"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        # even though it's eligible for both, it should only appear once
        assert len(restaurant_rows) == 1

    def test_mixed_pool_breakfast_and_dinner_restaurant(self):
        breakfast = _rest("Breakfast Spot", meal_times=["breakfast"])
        dinner = _rest("Dinner Place", meal_times=["dinner"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [breakfast, dinner])
        restaurant_rows = {row["slot"]: row["title"] for row in rows if row["category"] == "restaurant"}
        assert "lunch" not in restaurant_rows
        assert restaurant_rows.get("dinner") == "Dinner Place"

    def test_lunch_and_dinner_restaurants_fill_correct_slots(self):
        r_lunch = _rest("Lunch Spot", meal_times=["lunch"])
        r_dinner = _rest("Dinner Spot", meal_times=["dinner"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r_lunch, r_dinner])
        slot_titles = {row["slot"]: row["title"] for row in rows if row["category"] == "restaurant"}
        assert slot_titles.get("lunch") == "Lunch Spot"
        assert slot_titles.get("dinner") == "Dinner Spot"

    # -----------------------------------------------------------------------
    # Full slot mapping: morning / afternoon / evening
    # -----------------------------------------------------------------------

    def test_breakfast_restaurant_placed_in_morning_slot(self):
        r = _rest("Morning Stall", meal_times=["breakfast"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        assert len(restaurant_rows) == 1
        assert restaurant_rows[0]["slot"] == "morning"

    def test_snack_restaurant_placed_in_afternoon_slot(self):
        r = _rest("Snack Bar", meal_times=["snack"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        assert len(restaurant_rows) == 1
        assert restaurant_rows[0]["slot"] == "afternoon"

    def test_late_night_restaurant_placed_in_evening_slot(self):
        r = _rest("Night Spot", meal_times=["late_night"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        restaurant_rows = [row for row in rows if row["category"] == "restaurant"]
        assert len(restaurant_rows) == 1
        assert restaurant_rows[0]["slot"] == "evening"

    def test_all_five_meal_slots_filled_in_one_day(self):
        r_breakfast = _rest("Breakfast", meal_times=["breakfast"])
        r_lunch = _rest("Lunch", meal_times=["lunch"])
        r_snack = _rest("Snack", meal_times=["snack"])
        r_dinner = _rest("Dinner", meal_times=["dinner"])
        r_late = _rest("Late Night", meal_times=["late_night"])
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr("A1"), _attr("A2")],
            [r_breakfast, r_lunch, r_snack, r_dinner, r_late],
        )
        slot_titles = {row["slot"]: row["title"] for row in rows if row["category"] == "restaurant"}
        assert slot_titles.get("morning") == "Breakfast"
        assert slot_titles.get("lunch") == "Lunch"
        assert slot_titles.get("afternoon") == "Snack"
        assert slot_titles.get("dinner") == "Dinner"
        assert slot_titles.get("evening") == "Late Night"

    def test_unspecified_restaurant_not_placed_in_morning(self):
        r = _rest("Legacy", meal_times=None)
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        morning_restaurant_rows = [
            row for row in rows if row["slot"] == "morning" and row["category"] == "restaurant"
        ]
        assert len(morning_restaurant_rows) == 0

    def test_unspecified_restaurant_not_placed_in_afternoon(self):
        r = _rest("Legacy", meal_times=None)
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        afternoon_restaurant_rows = [
            row for row in rows if row["slot"] == "afternoon" and row["category"] == "restaurant"
        ]
        assert len(afternoon_restaurant_rows) == 0

    def test_unspecified_restaurant_not_placed_in_evening(self):
        r = _rest("Legacy", meal_times=None)
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        evening_rows = [row for row in rows if row["slot"] == "evening"]
        assert len(evening_rows) == 0

    def test_any_restaurant_not_placed_in_morning_afternoon_evening(self):
        r = _rest("Any Time", meal_times=["any"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr(), _attr()], [r])
        slot = next(
            (row["slot"] for row in rows if row["category"] == "restaurant"), None
        )
        assert slot in ("lunch", "dinner")

    def test_morning_slot_has_attraction_before_restaurant(self):
        r_breakfast = _rest("Breakfast Shop", meal_times=["breakfast"])
        rows = build_itinerary_rows(TRIP_ID, 1, [_attr("Temple"), _attr()], [r_breakfast])
        morning_rows = [r for r in rows if r["slot"] == "morning"]
        assert len(morning_rows) == 2
        assert morning_rows[0]["title"] == "Temple"
        assert morning_rows[0]["sort_order"] == 1
        assert morning_rows[1]["title"] == "Breakfast Shop"
        assert morning_rows[1]["sort_order"] == 2

    # -----------------------------------------------------------------------
    # Restaurant area preference (soft, subject to meal-time hard constraint)
    # -----------------------------------------------------------------------

    def test_preferred_area_restaurant_chosen_over_non_matching(self):
        # Two dinner-eligible restaurants; day 1 prefers 台中 → 台中 restaurant picked first
        r_taichung = _rest("台中餐廳", meal_times=["dinner"], area_label="台中")
        r_other = _rest("其他餐廳", meal_times=["dinner"], area_label="台北")
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr(), _attr()],
            [r_other, r_taichung],   # r_other listed first to confirm ordering
            day_preferences={1: "台中"},
        )
        dinner_rows = [r for r in rows if r["slot"] == "dinner"]
        assert len(dinner_rows) == 1
        assert dinner_rows[0]["title"] == "台中餐廳"

    def test_fallback_to_any_eligible_when_no_preferred_area_match(self):
        # Day 1 prefers 台中 but only a 台北 dinner restaurant exists → falls back
        r_taipei = _rest("台北餐廳", meal_times=["dinner"], area_label="台北")
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr(), _attr()],
            [r_taipei],
            day_preferences={1: "台中"},
        )
        dinner_rows = [r for r in rows if r["slot"] == "dinner"]
        assert len(dinner_rows) == 1
        assert dinner_rows[0]["title"] == "台北餐廳"

    def test_area_preference_does_not_override_meal_time_hard_constraint_lunch(self):
        # Day 1 prefers 台中; 台中 restaurant is dinner-only → must NOT go into lunch
        r_taichung_dinner = _rest("台中晚餐", meal_times=["dinner"], area_label="台中")
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr(), _attr()],
            [r_taichung_dinner],
            day_preferences={1: "台中"},
        )
        lunch_rows = [r for r in rows if r["slot"] == "lunch"]
        assert len(lunch_rows) == 0

    def test_area_preference_does_not_override_meal_time_hard_constraint_dinner(self):
        # Day 1 prefers 台中; 台中 restaurant is breakfast-only → must NOT go into dinner
        r_taichung_breakfast = _rest("台中早餐", meal_times=["breakfast"], area_label="台中")
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr(), _attr()],
            [r_taichung_breakfast],
            day_preferences={1: "台中"},
        )
        dinner_rows = [r for r in rows if r["slot"] == "dinner"]
        assert len(dinner_rows) == 0

    def test_area_preference_for_restaurant_applies_per_day(self):
        # Day 1 prefers 台中, Day 2 prefers 台北 → each day gets its preferred restaurant
        r_taichung = _rest("台中餐廳", meal_times=["lunch"], area_label="台中")
        r_taipei = _rest("台北餐廳", meal_times=["lunch"], area_label="台北")
        rows = build_itinerary_rows(
            TRIP_ID, 2,
            [_attr(), _attr(), _attr(), _attr()],
            [r_taipei, r_taichung],  # r_taipei listed first
            day_preferences={1: "台中", 2: "台北"},
        )
        day1_lunch = next((r for r in rows if r["day_number"] == 1 and r["slot"] == "lunch"), None)
        day2_lunch = next((r for r in rows if r["day_number"] == 2 and r["slot"] == "lunch"), None)
        assert day1_lunch is not None and day1_lunch["title"] == "台中餐廳"
        assert day2_lunch is not None and day2_lunch["title"] == "台北餐廳"

    def test_restaurant_without_area_label_used_as_fallback(self):
        # Day 1 prefers 台中; only unspecified-area restaurant available → fallback picks it
        r_no_area = _rest("無地區餐廳", meal_times=["dinner"], area_label=None)
        rows = build_itinerary_rows(
            TRIP_ID, 1,
            [_attr(), _attr()],
            [r_no_area],
            day_preferences={1: "台中"},
        )
        dinner_rows = [r for r in rows if r["slot"] == "dinner"]
        assert len(dinner_rows) == 1
        assert dinner_rows[0]["title"] == "無地區餐廳"
