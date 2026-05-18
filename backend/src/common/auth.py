from typing import Any

from common.errors import UnauthorizedError


def get_jwt_claims(event: dict) -> dict:
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]
    except (KeyError, TypeError):
        raise UnauthorizedError("JWT claims not found in request context")


def get_required_cognito_sub(claims: dict) -> str:
    sub = claims.get("sub")
    if not sub or not isinstance(sub, str) or not sub.strip():
        raise UnauthorizedError("Missing required identity claim: sub")
    return sub


def get_email_from_claims(claims: dict) -> str | None:
    email = claims.get("email")
    if isinstance(email, str) and email.strip():
        return email.strip()
    return None


def derive_display_name(claims: dict) -> str:
    for key in ("name", "preferred_username"):
        value = claims.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    email = get_email_from_claims(claims)
    if email and "@" in email:
        local_part = email.split("@", 1)[0]
        if local_part:
            return local_part

    return "CoTrip User"


def get_request_id(event: dict) -> str:
    try:
        return event["requestContext"]["requestId"] or ""
    except (KeyError, TypeError):
        return ""
