import uuid
from unittest.mock import MagicMock, patch

import pytest

from common.errors import UnauthorizedError
from common.repositories.user_repository import (
    create_user,
    find_user_by_cognito_sub,
    resolve_or_create_user,
)


def _mock_conn(fetchone_result=None):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone_result
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn, cur


class TestFindUserByCognitoSub:
    def test_returns_dict_when_found(self):
        uid = str(uuid.uuid4())
        row = (uid, "sub-1", "a@b.com", "Alice", "2024-01-01", "2024-01-01")
        conn, _ = _mock_conn(fetchone_result=row)
        result = find_user_by_cognito_sub(conn, "sub-1")
        assert result["email"] == "a@b.com"
        assert result["display_name"] == "Alice"

    def test_returns_none_when_not_found(self):
        conn, _ = _mock_conn(fetchone_result=None)
        assert find_user_by_cognito_sub(conn, "missing-sub") is None


class TestCreateUser:
    def test_inserts_and_returns_user(self):
        uid = str(uuid.uuid4())
        row = (uid, "sub-2", "b@b.com", "Bob", "2024-01-02", "2024-01-02")
        conn, _ = _mock_conn(fetchone_result=row)
        result = create_user(conn, "sub-2", "b@b.com", "Bob")
        assert result["cognito_sub"] == "sub-2"
        conn.commit.assert_called_once()


class TestResolveOrCreateUser:
    def _claims(self, sub="sub-x", email="x@y.com", name="Xavier"):
        return {"sub": sub, "email": email, "name": name}

    def test_returns_existing_user(self):
        uid = str(uuid.uuid4())
        row = (uid, "sub-x", "x@y.com", "Xavier", "2024-01-01", "2024-01-01")
        conn, _ = _mock_conn(fetchone_result=row)
        result = resolve_or_create_user(conn, self._claims())
        assert result["cognito_sub"] == "sub-x"

    def test_creates_user_when_not_found(self):
        uid = str(uuid.uuid4())
        new_row = (uid, "sub-new", "new@y.com", "New User", "2024-06-01", "2024-06-01")
        cur = MagicMock()
        cur.__enter__ = lambda s: s
        cur.__exit__ = MagicMock(return_value=False)
        # First call (find): returns None; second call (create): returns new_row
        cur.fetchone.side_effect = [None, new_row]
        conn = MagicMock()
        conn.cursor.return_value = cur
        result = resolve_or_create_user(conn, {"sub": "sub-new", "email": "new@y.com"})
        assert result["email"] == "new@y.com"
        conn.commit.assert_called_once()

    def test_raises_unauthorized_when_no_sub(self):
        conn, _ = _mock_conn()
        with pytest.raises(UnauthorizedError):
            resolve_or_create_user(conn, {})

    def test_raises_unauthorized_when_no_email(self):
        conn, _ = _mock_conn()
        with pytest.raises(UnauthorizedError):
            resolve_or_create_user(conn, {"sub": "sub-z"})
