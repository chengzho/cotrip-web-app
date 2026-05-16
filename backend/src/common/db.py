import os
from dataclasses import dataclass
from typing import Optional

import psycopg2
import psycopg2.extensions

from common.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    def safe_repr(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.name} user={self.user}"


def get_database_config() -> DatabaseConfig:
    missing = []
    host = os.environ.get("DB_HOST", "")
    port_str = os.environ.get("DB_PORT", "")
    name = os.environ.get("DB_NAME", "")
    user = os.environ.get("DB_USER", "")
    password = os.environ.get("DB_PASSWORD", "")

    for var, val in (("DB_HOST", host), ("DB_PORT", port_str), ("DB_NAME", name),
                     ("DB_USER", user), ("DB_PASSWORD", password)):
        if not val:
            missing.append(var)

    if missing:
        raise EnvironmentError(f"Missing required database environment variables: {', '.join(missing)}")

    try:
        port = int(port_str)
    except ValueError:
        raise EnvironmentError(f"DB_PORT must be an integer, got: {port_str!r}")

    return DatabaseConfig(host=host, port=port, name=name, user=user, password=password)


def get_connection(
    config: Optional[DatabaseConfig] = None,
) -> psycopg2.extensions.connection:
    if config is None:
        config = get_database_config()
    logger.debug("Opening database connection: %s", config.safe_repr())
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        dbname=config.name,
        user=config.user,
        password=config.password,
    )
    return conn


def close_connection_if_needed(conn: Optional[psycopg2.extensions.connection]) -> None:
    if conn is not None and not conn.closed:
        try:
            conn.close()
        except Exception:
            logger.warning("Failed to close database connection cleanly")
