"""pytest configuration - enable in-memory mode for unit tests."""

import os

import pytest

# Unit tests run without real infrastructure.
# Integration tests are skipped unless DATABASE_URL is set (i.e. inside Docker).
if not os.environ.get("DATABASE_URL"):
    os.environ["TESTING"] = "1"

_TRUNCATE = (
    "TRUNCATE users, follows, posts, notifications, messages"
    " RESTART IDENTITY CASCADE"
)


@pytest.fixture(autouse=True)
def clean_db():
    """Truncate all tables before each test when running against a real DB."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        yield
        return
    from src.db import get_connection, run_migrations

    run_migrations()
    with get_connection() as conn:
        conn.execute(_TRUNCATE)
        conn.commit()
    yield
