"""Tests for INFRA-BE-001.1 - health endpoint."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api import create_app


def test_infra_be_001_1_s1__all_dependencies_healthy(monkeypatch):
    # GIVEN - Story: INFRA-BE-001.1, Scenario: S1
    # No DATABASE_URL / REDIS_URL set → health reports ok (nothing to probe)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("TESTING", "1")
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
def test_infra_be_001_1_s2__degraded_dependency_reported(monkeypatch):
    # GIVEN - Story: INFRA-BE-001.1, Scenario: S2
    # App starts in in-memory mode; then DATABASE_URL is set to an unreachable
    # host so the health probe fails, simulating a DB going down after startup.
    client = TestClient(create_app())
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://bad:bad@localhost:1/bad",  # pragma: allowlist secret
    )

    # WHEN
    resp = client.get("/health")

    # THEN
    assert resp.status_code == 200
    assert resp.json()["postgres"] == "error"
    assert resp.json()["status"] == "degraded"
