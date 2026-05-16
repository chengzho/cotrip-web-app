import pytest
from common.errors import ValidationError
from common.request import ParsedRequest, parse_http_event


def _base_event(**overrides):
    event = {
        "requestContext": {
            "requestId": "req-123",
            "http": {"method": "GET", "path": "/trips"},
            "authorizer": {"jwt": {"claims": {"sub": "user-sub-1", "email": "a@b.com"}}},
        },
        "routeKey": "GET /trips",
        "pathParameters": None,
        "queryStringParameters": None,
        "body": None,
    }
    event.update(overrides)
    return event


class TestParseHttpEvent:
    def test_basic_get(self):
        req = parse_http_event(_base_event())
        assert req.method == "GET"
        assert req.raw_path == "/trips"
        assert req.route_key == "GET /trips"
        assert req.body is None
        assert req.request_id == "req-123"
        assert req.claims["sub"] == "user-sub-1"

    def test_path_parameters_extracted(self):
        event = _base_event(
            routeKey="GET /trips/{tripId}",
            pathParameters={"tripId": "abc-123"},
        )
        req = parse_http_event(event)
        assert req.path_parameters == {"tripId": "abc-123"}

    def test_query_parameters_extracted(self):
        event = _base_event(queryStringParameters={"scope": "past"})
        req = parse_http_event(event)
        assert req.query_parameters == {"scope": "past"}

    def test_json_body_parsed(self):
        import json
        event = _base_event(body=json.dumps({"title": "My Trip"}))
        req = parse_http_event(event)
        assert req.body == {"title": "My Trip"}

    def test_invalid_json_body_raises(self):
        event = _base_event(body="{invalid}")
        with pytest.raises(ValidationError):
            parse_http_event(event)

    def test_non_dict_json_body_ignored(self):
        import json
        event = _base_event(body=json.dumps([1, 2, 3]))
        req = parse_http_event(event)
        assert req.body is None

    def test_missing_claims_returns_empty_dict(self):
        event = _base_event()
        del event["requestContext"]["authorizer"]
        req = parse_http_event(event)
        assert req.claims == {}

    def test_none_path_parameters_becomes_empty_dict(self):
        req = parse_http_event(_base_event(pathParameters=None))
        assert req.path_parameters == {}

    def test_none_query_parameters_becomes_empty_dict(self):
        req = parse_http_event(_base_event(queryStringParameters=None))
        assert req.query_parameters == {}

    def test_method_uppercased(self):
        event = _base_event()
        event["requestContext"]["http"]["method"] = "post"
        req = parse_http_event(event)
        assert req.method == "POST"
