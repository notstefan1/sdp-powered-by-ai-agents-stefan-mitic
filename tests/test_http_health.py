"""Tests for minimal HTTP health endpoint behavior."""

from src.app import handle_request


def test_health_endpoint_returns_200_with_dependency_statuses():
    # GIVEN
    method = "GET"
    path = "/health"

    # WHEN
    status_code, body = handle_request(method, path)

    # THEN
    assert status_code == 200
    assert body == {"status": "ok", "postgres": "ok", "redis": "ok"}
