import pytest
from common.errors import (
    AppError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    AlreadyExistsError,
    ConflictError,
    InternalServerError,
    ErrorCode,
)


def test_validation_error_fields():
    err = ValidationError("title is required")
    assert err.code == ErrorCode.VALIDATION_ERROR
    assert err.status_code == 400
    assert err.message == "title is required"
    assert isinstance(err, AppError)


def test_unauthorized_error_defaults():
    err = UnauthorizedError()
    assert err.code == ErrorCode.UNAUTHORIZED
    assert err.status_code == 401


def test_unauthorized_error_custom_message():
    err = UnauthorizedError("Missing token")
    assert err.message == "Missing token"


def test_forbidden_error():
    err = ForbiddenError()
    assert err.code == ErrorCode.FORBIDDEN
    assert err.status_code == 403


def test_not_found_error():
    err = NotFoundError("Trip not found")
    assert err.code == ErrorCode.NOT_FOUND
    assert err.status_code == 404
    assert err.message == "Trip not found"


def test_already_exists_error():
    err = AlreadyExistsError("Already a member")
    assert err.code == ErrorCode.ALREADY_EXISTS
    assert err.status_code == 409


def test_conflict_error_default_code():
    err = ConflictError("State conflict")
    assert err.code == ErrorCode.CONFLICT
    assert err.status_code == 409


def test_conflict_error_custom_code():
    err = ConflictError("Invite expired", code=ErrorCode.INVITE_EXPIRED)
    assert err.code == ErrorCode.INVITE_EXPIRED
    assert err.status_code == 409


def test_internal_server_error():
    err = InternalServerError()
    assert err.code == ErrorCode.INTERNAL_SERVER_ERROR
    assert err.status_code == 500


def test_app_error_is_exception():
    err = ValidationError("bad input")
    with pytest.raises(ValidationError):
        raise err
