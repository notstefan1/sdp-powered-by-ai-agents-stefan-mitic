"""FastAPI application - HTTP layer wiring all services."""

import os
import time
from pathlib import Path

import redis as redis_lib
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.auth import AuthService, DbUserStore, UserStore
from src.db import get_connection, run_migrations
from src.feed import FeedCache, FeedService
from src.messaging import DbMessageRepository, MessageRepository, MessagingService
from src.notification import (
    DbNotificationRepository,
    NotificationRepository,
    NotificationService,
)
from src.post import (
    DbPostRepository,
    EventEmitter,
    MentionParser,
    PostRepository,
    PostService,
)
from src.user import DbFollowRepository, FollowRepository, UserService

_STATIC = Path(__file__).parent.parent / "static"
_bearer = HTTPBearer()

TESTING = os.environ.get("TESTING") == "1"


class _Auth:
    """Callable dependency wrapper - avoids B008 by deferring Depends to instance."""

    def __init__(self, auth_service: AuthService):
        self._svc = auth_service

    def __call__(self, creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
        try:
            return self._svc.decode_token(creds.credentials)
        except ValueError as e:
            raise HTTPException(status_code=401, detail="unauthorized") from e


def create_app() -> FastAPI:
    db_url = os.environ.get("DATABASE_URL")
    redis_url = os.environ.get("REDIS_URL")

    if not TESTING:
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL is not set. "
                "Start postgres and set DATABASE_URL, "
                "or set TESTING=1 for in-memory mode."
            )
        if not redis_url:
            raise RuntimeError(
                "REDIS_URL is not set. "
                "Start redis and set REDIS_URL, "
                "or set TESTING=1 for in-memory mode."
            )

    app = FastAPI()

    if db_url:
        try:
            run_migrations()
            user_store = DbUserStore()
            follow_repo = DbFollowRepository()
            post_repo = DbPostRepository()
            msg_repo = DbMessageRepository()
            notif_repo = DbNotificationRepository()
            # seed known_users from DB so messaging works for existing users
            known_users = set(user_store.all_user_ids())
        except Exception:
            user_store = UserStore()
            follow_repo = FollowRepository()
            post_repo = PostRepository()
            msg_repo = MessageRepository()
            notif_repo = NotificationRepository()
            known_users = set()
    else:
        user_store = UserStore()
        follow_repo = FollowRepository()
        post_repo = PostRepository()
        msg_repo = MessageRepository()
        notif_repo = NotificationRepository()
        known_users = set()

    user_service = UserService(follow_repo, known_users=known_users)
    auth_service = AuthService(user_store)
    emitter = EventEmitter()
    post_service = PostService(post_repo, emitter, MentionParser({}))
    feed_service = FeedService(FeedCache(), follow_repo, post_repo)
    notif_service = NotificationService(notif_repo)
    msg_service = MessagingService(msg_repo, user_service._users, emitter)

    current_user = _Auth(auth_service)

    class UserBody(BaseModel):
        username: str
        password: str

    @app.post("/register", status_code=201)
    def register(body: UserBody):
        try:
            result = user_service.register(body.username, "")
            user_store.create_with_id(result["user_id"], body.username, body.password)
            return result
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e

    @app.post("/auth/login")
    def login(body: UserBody):
        try:
            return auth_service.login(body.username, body.password)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e

    # --- Users ---
    @app.get("/users/search")
    def search_users(q: str, user_id: str = Depends(current_user)):
        if not hasattr(user_store, "search"):
            return {"users": []}
        return {"users": user_store.search(q)}

    @app.get("/users/{uid}")
    def get_user(uid: str, user_id: str = Depends(current_user)):
        if not hasattr(user_store, "get_by_id"):
            raise HTTPException(status_code=404, detail="not_found")
        u = user_store.get_by_id(uid)
        if not u:
            raise HTTPException(status_code=404, detail="not_found")
        followers = follow_repo.followers_of(uid)
        following = follow_repo.followees_of(uid)
        return {
            **u,
            "follower_count": len(followers),
            "following_count": len(following),
            "is_following": user_id in followers,
        }

    # --- Posts ---
    class PostBody(BaseModel):
        text: str

    @app.post("/posts", status_code=201)
    def create_post(body: PostBody, user_id: str = Depends(current_user)):
        try:
            result = post_service.publish(user_id, body.text)
            ts = time.time()
            feed_service.fan_out(result["post_id"], user_id, ts)
            feed_service._cache.zadd(user_id, ts, result["post_id"])
            if emitter.events:
                notif_service.handle_post_created(emitter.events[-1])
            return result
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    @app.get("/feed")
    def get_feed(user_id: str = Depends(current_user)):
        post_ids = feed_service.get_feed(user_id)
        posts = []
        for pid in post_ids:
            p = post_repo.get(pid)
            if p is None:
                continue
            row = vars(p).copy()
            # resolve author username
            if hasattr(user_store, "get_by_id"):
                u = user_store.get_by_id(p.author_id)
                row["author_username"] = u["username"] if u else p.author_id
            else:
                row["author_username"] = p.author_id
            posts.append(row)
        return {"posts": posts}

    # --- Follow ---
    @app.post("/users/{followee_id}/follow", status_code=201)
    def follow(followee_id: str, user_id: str = Depends(current_user)):
        try:
            user_service.follow(user_id, followee_id)
            return {"status": "ok"}
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e

    @app.delete("/users/{followee_id}/follow", status_code=204)
    def unfollow(followee_id: str, user_id: str = Depends(current_user)):
        try:
            user_service.unfollow(user_id, followee_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    # --- Notifications ---
    @app.get("/notifications")
    def get_notifications(user_id: str = Depends(current_user)):
        notifs = notif_service.get_unread(user_id)
        result = []
        for n in notifs:
            row = vars(n).copy()
            if hasattr(user_store, "get_by_id") and n.author_id:
                u = user_store.get_by_id(n.author_id)
                row["author_username"] = u["username"] if u else n.author_id
            result.append(row)
        return {"notifications": result}

    @app.post("/notifications/{notification_id}/read", status_code=204)
    def mark_read(notification_id: str, user_id: str = Depends(current_user)):
        try:
            notif_service.mark_read(notification_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    # --- Messages ---
    class MessageBody(BaseModel):
        recipient_id: str
        text: str

    @app.post("/messages", status_code=201)
    def send_message(body: MessageBody, user_id: str = Depends(current_user)):
        try:
            return msg_service.send(user_id, body.recipient_id, body.text)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    @app.get("/messages/{other_id}")
    def get_conversation(other_id: str, user_id: str = Depends(current_user)):
        msgs = msg_service.get_conversation(user_id, other_id)
        return {"messages": [vars(m) for m in msgs]}

    # --- Health ---
    @app.get("/health")
    def health():
        pg_status = "ok"
        redis_status = "ok"
        if db_url:
            try:
                with get_connection() as conn:
                    conn.execute("SELECT 1")
            except Exception:
                pg_status = "error"
        if redis_url:
            try:
                redis_lib.from_url(redis_url).ping()
            except Exception:
                redis_status = "error"
        overall = "ok" if pg_status == "ok" and redis_status == "ok" else "degraded"
        return {"status": overall, "postgres": pg_status, "redis": redis_status}

    @app.get("/", response_class=FileResponse)
    def index():
        return str(_STATIC / "index.html")

    return app
