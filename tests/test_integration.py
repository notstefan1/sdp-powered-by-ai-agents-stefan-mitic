"""Integration tests - require DATABASE_URL and REDIS_URL to be set."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.db import get_connection, run_migrations

DATABASE_URL = os.environ.get("DATABASE_URL")
skip_no_db = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")

_TRUNCATE = (
    "TRUNCATE users, follows, posts, notifications, messages"
    " RESTART IDENTITY CASCADE"
)


@pytest.fixture(autouse=True)
def clean_db():
    """Truncate all tables before each integration test."""
    if not DATABASE_URL:
        yield
        return
    run_migrations()
    with get_connection() as conn:
        conn.execute(_TRUNCATE)
        conn.commit()
    yield


@skip_no_db
def test_register_persists_to_db():
    # GIVEN - Story: USER-BE-002.1 with real DB
    client = TestClient(create_app())

    # WHEN
    resp = client.post(
        "/register",
        json={"username": "alice", "password": "pass"},  # pragma: allowlist secret
    )

    # THEN
    assert resp.status_code == 201
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE username = 'alice'")
        row = cur.fetchone()
    assert row is not None
    assert row[0] == "alice"
