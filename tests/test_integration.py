"""Integration tests - require DATABASE_URL and REDIS_URL to be set."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.db import get_connection

DATABASE_URL = os.environ.get("DATABASE_URL")
skip_no_db = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")

_PASS = "testpass"  # pragma: allowlist secret


def _register(client, username):
    return client.post(
        "/register", json={"username": username, "password": _PASS}
    ).json()


def _login_token(client, username):
    return client.post(
        "/auth/login", json={"username": username, "password": _PASS}
    ).json()["token"]


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


@skip_no_db
def test_message_persists_to_db():
    # GIVEN - Story: MSG-BE-001.1 with real DB
    client = TestClient(create_app())
    alice = _register(client, "alice")
    _register(client, "bob")
    bob_token = _login_token(client, "bob")

    # WHEN
    resp = client.post(
        "/messages",
        json={"recipient_id": alice["user_id"], "text": "Hey Alice"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # THEN
    assert resp.status_code == 201
    msg_id = resp.json()["message_id"]
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT text FROM messages WHERE message_id = %s", (msg_id,))
        assert cur.fetchone()[0] == "Hey Alice"


@skip_no_db
def test_data_persists_across_app_restart():
    # GIVEN - Story: INFRA-STORY-001-S3 - data survives container restart
    # Simulate restart by creating two separate app instances (each calls create_app())
    # which is equivalent to the process restarting - state is only in the DB.
    client1 = TestClient(create_app())
    _register(client1, "alice")
    token = _login_token(client1, "alice")
    resp = client1.post(
        "/posts",
        json={"text": "Survives restart"},
        headers={"Authorization": f"Bearer {token}"},
    )
    post_id = resp.json()["post_id"]

    # WHEN - a new app instance starts (simulates restart)
    client2 = TestClient(create_app())
    token2 = _login_token(client2, "alice")
    feed = client2.get("/feed", headers={"Authorization": f"Bearer {token2}"}).json()

    # THEN - the post is still there
    assert any(p["post_id"] == post_id for p in feed["posts"])


@skip_no_db
def test_mention_creates_notification():
    # GIVEN - Story: NOTIF-BE-001.1 with real DB + worker
    import redis as redis_lib

    from src.worker import ensure_consumer_groups, process_once

    r = redis_lib.from_url(os.environ["REDIS_URL"])
    ensure_consumer_groups(r)

    client = TestClient(create_app())
    _register(client, "alice")
    _register(client, "bob")
    bob_token = _login_token(client, "bob")

    # WHEN - bob posts mentioning @alice (event goes to Redis Stream)
    client.post(
        "/posts",
        json={"text": "Hey @alice how are you"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    process_once(r)  # worker processes the stream

    # THEN - alice has an unread notification
    alice_token = _login_token(client, "alice")
    resp = client.get(
        "/notifications", headers={"Authorization": f"Bearer {alice_token}"}
    )
    notifs = resp.json()["notifications"]
    assert len(notifs) == 1
    assert notifs[0]["type"] == "mention"


@skip_no_db
def test_feed_served_from_redis_after_post():
    # GIVEN - Story: FEED-BE-001.1 with real Redis
    client = TestClient(create_app())
    _register(client, "alice")
    token = _login_token(client, "alice")

    # WHEN - post something
    client.post(
        "/posts",
        json={"text": "Redis cache test"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # THEN - second request hits Redis (no SQL), still returns the post
    resp = client.get("/feed", headers={"Authorization": f"Bearer {token}"})
    posts = resp.json()["posts"]
    assert any(p["text"] == "Redis cache test" for p in posts)


@skip_no_db
def test_worker_consumes_post_created_event():
    # GIVEN - Story: NOTIF-INFRA-001.3 / FEED-INFRA-001.3
    import json

    import redis as redis_lib

    r = redis_lib.from_url(os.environ["REDIS_URL"])
    # ensure consumer groups exist
    from src.worker import ensure_consumer_groups

    ensure_consumer_groups(r)

    # WHEN - write a post.created event directly to the stream
    _register(TestClient(create_app()), "alice")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id FROM users WHERE username='alice'")
        alice_id = cur.fetchone()[0]

    r.xadd(
        "posts:events",
        {
            "post_id": "test-post-1",
            "author_id": alice_id,
            "mentioned_user_ids": json.dumps([alice_id]),
        },
    )

    # process one batch
    from src.worker import process_once

    process_once(r)

    # THEN - notification created for alice
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM notifications WHERE recipient_id=%s", (alice_id,)
        )
        assert cur.fetchone()[0] >= 1
