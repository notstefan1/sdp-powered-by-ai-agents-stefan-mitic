"""Tests for HTTP API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api import create_app


@pytest.fixture()
def client():
    return TestClient(create_app())


def _register_and_login(client, username="alice"):
    client.post(
        "/register",
        json={"username": username, "password": "pass"},  # pragma: allowlist secret
    )
    resp = client.post(
        "/auth/login",
        json={"username": username, "password": "pass"},  # pragma: allowlist secret
    )
    return resp.json()["token"]


def test_post_register_creates_user(client):
    resp = client.post(
        "/register",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "alice"


def test_post_login_returns_token(client):
    client.post(
        "/register",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_post_posts_creates_post(client):
    token = _register_and_login(client)
    resp = client.post(
        "/posts",
        json={"text": "Hello world"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert "post_id" in resp.json()


def test_get_feed_returns_posts(client):
    token = _register_and_login(client)
    client.post(
        "/posts",
        json={"text": "Hello feed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.get("/feed", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "posts" in resp.json()


def test_get_feed_returns_own_posts(client):
    # GIVEN - a user posts something
    token = _register_and_login(client)
    client.post(
        "/posts",
        json={"text": "My own post"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # WHEN - they view their feed
    resp = client.get("/feed", headers={"Authorization": f"Bearer {token}"})

    # THEN - their own post appears with text
    posts = resp.json()["posts"]
    assert len(posts) > 0
    assert posts[0]["text"] == "My own post"


def test_post_messages_sends_dm(client):
    token_alice = _register_and_login(client, "alice")
    bob_id = client.post(
        "/register",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    ).json()["user_id"]

    resp = client.post(
        "/messages",
        json={"recipient_id": bob_id, "text": "Hey Bob"},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert resp.status_code == 201
    assert "message_id" in resp.json()


def test_get_root_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_health_returns_status(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "postgres" in body
    assert "redis" in body
    assert body["status"] in ("ok", "degraded")


def test_get_post_by_id(client):
    # GIVEN - Story: POST-BE-002.1
    token = _register_and_login(client)
    post_id = client.post(
        "/posts",
        json={"text": "Permalink test"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["post_id"]

    # WHEN
    resp = client.get(f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"})

    # THEN
    assert resp.status_code == 200
    assert resp.json()["text"] == "Permalink test"


def test_get_post_by_id_not_found(client):
    # GIVEN - Story: POST-STORY-002-S2
    token = _register_and_login(client)

    # WHEN
    resp = client.get(
        "/posts/nonexistent", headers={"Authorization": f"Bearer {token}"}
    )

    # THEN
    assert resp.status_code == 404
