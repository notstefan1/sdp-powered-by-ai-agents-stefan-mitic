"""
Database seeder - creates demo users, posts, follows, and DMs.

Usage:
    docker compose run --rm \\
      -e DATABASE_URL=... -e REDIS_URL=... \\
      api python scripts/seed.py
"""

import os
import sys

# ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient

from src.api import create_app

BASE = "http://testserver"

USERS = [
    {"username": "alice", "password": "password123"},  # pragma: allowlist secret
    {"username": "bob", "password": "password123"},  # pragma: allowlist secret
    {"username": "carol", "password": "password123"},  # pragma: allowlist secret
]

POSTS = [
    ("alice", "Hello everyone! Excited to be here 🎉"),
    ("bob", "Hey @alice! Great to see you on here."),
    ("carol", "Just joined - this looks cool! @alice @bob"),
    ("alice", "Working on something interesting today..."),
    ("bob", "Anyone else think Redis Streams are underrated?"),
    ("carol", "Loving the feed feature. Fast! ⚡"),
]

FOLLOWS = [
    ("bob", "alice"),
    ("carol", "alice"),
    ("alice", "bob"),
    ("carol", "bob"),
    ("alice", "carol"),
]

DMS = [
    ("alice", "bob", "Hey Bob, great post about Redis!"),
    ("bob", "alice", "Thanks Alice! You should try it sometime."),
    ("carol", "alice", "Hi Alice, love your posts!"),
]


def seed():
    client = TestClient(create_app())
    tokens = {}
    user_ids = {}

    print("Seeding users...")
    for u in USERS:
        r = client.post("/register", json=u)
        if r.status_code == 409:
            print(f"  {u['username']} already exists, skipping")
        else:
            print(f"  created @{u['username']}")

        r = client.post("/auth/login", json=u)
        d = r.json()
        tokens[u["username"]] = d["token"]
        user_ids[u["username"]] = d["user_id"]

    print("Seeding follows...")
    for follower, followee in FOLLOWS:
        r = client.post(
            f"/users/{user_ids[followee]}/follow",
            headers={"Authorization": f"Bearer {tokens[follower]}"},
        )
        status = "ok" if r.status_code in (201, 409) else r.text
        print(f"  @{follower} -> @{followee}: {status}")

    print("Seeding posts...")
    for author, text in POSTS:
        r = client.post(
            "/posts",
            json={"text": text},
            headers={"Authorization": f"Bearer {tokens[author]}"},
        )
        print(f"  @{author}: {text[:50]}")

    print("Seeding DMs...")
    for sender, recipient, text in DMS:
        r = client.post(
            "/messages",
            json={"recipient_id": user_ids[recipient], "text": text},
            headers={"Authorization": f"Bearer {tokens[sender]}"},
        )
        print(f"  @{sender} -> @{recipient}: {text[:40]}")

    print("\nDone! Demo credentials:")
    for u in USERS:
        print(
            f"  username: {u['username']}  password: {u['password']}"
        )  # pragma: allowlist secret


if __name__ == "__main__":
    seed()
