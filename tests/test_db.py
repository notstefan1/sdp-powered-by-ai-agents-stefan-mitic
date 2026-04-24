"""Tests for INFRA-BE-001.2 - DB migrations create all required tables."""

import importlib
import os
from contextlib import contextmanager

import pytest

import src.db as db_module
from src.db import get_connection, run_migrations

DATABASE_URL = os.environ.get("DATABASE_URL")
skip_no_db = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")


@skip_no_db
def test_infra_be_001_2_s1__all_tables_exist_after_migration():
    # GIVEN - Story: INFRA-BE-001.2, Scenario: S1
    run_migrations()

    # WHEN
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables"
            " WHERE table_schema = 'public'"
        )
        tables = {row[0] for row in cur.fetchall()}

    # THEN
    assert {"users", "follows", "posts", "notifications", "messages"} <= tables


@skip_no_db
def test_infra_be_001_2_s2__migrations_are_idempotent():
    # GIVEN - Story: INFRA-BE-001.2, Scenario: S2
    # WHEN - run twice, should not raise
    run_migrations()
    run_migrations()


def test_get_connection_reads_database_url_from_env_at_call_time(monkeypatch):
    # GIVEN - module imported with one value, env changed before call
    monkeypatch.setenv("DATABASE_URL", "postgresql://old-url")
    captured = {}

    @contextmanager
    def fake_connect(url, **kwargs):
        captured["url"] = url
        yield object()

    importlib.reload(db_module)
    monkeypatch.setenv("DATABASE_URL", "postgresql://new-url")
    monkeypatch.setattr(db_module.psycopg, "connect", fake_connect)

    # WHEN
    with db_module.get_connection():
        pass

    # THEN
    assert captured["url"] == "postgresql://new-url"
