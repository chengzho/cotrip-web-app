import json
from typing import Any


_HEADERS = {"Content-Type": "application/json"}


def success_response(data: Any, status_code: int = 200, request_id: str = "") -> dict:
    body = {
        "success": True,
        "data": data,
        "error": None,
        "request_id": request_id,
    }
    return json_response(body, status_code)


def error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: str = "",
) -> dict:
    body = {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message},
        "request_id": request_id,
    }
    return json_response(body, status_code)


def json_response(body: Any, status_code: int = 200) -> dict:
    return {
        "statusCode": status_code,
        "headers": _HEADERS,
        "body": json.dumps(body, default=str),
    }
