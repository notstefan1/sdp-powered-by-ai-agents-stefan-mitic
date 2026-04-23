"""Tests for AUTH-BE-001.1"""

import pytest

from src.auth import AuthService, UserStore


def _service():
    store = UserStore()
    store.create("alice", "secret123")
    return AuthService(store), store


def test_auth_be_001_1_s1__valid_credentials_return_signed_token():
    # GIVEN - Story: AUTH-BE-001.1, Scenario: S1
    service, _ = _service()

    # WHEN
    result = service.login("alice", "secret123")

    # THEN
    assert "token" in result
    assert result["username"] == "alice"
    assert "user_id" in result


def test_auth_be_001_1_s2__invalid_credentials_raise_error():
    # GIVEN - Story: AUTH-BE-001.1, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="invalid_credentials"):
        service.login("alice", "wrongpassword")
