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
