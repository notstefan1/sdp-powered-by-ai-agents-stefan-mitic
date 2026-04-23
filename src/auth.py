"""Auth Service - AUTH-BE-001.1"""

import hashlib
import os
import uuid

import jwt

_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-32-bytes-minimum!")  # nosec


class UserStore:
    def __init__(self):
        self._users = {}

    def create(self, username: str, password: str) -> str:
        user_id = f"u-{uuid.uuid4().hex[:8]}"
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self._users[username] = {"user_id": user_id, "password_hash": pw_hash}
        return user_id

    def get(self, username: str):
        return self._users.get(username)


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
