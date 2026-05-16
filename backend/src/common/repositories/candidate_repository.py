import uuid

from common.errors import ForbiddenError, NotFoundError, ValidationError
from common.validation import validate_enum


VALID_CATEGORIES = frozenset({"attraction", "restaurant"})
ALLOWED_UPDATE_FIELDS = frozenset({"category", "name", "address", "note", "source_url"})


def _fmt(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _row_to_candidate(row) -> dict:
    """Map a 13-column enriched SELECT row to the API candidate dict.

    Expected column order:
    0  id
    1  trip_id
    2  category
    3  name
    4  address
    5  note
    6  source_url
    7  created_by  (user_id FK)
    8  display_name
    9  vote_count
    10 current_user_voted
    11 created_at
    12 updated_at
    """
    return {
        "candidate_id": str(row[0]),
        "trip_id": str(row[1]),
        "category": row[2],
        "name": row[3],
        "address": row[4],
        "note": row[5],
        "source_url": row[6],
        "created_by": {
            "user_id": str(row[7]),
            "display_name": row[8],
        },
        "vote_count": row[9] if row[9] is not None else 0,
        "current_user_voted": bool(row[10]) if row[10] is not None else False,
        "created_at": _fmt(row[11]),
        "updated_at": _fmt(row[12]),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_trip_membership(conn, trip_id: str, user_id: str):
    """Return user's role string or None (not a member). Raise NotFoundError if trip absent."""
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


def _get_candidate(conn, trip_id: str, candidate_id: str) -> dict:
    """Return minimal candidate dict. Raise NotFoundError if absent from this trip."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, trip_id, created_by, category, name, address, note, source_url,
                   created_at, updated_at
            FROM trip_candidates
            WHERE id = %s AND trip_id = %s
            """,
            (candidate_id, trip_id),
        )
        row = cur.fetchone()
    if row is None:
        raise NotFoundError("Candidate not found")
    return {
        "id": str(row[0]),
        "trip_id": str(row[1]),
        "created_by": str(row[2]),
    }


# ---------------------------------------------------------------------------
# Create candidate
# ---------------------------------------------------------------------------

def create_candidate(
    conn,
    trip_id: str,
    user_id: str,
    user_display_name: str,
    category: str,
    name: str,
    address=None,
    note=None,
    source_url=None,
) -> dict:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    candidate_id = str(uuid.uuid4())
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trip_candidates
                (id, trip_id, created_by, category, name, address, note, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, trip_id, category, name, address, note, source_url,
                      created_at, updated_at
            """,
            (candidate_id, trip_id, user_id, category, name, address, note, source_url),
        )
        row = cur.fetchone()
    conn.commit()

    return {
        "candidate_id": str(row[0]),
        "trip_id": str(row[1]),
        "category": row[2],
        "name": row[3],
        "address": row[4],
        "note": row[5],
        "source_url": row[6],
        "created_by": {
            "user_id": user_id,
            "display_name": user_display_name,
        },
        "vote_count": 0,
        "current_user_voted": False,
        "created_at": _fmt(row[7]),
        "updated_at": _fmt(row[8]),
    }


# ---------------------------------------------------------------------------
# List candidates
# ---------------------------------------------------------------------------

def list_candidates(conn, trip_id: str, user_id: str, category=None) -> list:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    if category is not None:
        category_clause = "AND tc.category = %s"
        params = (user_id, trip_id, category)
    else:
        category_clause = ""
        params = (user_id, trip_id)

    sql = f"""
        SELECT
            tc.id,
            tc.trip_id,
            tc.category,
            tc.name,
            tc.address,
            tc.note,
            tc.source_url,
            tc.created_by,
            u.display_name,
            COUNT(cv.candidate_id)                         AS vote_count,
            COALESCE(BOOL_OR(cv.user_id = %s), FALSE)      AS current_user_voted,
            tc.created_at,
            tc.updated_at
        FROM trip_candidates tc
        JOIN users u ON tc.created_by = u.id
        LEFT JOIN candidate_votes cv ON tc.id = cv.candidate_id
        WHERE tc.trip_id = %s
        {category_clause}
        GROUP BY tc.id, tc.trip_id, tc.category, tc.name, tc.address, tc.note,
                 tc.source_url, tc.created_by, u.id, u.display_name,
                 tc.created_at, tc.updated_at
        ORDER BY tc.created_at DESC
    """

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [_row_to_candidate(row) for row in rows]


# ---------------------------------------------------------------------------
# Update candidate
# ---------------------------------------------------------------------------

def update_candidate(conn, trip_id: str, candidate_id: str, user_id: str, patch: dict) -> dict:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    candidate = _get_candidate(conn, trip_id, candidate_id)

    if user_id != candidate["created_by"] and role != "owner":
        raise ForbiddenError("You are not authorized to modify this candidate")

    fields = {k: v for k, v in patch.items() if k in ALLOWED_UPDATE_FIELDS}
    if not fields:
        raise ValidationError("No valid fields provided for update")

    if "category" in fields:
        validate_enum(fields["category"], VALID_CATEGORIES, "category")
    if "name" in fields:
        if not isinstance(fields["name"], str) or not fields["name"].strip():
            raise ValidationError("name must not be empty")
        fields["name"] = fields["name"].strip()

    set_clauses = [f"{col} = %s" for col in fields] + ["updated_at = CURRENT_TIMESTAMP"]
    params = list(fields.values()) + [candidate_id, trip_id, user_id]

    sql = f"""
        WITH updated AS (
            UPDATE trip_candidates
            SET {", ".join(set_clauses)}
            WHERE id = %s AND trip_id = %s
            RETURNING id, trip_id, category, name, address, note, source_url,
                      created_by, created_at, updated_at
        )
        SELECT
            upd.id,
            upd.trip_id,
            upd.category,
            upd.name,
            upd.address,
            upd.note,
            upd.source_url,
            upd.created_by,
            u.display_name,
            COUNT(cv.candidate_id)                         AS vote_count,
            COALESCE(BOOL_OR(cv.user_id = %s), FALSE)      AS current_user_voted,
            upd.created_at,
            upd.updated_at
        FROM updated upd
        JOIN users u ON upd.created_by = u.id
        LEFT JOIN candidate_votes cv ON upd.id = cv.candidate_id
        GROUP BY upd.id, upd.trip_id, upd.category, upd.name, upd.address, upd.note,
                 upd.source_url, upd.created_by, u.display_name, upd.created_at, upd.updated_at
    """

    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    conn.commit()

    return _row_to_candidate(row)


# ---------------------------------------------------------------------------
# Delete candidate
# ---------------------------------------------------------------------------

def delete_candidate(conn, trip_id: str, candidate_id: str, user_id: str) -> str:
    role = _get_trip_membership(conn, trip_id, user_id)
    if role is None:
        raise ForbiddenError("You are not a member of this trip")

    candidate = _get_candidate(conn, trip_id, candidate_id)

    if user_id != candidate["created_by"] and role != "owner":
        raise ForbiddenError("You are not authorized to delete this candidate")

    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM trip_candidates WHERE id = %s AND trip_id = %s",
            (candidate_id, trip_id),
        )
    conn.commit()

    return candidate_id
