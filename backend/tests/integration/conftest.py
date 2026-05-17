import glob
import os

import psycopg2
import pytest

_INTEGRATION_ENABLED = bool(os.environ.get("COTRIP_RUN_INTEGRATION"))

_SKIP_REASON = "Set COTRIP_RUN_INTEGRATION=1 to run integration tests"


def pytest_collection_modifyitems(items, config):
    """Skip all integration tests unless COTRIP_RUN_INTEGRATION=1 is set."""
    if _INTEGRATION_ENABLED:
        return
    skip_mark = pytest.mark.skip(reason=_SKIP_REASON)
    for item in items:
        if "tests/integration" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip_mark)


_DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
_DB_PORT = int(os.environ.get("DB_PORT", "55432"))
_DB_NAME = os.environ.get("DB_NAME", "cotrip_integration")
_DB_USER = os.environ.get("DB_USER", "cotrip_it")
_DB_PASSWORD = os.environ.get("DB_PASSWORD", "cotrip_it_password")

_MIGRATIONS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "migrations")
)

_TRUNCATE_SQL = (
    "TRUNCATE users, trips, trip_members, trip_invites, "
    "trip_candidates, candidate_votes, itinerary_items CASCADE"
)


@pytest.fixture(scope="session")
def pg_conn():
    """Session-scoped direct DB connection. Applies migrations once."""
    conn = psycopg2.connect(
        host=_DB_HOST,
        port=_DB_PORT,
        dbname=_DB_NAME,
        user=_DB_USER,
        password=_DB_PASSWORD,
    )
    conn.autocommit = True

    migration_files = sorted(glob.glob(os.path.join(_MIGRATIONS_DIR, "*.sql")))
    assert migration_files, f"No migration files found in {_MIGRATIONS_DIR}"
    for path in migration_files:
        with open(path) as fh:
            sql = fh.read()
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            with conn.cursor() as cur:
                cur.execute(stmt)

    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_db(pg_conn):
    """Truncate all tables before every test for full isolation."""
    with pg_conn.cursor() as cur:
        cur.execute(_TRUNCATE_SQL)
    yield
