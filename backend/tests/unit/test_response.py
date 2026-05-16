import json
import pytest
from common.response import success_response, error_response, json_response


def test_success_response_envelope():
    result = success_response({"id": "abc"}, status_code=200, request_id="req-1")
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["success"] is True
    assert body["data"] == {"id": "abc"}
    assert body["error"] is None
    assert body["request_id"] == "req-1"


def test_success_response_201():
    result = success_response({"id": "new"}, status_code=201, request_id="req-2")
    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert body["success"] is True


def test_error_response_envelope():
    result = error_response("VALIDATION_ERROR", "title is required", 400, "req-3")
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "title is required"
    assert body["request_id"] == "req-3"


def test_error_response_500():
    result = error_response("INTERNAL_SERVER_ERROR", "unexpected", 500)
    assert result["statusCode"] == 500


def test_json_body_is_string():
    result = success_response({"x": 1})
    assert isinstance(result["body"], str)


def test_content_type_header():
    result = success_response({})
    assert result["headers"]["Content-Type"] == "application/json"


def test_json_response_serializes_non_serializable():
    from datetime import date
    result = json_response({"d": date(2026, 1, 1)}, 200)
    body = json.loads(result["body"])
    assert body["d"] == "2026-01-01"
