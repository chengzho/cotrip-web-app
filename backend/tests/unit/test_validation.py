import pytest
import uuid
from common.errors import ValidationError
from common.validation import (
    require_non_empty_string,
    validate_uuid_string,
    validate_date_string,
    validate_date_range,
    validate_enum,
    ensure_non_empty_patch_payload,
)


# --- require_non_empty_string ---

def test_require_non_empty_string_valid():
    assert require_non_empty_string("hello", "title") == "hello"


def test_require_non_empty_string_strips_whitespace():
    assert require_non_empty_string("  hi  ", "title") == "hi"


def test_require_non_empty_string_empty_raises():
    with pytest.raises(ValidationError, match="title"):
        require_non_empty_string("", "title")


def test_require_non_empty_string_whitespace_only_raises():
    with pytest.raises(ValidationError, match="title"):
        require_non_empty_string("   ", "title")


def test_require_non_empty_string_non_string_raises():
    with pytest.raises(ValidationError):
        require_non_empty_string(None, "title")


# --- validate_uuid_string ---

def test_validate_uuid_valid():
    value = str(uuid.uuid4())
    assert validate_uuid_string(value, "trip_id") == value


def test_validate_uuid_invalid_string():
    with pytest.raises(ValidationError, match="trip_id"):
        validate_uuid_string("not-a-uuid", "trip_id")


def test_validate_uuid_non_string():
    with pytest.raises(ValidationError):
        validate_uuid_string(123, "trip_id")


# --- validate_date_string ---

def test_validate_date_string_valid():
    assert validate_date_string("2026-08-20", "start_date") == "2026-08-20"


def test_validate_date_string_wrong_format():
    with pytest.raises(ValidationError, match="start_date"):
        validate_date_string("20-08-2026", "start_date")


def test_validate_date_string_invalid_day():
    with pytest.raises(ValidationError):
        validate_date_string("2026-02-30", "start_date")


def test_validate_date_string_non_string():
    with pytest.raises(ValidationError):
        validate_date_string(20260820, "start_date")


# --- validate_date_range ---

def test_validate_date_range_valid():
    validate_date_range("2026-08-20", "2026-08-25")  # no exception


def test_validate_date_range_same_day():
    validate_date_range("2026-08-20", "2026-08-20")  # equal is allowed


def test_validate_date_range_invalid():
    with pytest.raises(ValidationError, match="start_date"):
        validate_date_range("2026-08-25", "2026-08-20")


# --- validate_enum ---

def test_validate_enum_valid():
    assert validate_enum("attraction", {"attraction", "restaurant"}, "category") == "attraction"


def test_validate_enum_invalid():
    with pytest.raises(ValidationError, match="category"):
        validate_enum("hotel", {"attraction", "restaurant"}, "category")


def test_validate_enum_role_values():
    assert validate_enum("owner", {"owner", "member"}, "role") == "owner"
    assert validate_enum("member", {"owner", "member"}, "role") == "member"


def test_validate_enum_slot_values():
    slots = {"morning", "lunch", "afternoon", "dinner", "evening"}
    for slot in slots:
        assert validate_enum(slot, slots, "slot") == slot


def test_validate_enum_scope_values():
    scopes = {"upcoming", "past", "all"}
    for scope in scopes:
        assert validate_enum(scope, scopes, "scope") == scope

    with pytest.raises(ValidationError):
        validate_enum("invalid", scopes, "scope")


# --- ensure_non_empty_patch_payload ---

def test_ensure_non_empty_patch_payload_valid():
    ensure_non_empty_patch_payload({"title": "Updated"})  # no exception


def test_ensure_non_empty_patch_payload_empty_raises():
    with pytest.raises(ValidationError, match="at least one field"):
        ensure_non_empty_patch_payload({})


def test_ensure_non_empty_patch_payload_none_raises():
    with pytest.raises(ValidationError):
        ensure_non_empty_patch_payload(None)
