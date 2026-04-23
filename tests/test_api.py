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


def test_post_messages_sends_dm():
    # GIVEN - Story: MSG-BE-001.1, HTTP layer
    client = TestClient(create_app())
    token_alice = _register_and_login(client)
    # register bob so alice can DM him
    client.post(
        "/register",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    )
    bob_id = client.post(
        "/auth/login",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    ).json()["user_id"]

    # WHEN
    resp = client.post(
        "/messages",
        json={"recipient_id": bob_id, "text": "Hey Bob"},
        headers={"Authorization": f"Bearer {token_alice}"},
    )

    # THEN
    assert resp.status_code == 201
    assert "message_id" in resp.json()


def test_get_root_serves_html():
    # GIVEN - Story: INFRA-FE-001.1 / minimal frontend
    client = TestClient(create_app())

    # WHEN
    resp = client.get("/")

    # THEN
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
