"""Database connection and migrations - INFRA-BE-001.2"""

import os
import time
from contextlib import contextmanager
from pathlib import Path

import psycopg

_MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"


def _database_url() -> str:
    return os.environ.get("DATABASE_URL", "")


def _db_connect_retries() -> int:
    return int(os.environ.get("DB_CONNECT_RETRIES", "10"))


def _db_connect_retry_delay() -> float:
    return float(os.environ.get("DB_CONNECT_RETRY_DELAY", "1"))


@contextmanager
def get_connection():
    database_url = _database_url()
    retries = _db_connect_retries()
    retry_delay = _db_connect_retry_delay()
    last_error = None
    for attempt in range(retries):
        try:
            with psycopg.connect(database_url, connect_timeout=3) as conn:
                yield conn
                return
        except psycopg.OperationalError as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            time.sleep(retry_delay)
    raise last_error


def run_migrations() -> None:
    sql_files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    with get_connection() as conn:
        for path in sql_files:
            conn.execute(path.read_text())
        conn.commit()
