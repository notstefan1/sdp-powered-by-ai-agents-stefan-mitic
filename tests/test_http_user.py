"""Tests for USER-BE-001.1, USER-BE-001.2, USER-BE-003.1, USER-BE-002.2 HTTP layer."""

from fastapi.testclient import TestClient

from src.api import create_app

_PASS = "pass"  # pragma: allowlist secret


def _setup(client):
    client.post("/register", json={"username": "alice", "password": _PASS})
    bob = client.post("/register", json={"username": "bob", "password": _PASS}).json()
    alice_token = client.post(
        "/auth/login", json={"username": "alice", "password": _PASS}
    ).json()["token"]
    return bob["user_id"], alice_token


def test_user_be_003_1_s1__get_by_username_via_http():
    # GIVEN - Story: USER-BE-003.1, Scenario: S1
    client = TestClient(create_app())
    _, alice_token = _setup(client)

    # WHEN
    resp = client.get(
        "/users/by-username/alice",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_user_be_003_1_s2__get_by_username_unknown_returns_404():
    # GIVEN - Story: USER-BE-003.1, Scenario: S2
    client = TestClient(create_app())
    _, alice_token = _setup(client)

    # WHEN
    resp = client.get(
        "/users/by-username/nobody",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 404


def test_user_be_002_2_s1__update_profile_via_http():
    # GIVEN - Story: USER-BE-002.2, Scenario: S1
    client = TestClient(create_app())
    _, alice_token = _setup(client)

    # WHEN
    resp = client.patch(
        "/users/me",
        json={"display_name": "Alice Smith"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Alice Smith"


def test_user_be_001_1_s1__follow_relationship_created_via_http():
    # GIVEN - Story: USER-BE-001.1, Scenario: S1
    client = TestClient(create_app())
    bob_id, alice_token = _setup(client)

    # WHEN
    resp = client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 201


def test_user_be_001_1_s2__duplicate_follow_returns_conflict_via_http():
    # GIVEN - Story: USER-BE-001.1, Scenario: S2
    client = TestClient(create_app())
    bob_id, alice_token = _setup(client)
    client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # WHEN - follow again
    resp = client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 409


def test_user_be_001_2_s1__unfollow_removes_relationship_via_http():
    # GIVEN - Story: USER-BE-001.2, Scenario: S1
    client = TestClient(create_app())
    bob_id, alice_token = _setup(client)
    client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # WHEN
    resp = client.delete(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # THEN
    assert resp.status_code == 204
