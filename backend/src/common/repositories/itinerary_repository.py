import uuid
from datetime import date, timedelta

from common.errors import (
    ConflictError,
    ForbiddenError,
    ItineraryAlreadyExistsError,
    NotFoundError,
    ValidationError,
)
from common.validation import require_non_empty_string, validate_enum, validate_positive_integer


VALID_SLOTS = frozenset({"morning", "lunch", "afternoon", "dinner", "evening"})
ALLOWED_ITEM_UPDATE_FIELDS = frozenset({"day_number", "slot", "title", "note", "sort_order"})

_SLOT_PATTERN = [
    ("morning",   "attraction"),
    ("morning",   "restaurant"),   # breakfast-tagged restaurants only
    ("lunch",     "restaurant"),
    ("afternoon", "attraction"),
    ("afternoon", "restaurant"),   # snack-tagged restaurants only
    ("dinner",    "restaurant"),
    ("evening",   "restaurant"),   # late_night-tagged restaurants only
]

# Map each itinerary slot to the meal-time values that make a restaurant eligible.
# Unspecified (legacy) restaurants are eligible for lunch and dinner only.
_SLOT_ELIGIBLE_MEAL_TIMES = {
    "morning":   frozenset({"breakfast"}),
    "lunch":     frozenset({"lunch", "any"}),
    "afternoon": frozenset({"snack"}),
    "dinner":    frozenset({"dinner", "any"}),
    "evening":   frozenset({"late_night"}),
}

# Slots where unspecified (legacy) restaurants are eligible.
_LEGACY_RESTAURANT_SLOTS = frozenset({"lunch", "dinner"})


def _restaurant_eligible_for_slot(restaurant: dict, slot: str) -> bool:
    """Return True if this restaurant can be scheduled into the given meal slot."""
    meal_times = restaurant.get("restaurant_meal_times")
    eligible = _SLOT_ELIGIBLE_MEAL_TIMES.get(slot)
    if eligible is None:
        return False
    if not meal_times:
        # Unspecified (legacy) → preserve old behavior: lunch and dinner only
        return slot in _LEGACY_RESTAURANT_SLOTS
    return bool(set(meal_times) & eligible)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_trip_with_dates(conn, trip_id: str, user_id: str):
    """Return (start_date, end_date, role). Raise NotFoundError if trip absent."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT t.start_date, t.end_date, tm.role
            FROM trips t
            LEFT JOIN trip_members tm ON t.id = tm.trip_id AND tm.user_id = %s
            WHERE t.id = %s
            """,
            (user_id, trip_id),
        )
        row = cur.fetchone()
    if row is None:
        raise NotFoundError("Trip not found")
    return row[0], row[1], row[2]


def _get_trip_membership(conn, trip_id: str, user_id: str):
    """Return role string or None (not a member). Raise NotFoundError if trip absent."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tm.role
            FROM trips t
            LEFT JOIN trip_members tm ON t.id = tm.trip_id AND tm.user_id = %s
            WHERE t.id = %s
            """,
            (user_id, trip_id),
        )
        row = cur.fetchone()
    if row is None:
        raise NotFoundError("Trip not found")
    return row[0]


def _get_itinerary_item(conn, trip_id: str, item_id: str) -> dict:
    """Return item dict. Raise NotFoundError if absent or belonging to different trip."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, trip_id, day_number, slot, candidate_id, category, title, note, sort_order
            FROM itinerary_items
            WHERE id = %s AND trip_id = %s
            """,
            (item_id, trip_id),
        )
        row = cur.fetchone()
    if row is None:
        raise NotFoundError("Itinerary item not found")
    return _row_to_item(row)


def _row_to_item(row) -> dict:
    return {
        "item_id": str(row[0]),
        "trip_id": str(row[1]),
        "day_number": row[2],
        "slot": row[3],
        "candidate_id": str(row[4]) if row[4] is not None else None,
        "category": row[5],
        "title": row[6],
        "note": row[7],
        "sort_order": row[8],
    }


def _group_items_by_day(trip_id: str, start_date, items: list) -> dict:
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    days_dict: dict = {}
    for item in items:
        day_num = item["day_number"]
        if day_num not in days_dict:
            days_dict[day_num] = []
        days_dict[day_num].append({
            "item_id": item["item_id"],
            "slot": item["slot"],
            "title": item["title"],
            "candidate_id": item["candidate_id"],
            "category": item["category"],
            "note": item["note"],
            "sort_order": item["sort_order"],
        })

    days = []
    for day_num in sorted(days_dict.keys()):
        days.append({
            "day_number": day_num,
            "date": (start_date + timedelta(days=day_num - 1)).isoformat(),
            "items": days_dict[day_num],
        })

    return {"trip_id": trip_id, "days": days}


# ---------------------------------------------------------------------------
# Pure generation helper (no DB calls — fully unit-testable)
# ---------------------------------------------------------------------------

def build_itinerary_rows(
    trip_id: str,
    num_days: int,
    attractions: list,
    restaurants: list,
    day_preferences: dict | None = None,
) -> list:
    """Build insertion-ready row dicts from ranked candidate lists.

    Restaurants are assigned to meal slots based on their restaurant_meal_times metadata.
    Meal-time eligibility is a hard constraint and is never overridden.
    Unspecified (legacy) restaurants are eligible for both lunch and dinner.
    A restaurant is never scheduled twice even if eligible for multiple slots.

    day_preferences: optional dict {day_number (int) -> preferred_area_label (str|None)}.
    Area preference is soft and applies to both attractions and restaurants.
    For restaurants, area preference is evaluated only among meal-time-eligible candidates.
    """
    rows = []
    used_attr_ids: set = set()
    used_restaurant_ids: set = set()
    day_preferences = day_preferences or {}

    def _next_attraction_for_day(day_number: int):
        preferred_area = day_preferences.get(day_number)
        # First pass: prefer attractions matching the day's preferred area
        if preferred_area:
            for a in attractions:
                if a["id"] not in used_attr_ids and a.get("area_label") == preferred_area:
                    used_attr_ids.add(a["id"])
                    return a
        # Second pass: any remaining attraction
        for a in attractions:
            if a["id"] not in used_attr_ids:
                used_attr_ids.add(a["id"])
                return a
        return None

    def _next_restaurant_for_slot(slot: str, day_number: int):
        preferred_area = day_preferences.get(day_number)
        # First pass: eligible restaurants matching the day's preferred area
        if preferred_area:
            for r in restaurants:
                if (
                    r["id"] not in used_restaurant_ids
                    and _restaurant_eligible_for_slot(r, slot)
                    and r.get("area_label") == preferred_area
                ):
                    used_restaurant_ids.add(r["id"])
                    return r
        # Second pass: any eligible restaurant
        for r in restaurants:
            if r["id"] not in used_restaurant_ids and _restaurant_eligible_for_slot(r, slot):
                used_restaurant_ids.add(r["id"])
                return r
        return None

    for day_idx in range(num_days):
        day_number = day_idx + 1
        slot_sort = 1
        for slot, category in _SLOT_PATTERN:
            if category == "attraction":
                candidate = _next_attraction_for_day(day_number)
            else:
                candidate = _next_restaurant_for_slot(slot, day_number)
            if candidate is None:
                continue
            rows.append({
                "id": str(uuid.uuid4()),
                "trip_id": trip_id,
                "day_number": day_number,
                "slot": slot,
                "candidate_id": candidate["id"],
                "category": candidate["category"],   # snapshot
                "title": candidate["name"],
                "note": candidate["note"],
                "sort_order": slot_sort,
            })
            slot_sort += 1

    return rows


# ---------------------------------------------------------------------------
# Day preferences (area preference — soft constraint)
# ---------------------------------------------------------------------------

def get_day_preferences(conn, trip_id: str, user_id: str) -> list:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT day_number, preferred_area_label
            FROM trip_day_preferences
            WHERE trip_id = %s
            ORDER BY day_number
            """,
            (trip_id,),
        )
        rows = cur.fetchall()

    return [{"day_number": r[0], "preferred_area_label": r[1]} for r in rows]


def upsert_day_preferences(conn, trip_id: str, user_id: str, preferences: list) -> list:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")
    if role != "owner":
        raise ForbiddenError("Only trip owners can update day preferences")

    if not isinstance(preferences, list):
        raise ValidationError("preferences must be an array")

    seen_days: set = set()
    cleaned = []
    for entry in preferences:
        if not isinstance(entry, dict):
            raise ValidationError("Each preference entry must be an object")
        day_number = entry.get("day_number")
        preferred_area = entry.get("preferred_area_label")
        if not isinstance(day_number, int) or day_number < 1:
            raise ValidationError("day_number must be a positive integer")
        if day_number in seen_days:
            raise ValidationError(f"Duplicate day_number: {day_number}")
        seen_days.add(day_number)
        if preferred_area is None:
            normalized_area = None
        elif isinstance(preferred_area, str):
            normalized_area = preferred_area.strip() or None
        else:
            raise ValidationError("preferred_area_label must be a string or null")
        cleaned.append((day_number, normalized_area))

    with conn.cursor() as cur:
        cur.execute("DELETE FROM trip_day_preferences WHERE trip_id = %s", (trip_id,))
        for day_number, preferred_area in cleaned:
            cur.execute(
                """
                INSERT INTO trip_day_preferences (trip_id, day_number, preferred_area_label)
                VALUES (%s, %s, %s)
                """,
                (trip_id, day_number, preferred_area),
            )

    conn.commit()

    return [{"day_number": d, "preferred_area_label": a} for d, a in sorted(cleaned)]


# ---------------------------------------------------------------------------
# Generate itinerary
# ---------------------------------------------------------------------------

def generate_itinerary(
    conn, trip_id: str, user_id: str, overwrite_existing: bool = False
) -> dict:
    start_date, end_date, role = _get_trip_with_dates(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")
    if role != 'owner':
        raise ForbiddenError("Only trip owners can modify the itinerary")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM itinerary_items WHERE trip_id = %s",
            (trip_id,),
        )
        existing_count = cur.fetchone()[0]

    if existing_count > 0 and not overwrite_existing:
        raise ItineraryAlreadyExistsError()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tc.id, tc.category, tc.name, tc.note, tc.restaurant_meal_times, tc.area_label
            FROM trip_candidates tc
            LEFT JOIN candidate_votes cv ON tc.id = cv.candidate_id
            WHERE tc.trip_id = %s
            GROUP BY tc.id, tc.category, tc.name, tc.note, tc.restaurant_meal_times,
                     tc.area_label, tc.created_at
            ORDER BY COUNT(cv.candidate_id) DESC, tc.created_at ASC
            """,
            (trip_id,),
        )
        candidate_rows = cur.fetchall()

    if not candidate_rows:
        raise ConflictError("No candidate places are available for itinerary generation.")

    attractions = [
        {
            "id": str(r[0]),
            "category": r[1],
            "name": r[2],
            "note": r[3],
            "area_label": r[5],
        }
        for r in candidate_rows if r[1] == "attraction"
    ]
    restaurants = [
        {
            "id": str(r[0]),
            "category": r[1],
            "name": r[2],
            "note": r[3],
            "restaurant_meal_times": r[4],
            "area_label": r[5],
        }
        for r in candidate_rows if r[1] == "restaurant"
    ]

    # Load day preferences (soft area preference)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT day_number, preferred_area_label
            FROM trip_day_preferences
            WHERE trip_id = %s
            """,
            (trip_id,),
        )
        pref_rows = cur.fetchall()
    day_preferences = {r[0]: r[1] for r in pref_rows}

    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)

    num_days = (end_date - start_date).days + 1
    rows = build_itinerary_rows(
        trip_id, num_days, attractions, restaurants, day_preferences=day_preferences
    )

    if overwrite_existing and existing_count > 0:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM itinerary_items WHERE trip_id = %s",
                (trip_id,),
            )

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                """
                INSERT INTO itinerary_items
                    (id, trip_id, day_number, slot, candidate_id, category, title, note, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row["id"], row["trip_id"], row["day_number"], row["slot"],
                    row["candidate_id"], row["category"], row["title"], row["note"],
                    row["sort_order"],
                ),
            )

    conn.commit()

    items = [
        {
            "item_id": r["id"],
            "trip_id": r["trip_id"],
            "day_number": r["day_number"],
            "slot": r["slot"],
            "candidate_id": r["candidate_id"],
            "category": r["category"],
            "title": r["title"],
            "note": r["note"],
            "sort_order": r["sort_order"],
        }
        for r in rows
    ]

    return _group_items_by_day(trip_id, start_date, items)


# ---------------------------------------------------------------------------
# Get itinerary
# ---------------------------------------------------------------------------

def get_itinerary(conn, trip_id: str, user_id: str) -> dict:
    start_date, _, role = _get_trip_with_dates(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, trip_id, day_number, slot, candidate_id, category, title, note, sort_order
            FROM itinerary_items
            WHERE trip_id = %s
            ORDER BY day_number ASC, sort_order ASC
            """,
            (trip_id,),
        )
        rows = cur.fetchall()

    items = [_row_to_item(r) for r in rows]
    return _group_items_by_day(trip_id, start_date, items)


# ---------------------------------------------------------------------------
# Update itinerary item
# ---------------------------------------------------------------------------

def update_itinerary_item(
    conn, trip_id: str, item_id: str, user_id: str, patch: dict
) -> dict:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")
    if role != 'owner':
        raise ForbiddenError("Only trip owners can modify the itinerary")

    _get_itinerary_item(conn, trip_id, item_id)

    if "category" in patch:
        raise ValidationError("category cannot be updated")

    updates = {k: v for k, v in patch.items() if k in ALLOWED_ITEM_UPDATE_FIELDS}
    if not updates:
        raise ValidationError("Request body must contain at least one valid field to update")

    if "day_number" in updates:
        validate_positive_integer(updates["day_number"], "day_number")
    if "sort_order" in updates:
        validate_positive_integer(updates["sort_order"], "sort_order")
    if "slot" in updates:
        validate_enum(updates["slot"], VALID_SLOTS, "slot")
    if "title" in updates:
        require_non_empty_string(updates["title"], "title")

    set_parts = [f"{k} = %s" for k in updates]
    set_parts.append("updated_at = NOW()")
    params = list(updates.values()) + [item_id, trip_id]

    sql = (
        f"UPDATE itinerary_items SET {', '.join(set_parts)} "
        f"WHERE id = %s AND trip_id = %s "
        f"RETURNING id, trip_id, day_number, slot, candidate_id, category, title, note, sort_order"
    )

    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()

    conn.commit()

    if row is None:
        raise NotFoundError("Itinerary item not found")

    return _row_to_item(row)


# ---------------------------------------------------------------------------
# Delete itinerary item
# ---------------------------------------------------------------------------

def delete_itinerary_item(conn, trip_id: str, item_id: str, user_id: str) -> str:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")
    if role != 'owner':
        raise ForbiddenError("Only trip owners can modify the itinerary")

    item = _get_itinerary_item(conn, trip_id, item_id)

    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM itinerary_items WHERE id = %s AND trip_id = %s",
            (item_id, trip_id),
        )

    conn.commit()

    return item["item_id"]
