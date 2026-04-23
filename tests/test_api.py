"""Tests for HTTP API endpoints - register and login"""

from fastapi.testclient import TestClient

from src.api import create_app


def test_post_register_creates_user():
    # GIVEN - Story: USER-BE-002.1, HTTP layer
    client = TestClient(create_app())

    # WHEN
    resp = client.post("/register", json={"username": "alice", "password": "secret123"})

    # THEN
    assert resp.status_code == 201
    assert "user_id" in resp.json()
    assert resp.json()["username"] == "alice"


def test_post_login_returns_token():
    # GIVEN - Story: AUTH-BE-001.1, HTTP layer
    client = TestClient(create_app())
    client.post(
        "/register",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )

    # WHEN
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )

    # THEN
    assert resp.status_code == 200
    assert "token" in resp.json()


def _register_and_login(client):
    client.post(
        "/register",
        json={"username": "alice", "password": "pass"},  # pragma: allowlist secret
    )
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "pass"},  # pragma: allowlist secret
    )
    return resp.json()["token"]


def test_post_posts_creates_post():
    # GIVEN - Story: POST-BE-001.1, HTTP layer
    client = TestClient(create_app())
    token = _register_and_login(client)

    # WHEN
    resp = client.post(
        "/posts",
        json={"text": "Hello world"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # THEN
    assert resp.status_code == 201
    assert "post_id" in resp.json()


def test_get_feed_returns_posts():
    # GIVEN - Story: FEED-BE-001.1, HTTP layer
    client = TestClient(create_app())
    token = _register_and_login(client)
    client.post(
        "/posts",
        json={"text": "Hello feed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # WHEN
    resp = client.get("/feed", headers={"Authorization": f"Bearer {token}"})

    # THEN
    assert resp.status_code == 200
    assert "posts" in resp.json()
