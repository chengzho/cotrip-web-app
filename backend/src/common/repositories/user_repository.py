import uuid
from typing import Optional

from common.auth import derive_display_name, get_email_from_claims, get_required_cognito_sub
from common.errors import UnauthorizedError


_USER_COLS = ("id", "cognito_sub", "email", "display_name", "created_at", "updated_at")


def _is_stale_display_name(display_name: Optional[str], cognito_sub: str, claims: dict) -> bool:
    if not display_name or not display_name.strip():
        return True
    if display_name == cognito_sub:
        return True
    cognito_username = claims.get("cognito:username")
    if isinstance(cognito_username, str) and display_name == cognito_username:
        return True
    return False


def _row_to_user(row) -> dict:
    return dict(zip(_USER_COLS, row))


def find_user_by_cognito_sub(conn, cognito_sub: str) -> Optional[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, cognito_sub, email, display_name, created_at, updated_at "
            "FROM users WHERE cognito_sub = %s",
            (cognito_sub,),
        )
        row = cur.fetchone()
    return _row_to_user(row) if row is not None else None


def update_user_display_name(conn, user_id: str, display_name: str) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET display_name = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = %s "
            "RETURNING id, cognito_sub, email, display_name, created_at, updated_at",
            (display_name, user_id),
        )
        row = cur.fetchone()
    conn.commit()
    return _row_to_user(row)


def create_user(conn, cognito_sub: str, email: str, display_name: str) -> dict:
    user_id = str(uuid.uuid4())
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (id, cognito_sub, email, display_name) "
            "VALUES (%s, %s, %s, %s) "
            "RETURNING id, cognito_sub, email, display_name, created_at, updated_at",
            (user_id, cognito_sub, email, display_name),
        )
        row = cur.fetchone()
    conn.commit()
    return _row_to_user(row)


def resolve_or_create_user(conn, claims: dict) -> dict:
    """Resolve application user from JWT claims, lazily creating a row if needed."""
    cognito_sub = get_required_cognito_sub(claims)
    email = get_email_from_claims(claims)
    if email is None:
        raise UnauthorizedError("email claim is required for user resolution")

    user = find_user_by_cognito_sub(conn, cognito_sub)
    if user is not None:
        friendly = derive_display_name(claims)
        if _is_stale_display_name(user.get("display_name"), cognito_sub, claims) and friendly:
            user = update_user_display_name(conn, user["id"], friendly)
        return user

    display_name = derive_display_name(claims)
    return create_user(conn, cognito_sub, email, display_name)
