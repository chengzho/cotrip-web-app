import re
import uuid
from datetime import date
from typing import Any, Collection

from common.errors import ValidationError

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} is required")
    return value.strip()


def validate_uuid_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a valid UUID")
    try:
        uuid.UUID(value)
    except ValueError:
        raise ValidationError(f"{field_name} must be a valid UUID")
    return value


def validate_date_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format")
    return value


def validate_date_range(start: str, end: str) -> None:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if start_date > end_date:
        raise ValidationError("start_date must not be later than end_date")


def validate_enum(value: Any, allowed: Collection[str], field_name: str) -> str:
    if value not in allowed:
        joined = ", ".join(sorted(allowed))
        raise ValidationError(f"{field_name} must be one of: {joined}")
    return value


def validate_positive_integer(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer")
    return value


def ensure_non_empty_patch_payload(body: dict) -> None:
    if not body:
        raise ValidationError("Request body must contain at least one field to update")
