"""Tests for minimal HTTP health endpoint behavior."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
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


@pytest.mark.skipif(
    bool(os.environ.get("DATABASE_URL")),
    reason="Only meaningful without a real DB running",
)
def test_health_reports_degraded_when_db_unreachable():
    # GIVEN - Story: INFRA-BE-001.1, Scenario: S2
    original = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = (
        "postgresql://bad:bad@localhost:1/bad"  # pragma: allowlist secret
    )
    try:
        client = TestClient(create_app())
        resp = client.get("/health")
    finally:
        if original is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original

    assert resp.status_code == 200
    assert resp.json()["postgres"] == "error"
    assert resp.json()["status"] == "degraded"
