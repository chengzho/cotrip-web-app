from common.errors import ForbiddenError, NotFoundError
from common.repositories.candidate_repository import VALID_CATEGORIES


def _fmt(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _resolve_candidate_membership(conn, candidate_id: str, user_id: str) -> tuple:
    """Return (trip_id_str, role). Raise NotFoundError / ForbiddenError."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tc.trip_id, tm.role
            FROM trip_candidates tc
            LEFT JOIN trip_members tm ON tc.trip_id = tm.trip_id AND tm.user_id = %s
            WHERE tc.id = %s
            """,
            (user_id, candidate_id),
        )
        row = cur.fetchone()
    if row is None:
        raise NotFoundError("Candidate not found")
    if row[1] is None:
        raise ForbiddenError("You are not a member of this trip")
    return str(row[0]), row[1]


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


# ---------------------------------------------------------------------------
# Vote for a candidate (idempotent)
# ---------------------------------------------------------------------------

def vote_candidate(conn, candidate_id: str, user_id: str) -> dict:
    _resolve_candidate_membership(conn, candidate_id, user_id)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO candidate_votes (candidate_id, user_id, vote_value)
            VALUES (%s, %s, 1)
            ON CONFLICT (candidate_id, user_id) DO NOTHING
            """,
            (candidate_id, user_id),
        )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM candidate_votes WHERE candidate_id = %s",
            (candidate_id,),
        )
        vote_count = cur.fetchone()[0]

    conn.commit()

    return {
        "candidate_id": candidate_id,
        "voted": True,
        "vote_count": vote_count,
    }


# ---------------------------------------------------------------------------
# Remove the current user's vote (idempotent)
# ---------------------------------------------------------------------------

def unvote_candidate(conn, candidate_id: str, user_id: str) -> dict:
    _resolve_candidate_membership(conn, candidate_id, user_id)

    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM candidate_votes WHERE candidate_id = %s AND user_id = %s",
            (candidate_id, user_id),
        )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM candidate_votes WHERE candidate_id = %s",
            (candidate_id,),
        )
        vote_count = cur.fetchone()[0]

    conn.commit()

    return {
        "candidate_id": candidate_id,
        "voted": False,
        "vote_count": vote_count,
    }


# ---------------------------------------------------------------------------
# Get ranked candidates for a trip
# ---------------------------------------------------------------------------

def get_rankings(conn, trip_id: str, user_id: str, category=None) -> list:
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
            tc.note,
            tc.created_by,
            u.display_name,
            COUNT(cv.candidate_id)                          AS vote_count,
            COALESCE(BOOL_OR(cv.user_id = %s), FALSE)       AS current_user_voted,
            tc.created_at
        FROM trip_candidates tc
        JOIN users u ON tc.created_by = u.id
        LEFT JOIN candidate_votes cv ON tc.id = cv.candidate_id
        WHERE tc.trip_id = %s
        {category_clause}
        GROUP BY tc.id, tc.trip_id, tc.category, tc.name, tc.note, tc.created_by,
                 u.id, u.display_name, tc.created_at
        ORDER BY vote_count DESC, tc.created_at ASC
    """

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    result = []
    for rank, row in enumerate(rows, start=1):
        result.append({
            "rank": rank,
            "candidate_id": str(row[0]),
            "trip_id": str(row[1]),
            "category": row[2],
            "name": row[3],
            "note": row[4],
            "created_by": {
                "user_id": str(row[5]),
                "display_name": row[6],
            },
            "vote_count": row[7] if row[7] is not None else 0,
            "current_user_voted": bool(row[8]) if row[8] is not None else False,
            "created_at": _fmt(row[9]),
        })

    return result
