"""
Apply SQL migration files in backend/migrations/ to a PostgreSQL database.

Reads connection details from environment variables:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

Migration files are applied in lexicographic order (001_..., 002_..., etc.).
Each file is committed individually. On failure the current file is rolled back,
an error message is printed, and the script exits non-zero.

Usage:
  python scripts/apply_migrations.py
  python scripts/apply_migrations.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

import psycopg2

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

_REQUIRED = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


def _load_config() -> dict:
    missing = [v for v in _REQUIRED if not os.environ.get(v, "").strip()]
    if missing:
        print(
            f"ERROR: Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        port = int(os.environ["DB_PORT"].strip())
    except ValueError:
        print(
            f"ERROR: DB_PORT must be an integer, got: {os.environ['DB_PORT']!r}",
            file=sys.stderr,
        )
        sys.exit(1)
    return {
        "host": os.environ["DB_HOST"].strip(),
        "port": port,
        "dbname": os.environ["DB_NAME"].strip(),
        "user": os.environ["DB_USER"].strip(),
        "password": os.environ["DB_PASSWORD"].strip(),
    }


def _discover_migrations() -> list[Path]:
    if not MIGRATIONS_DIR.is_dir():
        print(f"ERROR: Migrations directory not found: {MIGRATIONS_DIR}", file=sys.stderr)
        sys.exit(1)
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print(
            f"ERROR: No .sql migration files found in {MIGRATIONS_DIR}",
            file=sys.stderr,
        )
        sys.exit(1)
    return files


def _run(config: dict, migrations: list[Path], dry_run: bool) -> None:
    print(
        f"Target: {config['host']}:{config['port']}/{config['dbname']}"
        f" (user: {config['user']})"
    )

    if dry_run:
        print("DRY RUN — no SQL will be executed.")
        for path in migrations:
            print(f"  {path.name}")
        return

    conn = psycopg2.connect(**config)
    try:
        conn.autocommit = False
        for path in migrations:
            print(f"Applying {path.name}...", end=" ", flush=True)
            sql = path.read_text(encoding="utf-8")
            cur = conn.cursor()
            try:
                cur.execute(sql)
                conn.commit()
                print("ok")
            except Exception as exc:
                conn.rollback()
                print("FAILED", flush=True)
                print(
                    f"ERROR: {path.name} failed: {exc}",
                    file=sys.stderr,
                )
                sys.exit(1)
            finally:
                cur.close()
        print(f"Done. {len(migrations)} migration(s) applied.")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List migration files that would be applied without executing any SQL.",
    )
    args = parser.parse_args()

    config = _load_config()
    migrations = _discover_migrations()
    _run(config, migrations, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
