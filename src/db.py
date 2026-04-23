"""Database connection and migrations - INFRA-BE-001.2"""

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg

_DATABASE_URL = os.environ.get("DATABASE_URL", "")
_MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"


@contextmanager
def get_connection():
    with psycopg.connect(_DATABASE_URL) as conn:
        yield conn


def run_migrations() -> None:
    sql_files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    with get_connection() as conn:
        for path in sql_files:
            conn.execute(path.read_text())
        conn.commit()
