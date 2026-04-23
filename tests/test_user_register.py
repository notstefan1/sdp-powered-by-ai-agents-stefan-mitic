"""Tests for USER-BE-002.1"""

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
