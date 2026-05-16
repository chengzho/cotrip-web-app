import json
from dataclasses import dataclass, field
from typing import Any

from common.errors import UnauthorizedError, ValidationError


@dataclass
class ParsedRequest:
    method: str
    raw_path: str
    route_key: str
    path_parameters: dict[str, str]
    query_parameters: dict[str, str]
    body: "dict[str, Any] | None"
    request_id: str
    claims: dict[str, Any]


def parse_http_event(event: dict) -> ParsedRequest:
    rc = event.get("requestContext", {})
    http_ctx = rc.get("http", {})

    method = (http_ctx.get("method") or event.get("httpMethod") or "").upper()
    raw_path = http_ctx.get("path") or event.get("rawPath") or ""
    route_key = event.get("routeKey") or rc.get("routeKey") or ""

    path_parameters: dict[str, str] = dict(event.get("pathParameters") or {})
    query_parameters: dict[str, str] = dict(event.get("queryStringParameters") or {})

    raw_body = event.get("body")
    body: "dict[str, Any] | None" = None
    if raw_body:
        try:
            parsed = json.loads(raw_body)
            body = parsed if isinstance(parsed, dict) else None
        except (json.JSONDecodeError, ValueError):
            raise ValidationError("Request body contains invalid JSON")

    from common.auth import get_request_id, get_jwt_claims
    request_id = get_request_id(event)

    # Public routes have no JWT claims; return empty dict rather than raising.
    try:
        claims = get_jwt_claims(event)
    except (UnauthorizedError, Exception):
        claims = {}

    return ParsedRequest(
        method=method,
        raw_path=raw_path,
        route_key=route_key,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        body=body,
        request_id=request_id,
        claims=claims,
    )
