"""FastAPI application - HTTP layer wiring all services."""

from fastapi import FastAPI
from pydantic import BaseModel

from src.auth import AuthService, UserStore
from src.user import FollowRepository, UserService


def create_app() -> FastAPI:
    app = FastAPI()

    follow_repo = FollowRepository()
    user_store = UserStore()
    user_service = UserService(follow_repo, known_users=set())
    auth_service = AuthService(user_store)

    class RegisterBody(BaseModel):
        username: str
        password: str

    @app.post("/register", status_code=201)
    def register(body: RegisterBody):
        # raises ValueError("username_taken") if duplicate
        result = user_service.register(body.username, "")
        user_store.create(body.username, body.password)
        return result

    class LoginBody(BaseModel):
        username: str
        password: str

    @app.post("/auth/login")
    def login(body: LoginBody):
        return auth_service.login(body.username, body.password)

    return app
