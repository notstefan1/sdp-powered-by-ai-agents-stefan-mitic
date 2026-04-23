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

_PASS = "testpass"  # pragma: allowlist secret


def _register(client, username):
    return client.post(
        "/register", json={"username": username, "password": _PASS}
    ).json()


def _login_token(client, username):
    return client.post(
        "/auth/login", json={"username": username, "password": _PASS}
    ).json()["token"]


@pytest.fixture(autouse=True)
def clean_db():
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
    resp = _register(client, "alice")

    # THEN
    assert resp["username"] == "alice"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE username = 'alice'")
        assert cur.fetchone()[0] == "alice"


@skip_no_db
def test_follow_persists_to_db():
    # GIVEN - Story: USER-BE-001.1 with real DB
    client = TestClient(create_app())
    alice = _register(client, "alice")
    _register(client, "bob")
    bob_token = _login_token(client, "bob")

    # WHEN
    resp = client.post(
        f"/users/{alice['user_id']}/follow",
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # THEN
    assert resp.status_code == 201
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM follows WHERE followee_id = %s", (alice["user_id"],))
        assert cur.fetchone() is not None


@skip_no_db
def test_post_persists_to_db():
    # GIVEN - Story: POST-BE-001.1 with real DB
    client = TestClient(create_app())
    _register(client, "alice")
    token = _login_token(client, "alice")

    # WHEN
    resp = client.post(
        "/posts",
        json={"text": "Hello world"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # THEN
    assert resp.status_code == 201
    post_id = resp.json()["post_id"]
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT text FROM posts WHERE post_id = %s", (post_id,))
        assert cur.fetchone()[0] == "Hello world"
