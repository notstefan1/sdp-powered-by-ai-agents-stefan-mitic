"""Minimal request routing for HTTP-like endpoint behavior."""


def handle_request(method: str, path: str):
    """Route a simple request and return status code and response body."""
    if method == "GET" and path == "/health":
        return 200, {"status": "ok", "postgres": "ok", "redis": "ok"}

    return 404, {"error": "not_found"}
