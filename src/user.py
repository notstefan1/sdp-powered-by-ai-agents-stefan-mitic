"""User Service - USER-BE-001.1, USER-BE-001.2, USER-BE-002.1"""

import uuid

from src.db import get_connection


class FollowRepository:
    def __init__(self):
        self._follows: set[tuple[str, str]] = set()

    def exists(self, follower_id: str, followee_id: str) -> bool:
        return (follower_id, followee_id) in self._follows

    def add(self, follower_id: str, followee_id: str) -> None:
        self._follows.add((follower_id, followee_id))

    def remove(self, follower_id: str, followee_id: str) -> None:
        self._follows.discard((follower_id, followee_id))

    def followers_of(self, followee_id: str) -> list[str]:
        return [f for f, fe in self._follows if fe == followee_id]

    def followees_of(self, follower_id: str) -> list[str]:
        return [fe for f, fe in self._follows if f == follower_id]


class DbFollowRepository:
    def exists(self, follower_id: str, followee_id: str) -> bool:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM follows WHERE follower_id=%s AND followee_id=%s",
                (follower_id, followee_id),
            )
            return cur.fetchone() is not None

    def add(self, follower_id: str, followee_id: str) -> None:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO follows (follower_id, followee_id) VALUES (%s, %s)",
                (follower_id, followee_id),
            )
            conn.commit()

    def remove(self, follower_id: str, followee_id: str) -> None:
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM follows WHERE follower_id=%s AND followee_id=%s",
                (follower_id, followee_id),
            )
            conn.commit()

    def followers_of(self, followee_id: str) -> list[str]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT follower_id FROM follows WHERE followee_id=%s", (followee_id,)
            )
            return [r[0] for r in cur.fetchall()]

    def followees_of(self, follower_id: str) -> list[str]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT followee_id FROM follows WHERE follower_id=%s", (follower_id,)
            )
            return [r[0] for r in cur.fetchall()]


class UserService:
    def __init__(self, repo: FollowRepository, known_users: set[str]):
        self._repo = repo
        self._users = known_users
        self._profiles: dict[str, dict] = {}

    def register(self, username: str, email: str) -> dict:
        """USER-BE-002.1 - create a new user; raises if username taken."""
        for p in self._profiles.values():
            if p["username"] == username:
                raise ValueError("username_taken")
        user_id = f"u-{uuid.uuid4().hex[:8]}"
        self._profiles[user_id] = {
            "user_id": user_id,
            "username": username,
            "email": email,
        }
        self._users.add(user_id)
        return {"user_id": user_id, "username": username}

    def follow(self, follower_id: str, followee_id: str) -> None:
        """USER-BE-001.1 - follow a user; raises if duplicate."""
        if self._repo.exists(follower_id, followee_id):
            raise ValueError("already_following")
        self._repo.add(follower_id, followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        """USER-BE-001.2 - unfollow a user; raises if not following."""
        if not self._repo.exists(follower_id, followee_id):
            raise ValueError("not_following")
        self._repo.remove(follower_id, followee_id)
