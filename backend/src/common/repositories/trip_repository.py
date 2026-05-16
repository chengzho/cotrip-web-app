import uuid
from typing import Optional

from common.errors import ForbiddenError, NotFoundError, ValidationError
from common.validation import validate_date_string, validate_date_range


VALID_SCOPES = frozenset({"upcoming", "past", "all"})

ALLOWED_UPDATE_FIELDS = frozenset({"title", "destination", "start_date", "end_date", "description"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fmt(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _get_trip_and_membership(conn, trip_id: str, user_id: str):
    """Return (trip_dict, role). role is None if user is not a member.
    Both are None if the trip does not exist."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT t.id, t.title, t.destination, t.start_date, t.end_date,
                   t.description, t.created_by, t.created_at, t.updated_at,
                   tm.role
            FROM trips t
            LEFT JOIN trip_members tm ON t.id = tm.trip_id AND tm.user_id = %s
            WHERE t.id = %s
            """,
            (user_id, trip_id),
        )
        row = cur.fetchone()
    if row is None:
        return None, None
    trip = {
        "id": str(row[0]),
        "title": row[1],
        "destination": row[2],
        "start_date": _fmt(row[3]),
        "end_date": _fmt(row[4]),
        "description": row[5],
        "created_by": str(row[6]) if row[6] else None,
        "created_at": _fmt(row[7]),
        "updated_at": _fmt(row[8]),
    }
    return trip, row[9]  # row[9] is role, None if not a member


# ---------------------------------------------------------------------------
# Create trip (transactional)
# ---------------------------------------------------------------------------

def create_trip(
    conn,
    user_id: str,
    title: str,
    destination: str,
    start_date: str,
    end_date: str,
    description: Optional[str] = None,
) -> dict:
    """Insert trip + owner membership atomically."""
    trip_id = str(uuid.uuid4())
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trips (id, title, destination, start_date, end_date, description, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, destination, start_date, end_date, description, created_at, updated_at
            """,
            (trip_id, title, destination, start_date, end_date, description, user_id),
        )
        trip_row = cur.fetchone()
        cur.execute(
            "INSERT INTO trip_members (trip_id, user_id, role) VALUES (%s, %s, 'owner')",
            (trip_id, user_id),
        )
    conn.commit()
    return {
        "trip_id": str(trip_row[0]),
        "title": trip_row[1],
        "destination": trip_row[2],
        "start_date": _fmt(trip_row[3]),
        "end_date": _fmt(trip_row[4]),
        "description": trip_row[5],
        "role": "owner",
        "created_at": _fmt(trip_row[6]),
        "updated_at": _fmt(trip_row[7]),
    }


# ---------------------------------------------------------------------------
# List trips
# ---------------------------------------------------------------------------

def list_trips(conn, user_id: str, scope: str = "upcoming") -> list:
    if scope not in VALID_SCOPES:
        raise ValidationError(f"scope must be one of: {', '.join(sorted(VALID_SCOPES))}")

    if scope == "upcoming":
        date_filter = "AND t.end_date >= CURRENT_DATE"
        order_by = "t.start_date ASC"
    elif scope == "past":
        date_filter = "AND t.end_date < CURRENT_DATE"
        order_by = "t.end_date DESC"
    else:  # all
        date_filter = ""
        order_by = "t.start_date ASC"

    sql = f"""
        SELECT
            t.id,
            t.title,
            t.destination,
            t.start_date,
            t.end_date,
            tm.role,
            (SELECT COUNT(*) FROM trip_members tm2 WHERE tm2.trip_id = t.id) AS member_count,
            (SELECT COUNT(*) FROM trip_candidates tc  WHERE tc.trip_id  = t.id) AS candidate_count,
            (SELECT COUNT(*) FROM itinerary_items ii  WHERE ii.trip_id  = t.id) AS itinerary_item_count
        FROM trips t
        JOIN trip_members tm ON t.id = tm.trip_id AND tm.user_id = %s
        WHERE 1=1 {date_filter}
        ORDER BY {order_by}
    """
    with conn.cursor() as cur:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()

    return [
        {
            "trip_id": str(row[0]),
            "title": row[1],
            "destination": row[2],
            "start_date": _fmt(row[3]),
            "end_date": _fmt(row[4]),
            "role": row[5],
            "member_count": row[6],
            "candidate_count": row[7],
            "itinerary_item_count": row[8],
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Get trip detail
# ---------------------------------------------------------------------------

def get_trip_detail(conn, trip_id: str, user_id: str) -> dict:
    trip, role = _get_trip_and_membership(conn, trip_id, user_id)
    if trip is None:
        raise NotFoundError("Trip not found")
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM trip_members   WHERE trip_id = %s) AS member_count,
                (SELECT COUNT(*) FROM trip_candidates WHERE trip_id = %s) AS candidate_count,
                (SELECT COUNT(*) FROM candidate_votes cv
                    JOIN trip_candidates tc ON cv.candidate_id = tc.id
                    WHERE tc.trip_id = %s) AS vote_count,
                (SELECT COUNT(*) FROM itinerary_items WHERE trip_id = %s) AS itinerary_item_count
            """,
            (trip_id, trip_id, trip_id, trip_id),
        )
        counts = cur.fetchone()

    return {
        "trip_id": trip["id"],
        "title": trip["title"],
        "destination": trip["destination"],
        "start_date": trip["start_date"],
        "end_date": trip["end_date"],
        "description": trip["description"],
        "current_user_role": role,
        "summary": {
            "member_count": counts[0],
            "candidate_count": counts[1],
            "vote_count": counts[2],
            "itinerary_item_count": counts[3],
        },
        "created_at": trip["created_at"],
        "updated_at": trip["updated_at"],
    }


# ---------------------------------------------------------------------------
# Update trip (owner-only)
# ---------------------------------------------------------------------------

def update_trip(conn, trip_id: str, user_id: str, patch: dict) -> dict:
    if not patch:
        raise ValidationError("Request body must contain at least one field to update")

    fields = {k: v for k, v in patch.items() if k in ALLOWED_UPDATE_FIELDS}
    if not fields:
        raise ValidationError("No valid fields provided for update")

    # Existence and ownership checks
    trip, role = _get_trip_and_membership(conn, trip_id, user_id)
    if trip is None:
        raise NotFoundError("Trip not found")
    if role is None:
        raise ForbiddenError("You are not a member of this trip")
    if role != "owner":
        raise ForbiddenError("Only the trip owner can update trip details")

    # Field-level validation
    if "title" in fields:
        if not isinstance(fields["title"], str) or not fields["title"].strip():
            raise ValidationError("title must not be empty")
        fields["title"] = fields["title"].strip()
    if "destination" in fields:
        if not isinstance(fields["destination"], str) or not fields["destination"].strip():
            raise ValidationError("destination must not be empty")
        fields["destination"] = fields["destination"].strip()
    if "start_date" in fields:
        validate_date_string(fields["start_date"], "start_date")
    if "end_date" in fields:
        validate_date_string(fields["end_date"], "end_date")

    # Date range using merged current + new values
    effective_start = fields.get("start_date", trip["start_date"])
    effective_end = fields.get("end_date", trip["end_date"])
    validate_date_range(effective_start, effective_end)

    set_clauses = [f"{col} = %s" for col in fields]
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params = list(fields.values()) + [trip_id]

    with conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE trips SET {", ".join(set_clauses)}
            WHERE id = %s
            RETURNING id, title, destination, start_date, end_date, description, updated_at
            """,
            params,
        )
        row = cur.fetchone()
    conn.commit()

    return {
        "trip_id": str(row[0]),
        "title": row[1],
        "destination": row[2],
        "start_date": _fmt(row[3]),
        "end_date": _fmt(row[4]),
        "description": row[5],
        "updated_at": _fmt(row[6]),
    }


# ---------------------------------------------------------------------------
# List members
# ---------------------------------------------------------------------------

def list_members(conn, trip_id: str, user_id: str) -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM trips WHERE id = %s", (trip_id,))
        if cur.fetchone() is None:
            raise NotFoundError("Trip not found")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM trip_members WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id),
        )
        if cur.fetchone() is None:
            raise ForbiddenError("You are not a member of this trip")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT u.id, u.display_name, u.email, tm.role, tm.joined_at
            FROM trip_members tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.trip_id = %s
            ORDER BY tm.joined_at ASC
            """,
            (trip_id,),
        )
        rows = cur.fetchall()

    return [
        {
            "user_id": str(row[0]),
            "display_name": row[1],
            "email": row[2],
            "role": row[3],
            "joined_at": _fmt(row[4]),
        }
        for row in rows
    ]
