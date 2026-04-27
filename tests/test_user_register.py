"""Tests for USER-BE-002.1"""

import pytest

from src.exceptions import UsernameTakenError
from src.user import FollowRepository, UserService


def _service():
    return UserService(FollowRepository(), known_users=set())


def test_user_be_002_1_s1__new_user_created_and_returned():
    # GIVEN - Story: USER-BE-002.1, Scenario: S1
    service = _service()

    # WHEN
    result = service.register("alice", "alice@example.com")

    # THEN
    assert "user_id" in result
    assert result["username"] == "alice"


def test_user_be_002_1_s2__duplicate_username_raises_error():
    # GIVEN - Story: USER-BE-002.1, Scenario: S2
    service = _service()
    service.register("alice", "alice@example.com")

    # WHEN / THEN
    with pytest.raises(UsernameTakenError):
        service.register("alice", "other@example.com")
