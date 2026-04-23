"""Tests for INFRA-BE-001.1 - health endpoint."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api import create_app


def test_infra_be_001_1_s1__all_dependencies_healthy():
    # GIVEN - Story: INFRA-BE-001.1, Scenario: S1
    client = TestClient(create_app())

    # WHEN
    resp = client.get("/health")

    # THEN
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "postgres": "ok", "redis": "ok"}


@pytest.mark.skipif(
    bool(os.environ.get("DATABASE_URL")),
    reason="Only meaningful without a real DB running",
)
def test_infra_be_001_1_s2__degraded_dependency_reported():
    # GIVEN - Story: INFRA-BE-001.1, Scenario: S2 - Redis unreachable
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
