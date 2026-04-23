"""FastAPI application - HTTP layer wiring all services."""

import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.auth import AuthService, UserStore
from src.feed import FeedCache, FeedService
from src.messaging import MessageRepository, MessagingService
from src.notification import NotificationRepository, NotificationService
from src.post import EventEmitter, MentionParser, PostRepository, PostService
from src.user import FollowRepository, UserService

_bearer = HTTPBearer()


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
    app = FastAPI()

    follow_repo = FollowRepository()
    user_store = UserStore()
    user_service = UserService(follow_repo, known_users=set())
    auth_service = AuthService(user_store)
    post_repo = PostRepository()
    emitter = EventEmitter()
    post_service = PostService(post_repo, emitter, MentionParser({}))
    feed_service = FeedService(FeedCache(), follow_repo, post_repo)
    notif_service = NotificationService(NotificationRepository())
    msg_service = MessagingService(MessageRepository(), user_service._users, emitter)

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

    class PostBody(BaseModel):
        text: str

    @app.post("/posts", status_code=201)
    def create_post(body: PostBody, user_id: str = Depends(current_user)):
        try:
            result = post_service.publish(user_id, body.text)
            feed_service.fan_out(result["post_id"], user_id, time.time())
            if emitter.events:
                notif_service.handle_post_created(emitter.events[-1])
            return result
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    @app.get("/feed")
    def get_feed(user_id: str = Depends(current_user)):
        return {"posts": feed_service.get_feed(user_id)}

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

    @app.get("/notifications")
    def get_notifications(user_id: str = Depends(current_user)):
        return {"notifications": [vars(n) for n in notif_service.get_unread(user_id)]}

    @app.post("/notifications/{notification_id}/read", status_code=204)
    def mark_read(notification_id: str, user_id: str = Depends(current_user)):
        try:
            notif_service.mark_read(notification_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

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

    @app.get("/health")
    def health():
        return {"status": "ok", "postgres": "ok", "redis": "ok"}

    return app
