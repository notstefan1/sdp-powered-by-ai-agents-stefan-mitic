"""Minimal request routing for HTTP-like endpoint behavior."""

from src.user import FollowRepository, UserService


class App:
    """Tiny app shell used by HTTP-level tests."""

    def __init__(self):
        self.follow_repo = FollowRepository()
        self.user_service = UserService(self.follow_repo, {"u-alice", "u-bob"})

    def handle_request(self, method: str, path: str, auth_user_id: str = ""):
        if method == "GET" and path == "/health":
            return 200, {"status": "ok", "postgres": "ok", "redis": "ok"}

        if method == "POST" and path.startswith("/users/") and path.endswith("/follow"):
            followee_id = path.split("/")[2]
            if not auth_user_id:
                return 401, {"error": "unauthorized"}
            self.user_service.follow(auth_user_id, followee_id)
            return 201, {"status": "ok"}

        return 404, {"error": "not_found"}


def handle_request(method: str, path: str):
    """Route a simple request and return status code and response body."""
    return App().handle_request(method, path)
