import pytest
from common.auth import (
    get_jwt_claims,
    get_required_cognito_sub,
    get_email_from_claims,
    derive_display_name,
    get_request_id,
)
from common.errors import UnauthorizedError


def _make_event(claims: dict, request_id: str = "req-test") -> dict:
    return {
        "requestContext": {
            "requestId": request_id,
            "authorizer": {
                "jwt": {
                    "claims": claims,
                }
            },
        }
    }


# --- get_jwt_claims ---

def test_get_jwt_claims_success():
    event = _make_event({"sub": "abc123", "email": "user@example.com"})
    claims = get_jwt_claims(event)
    assert claims["sub"] == "abc123"


def test_get_jwt_claims_missing_context():
    with pytest.raises(UnauthorizedError):
        get_jwt_claims({})


def test_get_jwt_claims_missing_authorizer():
    with pytest.raises(UnauthorizedError):
        get_jwt_claims({"requestContext": {}})


# --- get_required_cognito_sub ---

def test_get_required_cognito_sub_present():
    assert get_required_cognito_sub({"sub": "user-sub-123"}) == "user-sub-123"


def test_get_required_cognito_sub_missing():
    with pytest.raises(UnauthorizedError, match="sub"):
        get_required_cognito_sub({})


def test_get_required_cognito_sub_empty_string():
    with pytest.raises(UnauthorizedError):
        get_required_cognito_sub({"sub": ""})


def test_get_required_cognito_sub_whitespace():
    with pytest.raises(UnauthorizedError):
        get_required_cognito_sub({"sub": "   "})


# --- get_email_from_claims ---

def test_get_email_from_claims_present():
    assert get_email_from_claims({"email": "user@example.com"}) == "user@example.com"


def test_get_email_from_claims_absent():
    assert get_email_from_claims({}) is None


def test_get_email_from_claims_empty():
    assert get_email_from_claims({"email": ""}) is None


# --- derive_display_name ---

def test_derive_display_name_uses_name_first():
    claims = {
        "name": "Alice",
        "preferred_username": "alice99",
        "cognito:username": "alice-cog",
        "email": "alice@example.com",
    }
    assert derive_display_name(claims) == "Alice"


def test_derive_display_name_falls_back_to_preferred_username():
    claims = {
        "preferred_username": "alice99",
        "cognito:username": "alice-cog",
        "email": "alice@example.com",
    }
    assert derive_display_name(claims) == "alice99"


def test_derive_display_name_skips_cognito_username_falls_to_email_local_part():
    # cognito:username is an internal Cognito identifier — must not be used as display name
    claims = {
        "cognito:username": "alice-cog",
        "email": "alice@example.com",
    }
    assert derive_display_name(claims) == "alice"


def test_derive_display_name_skips_sub_falls_to_email_local_part():
    # sub is an internal UUID — must not be used as display name
    claims = {
        "sub": "74b864b8-80b1-70bd-1e98-57d696a328b9",
        "email": "alice@example.com",
    }
    assert derive_display_name(claims) == "alice"


def test_derive_display_name_falls_back_to_email_local_part():
    claims = {"email": "alice@example.com"}
    assert derive_display_name(claims) == "alice"


def test_derive_display_name_email_local_part_from_real_address():
    claims = {"email": "jczho.mg14@nycu.edu.tw"}
    assert derive_display_name(claims) == "jczho.mg14"


def test_derive_display_name_falls_back_to_default():
    assert derive_display_name({}) == "CoTrip User"


def test_derive_display_name_name_empty_falls_through():
    claims = {"name": "", "preferred_username": "alice99"}
    assert derive_display_name(claims) == "alice99"


def test_derive_display_name_email_no_at_sign_falls_to_default():
    claims = {"email": "invalidemail"}
    assert derive_display_name(claims) == "CoTrip User"


# --- get_request_id ---

def test_get_request_id_present():
    event = _make_event({}, request_id="my-req-id")
    assert get_request_id(event) == "my-req-id"


def test_get_request_id_missing():
    assert get_request_id({}) == ""
