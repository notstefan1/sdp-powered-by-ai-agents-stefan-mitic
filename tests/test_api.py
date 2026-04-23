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
