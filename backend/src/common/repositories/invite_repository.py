import os
import uuid
from datetime import datetime, timedelta, timezone

from common.errors import (
    AlreadyExistsError,
    ForbiddenError,
    InternalServerError,
    InviteExpiredError,
    InviteRevokedError,
    InviteUsageLimitReachedError,
    NotFoundError,
)
from common.invite_tokens import generate_invite_token, hash_invite_token


DEFAULT_EXPIRES_IN_DAYS = 7
DEFAULT_MAX_USES = 20


def _fmt(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _build_invite_url(raw_token: str) -> str:
    base_url = os.environ.get("FRONTEND_BASE_URL", "")
    if not base_url:
        raise InternalServerError("FRONTEND_BASE_URL is not configured")
    return f"{base_url.rstrip('/')}/join/{raw_token}"


def _validate_invite_state(expires_at, revoked_at, used_count, max_uses) -> None:
    if revoked_at is not None:
        raise InviteRevokedError()
    if expires_at is not None:
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
            raise InviteExpiredError()
    if used_count >= max_uses:
        raise InviteUsageLimitReachedError()


# ---------------------------------------------------------------------------
# Create invite
# ---------------------------------------------------------------------------

def create_invite(
    conn,
    trip_id: str,
    user_id: str,
    expires_in_days: int = DEFAULT_EXPIRES_IN_DAYS,
    max_uses: int = DEFAULT_MAX_USES,
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT role FROM trip_members WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id),
        )
        row = cur.fetchone()

    if row is None:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM trips WHERE id = %s", (trip_id,))
            trip_exists = cur.fetchone() is not None
        if not trip_exists:
            raise NotFoundError("Trip not found")
        raise ForbiddenError("You are not a member of this trip")

    if row[0] != "owner":
        raise ForbiddenError("Only the trip owner can create invite links")

    raw_token = generate_invite_token()
    token_hash = hash_invite_token(raw_token)
    invite_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trip_invites (id, trip_id, created_by, token_hash, expires_at, max_uses)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, trip_id, expires_at, max_uses
            """,
            (invite_id, trip_id, user_id, token_hash, expires_at, max_uses),
        )
        inv_row = cur.fetchone()
    conn.commit()

    invite_url = _build_invite_url(raw_token)

    return {
        "id": str(inv_row[0]),
        "trip_id": str(inv_row[1]),
        "invite_url": invite_url,
        "expires_at": _fmt(inv_row[2]),
        "max_uses": inv_row[3],
    }


# ---------------------------------------------------------------------------
# Preview invite (public)
# ---------------------------------------------------------------------------

def preview_invite(conn, raw_token: str) -> dict:
    token_hash = hash_invite_token(raw_token)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ti.expires_at,
                ti.revoked_at,
                ti.used_count,
                ti.max_uses,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                u.display_name
            FROM trip_invites ti
            JOIN trips t ON ti.trip_id = t.id
            JOIN users u ON ti.created_by = u.id
            WHERE ti.token_hash = %s
            """,
            (token_hash,),
        )
        row = cur.fetchone()

    if row is None:
        raise NotFoundError("Invite not found")

    _validate_invite_state(
        expires_at=row[0],
        revoked_at=row[1],
        used_count=row[2],
        max_uses=row[3],
    )

    return {
        "trip_title": row[4],
        "destination": row[5],
        "start_date": _fmt(row[6]),
        "end_date": _fmt(row[7]),
        "invited_by_display_name": row[8],
    }


# ---------------------------------------------------------------------------
# Join invite (transactional)
# ---------------------------------------------------------------------------

def join_invite(conn, raw_token: str, user_id: str) -> dict:
    token_hash = hash_invite_token(raw_token)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ti.id,
                ti.trip_id,
                ti.expires_at,
                ti.revoked_at,
                ti.used_count,
                ti.max_uses,
                t.title,
                t.destination
            FROM trip_invites ti
            JOIN trips t ON ti.trip_id = t.id
            WHERE ti.token_hash = %s
            FOR UPDATE OF ti
            """,
            (token_hash,),
        )
        row = cur.fetchone()

        if row is None:
            raise NotFoundError("Invite not found")

        invite_id = str(row[0])
        trip_id = str(row[1])

        _validate_invite_state(
            expires_at=row[2],
            revoked_at=row[3],
            used_count=row[4],
            max_uses=row[5],
        )

        trip_title = row[6]
        trip_destination = row[7]

        cur.execute(
            "SELECT 1 FROM trip_members WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id),
        )
        if cur.fetchone() is not None:
            raise AlreadyExistsError("You are already a member of this trip")

        cur.execute(
            "INSERT INTO trip_members (trip_id, user_id, role) VALUES (%s, %s, 'member')",
            (trip_id, user_id),
        )
        cur.execute(
            "UPDATE trip_invites SET used_count = used_count + 1 WHERE id = %s",
            (invite_id,),
        )

    conn.commit()

    return {
        "id": trip_id,
        "title": trip_title,
        "destination": trip_destination,
        "current_user_role": "member",
    }
