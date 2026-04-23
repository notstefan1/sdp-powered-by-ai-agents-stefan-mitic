"""Auth Service - AUTH-BE-001.1"""

import hashlib
import os
import uuid

import jwt

_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-32-bytes-minimum!")  # nosec


class UserStore:
    """In-memory user store (used in tests)."""

    def __init__(self):
        self._users: dict[str, dict] = {}  # username -> {user_id, password_hash}
        self._by_id: dict[str, str] = {}  # user_id -> username

    def create(self, username: str, password: str) -> str:
        user_id = f"u-{uuid.uuid4().hex[:8]}"
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self._users[username] = {"user_id": user_id, "password_hash": pw_hash}
        self._by_id[user_id] = username
        return user_id

    def create_with_id(self, user_id: str, username: str, password: str) -> None:
        if username in self._users:
            raise ValueError("username_taken")
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self._users[username] = {"user_id": user_id, "password_hash": pw_hash}
        self._by_id[user_id] = username

    def get(self, username: str):
        return self._users.get(username)

    def get_by_id(self, user_id: str):
        username = self._by_id.get(user_id)
        if not username:
            return None
        return {"user_id": user_id, "username": username}

    def search(self, query: str) -> list[dict]:
        return [
            {"user_id": v["user_id"], "username": k}
            for k, v in self._users.items()
            if query.lower() in k.lower()
        ]

    def all_user_ids(self) -> list[str]:
        return list(self._by_id.keys())


class DbUserStore:
    """PostgreSQL-backed user store."""

    def create_with_id(self, user_id: str, username: str, password: str) -> None:
        from src.db import get_connection

        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        with get_connection() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (user_id, username, password_hash)"
                    " VALUES (%s, %s, %s)",
                    (user_id, username, pw_hash),
                )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise ValueError("username_taken") from e

    def get(self, username: str):
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, password_hash FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return {"user_id": row[0], "password_hash": row[1]}

    def get_by_id(self, user_id: str):
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username FROM users WHERE user_id = %s", (user_id,)
            )
            row = cur.fetchone()
        return {"user_id": row[0], "username": row[1]} if row else None

    def search(self, query: str) -> list[dict]:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username FROM users WHERE username ILIKE %s LIMIT 20",
                (f"%{query}%",),
            )
            return [{"user_id": r[0], "username": r[1]} for r in cur.fetchall()]

    def all_user_ids(self) -> list[str]:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            return [r[0] for r in cur.fetchall()]


class AuthService:
    def __init__(self, store: UserStore):
        self._store = store

    def login(self, username: str, password: str) -> dict:
        user = self._store.get(username)
        if not user:
            raise ValueError("invalid_credentials")
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != pw_hash:
            raise ValueError("invalid_credentials")
        token = jwt.encode(
            {"sub": user["user_id"], "username": username}, _SECRET, algorithm="HS256"
        )
        return {"token": token, "user_id": user["user_id"], "username": username}

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, _SECRET, algorithms=["HS256"])
            return payload["sub"]
        except Exception as err:
            raise ValueError("invalid_token") from err
