import pytest
import os
from unittest.mock import patch
from common.db import get_database_config, DatabaseConfig


_VALID_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "cotrip_dev",
    "DB_USER": "postgres",
    "DB_PASSWORD": "secret",
}


def test_get_database_config_success():
    with patch.dict(os.environ, _VALID_ENV, clear=False):
        config = get_database_config()
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.name == "cotrip_dev"
    assert config.user == "postgres"
    assert config.password == "secret"


def test_get_database_config_missing_variable():
    env = {k: v for k, v in _VALID_ENV.items() if k != "DB_PASSWORD"}
    for key in _VALID_ENV:
        partial = {k: v for k, v in _VALID_ENV.items() if k != key}
        patched = {k: "" for k in _VALID_ENV}
        patched.update(partial)
        with patch.dict(os.environ, patched, clear=False):
            with pytest.raises(EnvironmentError, match=key):
                get_database_config()


def test_get_database_config_invalid_port():
    env = {**_VALID_ENV, "DB_PORT": "not-a-number"}
    with patch.dict(os.environ, env, clear=False):
        with pytest.raises(EnvironmentError, match="DB_PORT"):
            get_database_config()


def test_database_config_safe_repr_excludes_password():
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        name="cotrip_dev",
        user="postgres",
        password="super-secret",
    )
    safe = config.safe_repr()
    assert "super-secret" not in safe
    assert "localhost" in safe
    assert "cotrip_dev" in safe


def test_get_database_config_port_parsed_as_int():
    with patch.dict(os.environ, _VALID_ENV, clear=False):
        config = get_database_config()
    assert isinstance(config.port, int)
