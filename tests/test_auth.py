"""Tests for AUTH-BE-001.1"""

import pytest

from src.auth import AuthService, UserStore


def test_auth_infra_001_2_s1__password_stored_as_bcrypt_not_plaintext():
    # GIVEN - Story: AUTH-INFRA-001.2, Scenario: S1
    # Acceptance: stored value is a bcrypt hash, not plaintext
    store = UserStore()

    # WHEN
    store.create("bob", "hunter2")

    # THEN - bcrypt hashes start with $2b$
    record = store.get("bob")
    assert record["password_hash"].startswith(
        "$2b$"
    ), "password must be stored as bcrypt, not plaintext or sha256"


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


def test_auth_be_001_2_s1__valid_token_decodes_user_id():
    # GIVEN - Story: AUTH-BE-001.2, Scenario: S1
    service, _ = _service()
    result = service.login("alice", "secret123")

    # WHEN
    user_id = service.decode_token(result["token"])

    # THEN
    assert user_id == result["user_id"]


def test_auth_be_001_2_s2__tampered_token_raises_error():
    # GIVEN - Story: AUTH-BE-001.2, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="invalid_token"):
        service.decode_token("not.a.valid.token")
