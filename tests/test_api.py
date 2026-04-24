"""HTTP API endpoint tests - story-level scenarios."""

import pytest
from fastapi.testclient import TestClient

from src.api import create_app

_PASS = "pass"  # pragma: allowlist secret
_SECRET = "secret123"  # pragma: allowlist secret


@pytest.fixture()
def client():
    return TestClient(create_app())


def test_infra_be_001_2_s1__create_app_raises_on_bad_db_url(monkeypatch):
    # GIVEN - DATABASE_URL is set but points to an unreachable host
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://bad:bad@localhost:1/bad",  # pragma: allowlist secret
    )
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.delenv("TESTING", raising=False)
    # WHEN / THEN - should propagate the DB error, not silently fall back
    import psycopg

    with pytest.raises(psycopg.OperationalError):
        create_app()


def _register_and_login(client, username="alice"):
    client.post("/register", json={"username": username, "password": _PASS})
    return client.post(
        "/auth/login", json={"username": username, "password": _PASS}
    ).json()["token"]


def test_auth_story_001_s1__successful_login_returns_token(client):
    # GIVEN - Story: AUTH-STORY-001, Scenario: S1
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


def test_auth_story_001_s4__protected_endpoint_rejects_missing_token(client):
    # GIVEN - Story: AUTH-STORY-001, Scenario: S4
    # WHEN - no Authorization header
    resp = client.get("/feed")

    # THEN - 401 or 403 depending on FastAPI version (no credentials = unauthorized)
    assert resp.status_code in (401, 403)


def test_user_story_002_s1__successful_registration(client):
    # GIVEN - Story: USER-STORY-002, Scenario: S1
    # WHEN
    resp = client.post(
        "/register",
        json={"username": "alice", "password": "secret123"},  # pragma: allowlist secret
    )

    # THEN
    assert resp.status_code == 201
    assert resp.json()["username"] == "alice"
    assert "user_id" in resp.json()


def test_user_story_002_s2__duplicate_username_rejected(client):
    # GIVEN - Story: USER-STORY-002, Scenario: S2
    client.post("/register", json={"username": "alice", "password": _PASS})

    # WHEN
    resp = client.post(
        "/register",
        json={"username": "alice", "password": "pass"},  # pragma: allowlist secret
    )

    # THEN
    assert resp.status_code == 409


def test_post_story_001_s1__valid_post_persisted_and_201_returned(client):
    # GIVEN - Story: POST-STORY-001, Scenario: S1
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


def test_feed_story_001_s1__feed_returned_with_own_posts(client):
    # GIVEN - Story: FEED-STORY-001, Scenario: S1
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
    assert any(p["text"] == "Hello feed" for p in resp.json()["posts"])


def test_msg_story_001_s1__dm_sent_and_message_id_returned(client):
    # GIVEN - Story: MSG-STORY-001, Scenario: S1
    token_alice = _register_and_login(client, "alice")
    bob_id = client.post(
        "/register",
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


def test_infra_fe_001_1_s1__health_endpoint_returns_ok(client):
    # GIVEN - Story: INFRA-FE-001.1, Scenario: S1
    # WHEN
    resp = client.get("/health")

    # THEN
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("ok", "degraded")
    assert "postgres" in body
    assert "redis" in body


def test_infra_fe_001_1_s1__root_serves_html(client):
    # GIVEN - Story: INFRA-FE-001.1 - frontend served from /
    # WHEN
    resp = client.get("/")

    # THEN
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_post_story_002_s1__permalink_returns_post(client):
    # GIVEN - Story: POST-STORY-002, Scenario: S1
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


def test_post_story_002_s2__permalink_404_for_missing_post(client):
    # GIVEN - Story: POST-STORY-002, Scenario: S2
    token = _register_and_login(client)

    # WHEN
    resp = client.get(
        "/posts/nonexistent", headers={"Authorization": f"Bearer {token}"}
    )

    # THEN
    assert resp.status_code == 404


def test_user_story_003_s1__profile_shows_user_info_and_counts(client):
    # GIVEN - Story: USER-STORY-003, Scenario: S1 & S2
    token_alice = _register_and_login(client, "alice")
    bob_id = client.post(
        "/register",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    ).json()["user_id"]
    client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {token_alice}"},
    )

    # WHEN
    resp = client.get(
        f"/users/{bob_id}", headers={"Authorization": f"Bearer {token_alice}"}
    )

    # THEN
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "bob"
    assert body["follower_count"] == 1
    assert body["is_following"] is True


def test_user_story_003_s3__unknown_username_returns_404(client):
    # GIVEN - Story: USER-STORY-003, Scenario: S3
    token = _register_and_login(client)

    # WHEN
    resp = client.get(
        "/users/nonexistent-id", headers={"Authorization": f"Bearer {token}"}
    )

    # THEN
    assert resp.status_code == 404


def test_feed_story_001_s2__unfollow_removes_posts_from_feed(client):
    # GIVEN - Story: USER-STORY-001-S2 / FEED-STORY-001
    token_alice = _register_and_login(client, "alice")
    bob_id = client.post(
        "/register",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    ).json()["user_id"]
    bob_token = client.post(
        "/auth/login",
        json={"username": "bob", "password": "pass"},  # pragma: allowlist secret
    ).json()["token"]
    client.post(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    client.post(
        "/posts",
        json={"text": "Bob post"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    feed_before = client.get(
        "/feed", headers={"Authorization": f"Bearer {token_alice}"}
    ).json()["posts"]
    assert any(p["text"] == "Bob post" for p in feed_before)

    # WHEN
    client.delete(
        f"/users/{bob_id}/follow",
        headers={"Authorization": f"Bearer {token_alice}"},
    )

    # THEN
    feed_after = client.get(
        "/feed", headers={"Authorization": f"Bearer {token_alice}"}
    ).json()["posts"]
    assert not any(p["text"] == "Bob post" for p in feed_after)
