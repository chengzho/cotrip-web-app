import json


def make_event(
    method: str,
    path: str,
    route_key: str,
    *,
    sub: str = "",
    email: str = "",
    path_params: dict = None,
    query_params: dict = None,
    body: dict = None,
    public: bool = False,
) -> dict:
    """Build a minimal API Gateway HTTP API v2-style event dict."""
    event = {
        "requestContext": {
            "requestId": "req-integration",
            "http": {"method": method, "path": path},
        },
        "routeKey": route_key,
        "pathParameters": path_params,
        "queryStringParameters": query_params,
        "body": json.dumps(body) if body is not None else None,
    }
    if not public:
        event["requestContext"]["authorizer"] = {
            "jwt": {"claims": {"sub": sub, "email": email}}
        }
    return event


def assert_ok(resp: dict, expected_status: int = 200) -> dict:
    """Assert successful response and return the data payload."""
    parsed = json.loads(resp["body"])
    assert resp["statusCode"] == expected_status, (
        f"Expected HTTP {expected_status}, got {resp['statusCode']}: {parsed}"
    )
    assert parsed["success"] is True
    return parsed["data"]


def assert_err(resp: dict, expected_status: int, expected_code: str = None) -> dict:
    """Assert error response and return the error payload."""
    parsed = json.loads(resp["body"])
    assert resp["statusCode"] == expected_status, (
        f"Expected HTTP {expected_status}, got {resp['statusCode']}: {parsed}"
    )
    assert parsed["success"] is False
    if expected_code:
        assert parsed["error"]["code"] == expected_code, (
            f"Expected error code {expected_code!r}, got {parsed['error']['code']!r}"
        )
    return parsed["error"]
