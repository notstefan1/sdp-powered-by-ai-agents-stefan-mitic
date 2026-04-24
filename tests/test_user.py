"""Tests for USER-BE-001.1, USER-BE-001.2, USER-BE-003.1, USER-BE-002.2"""

import pytest

from src.user import FollowRepository, UserService


def _service():
    repo = FollowRepository()
    return UserService(repo, {"u-alice", "u-bob"}), repo


def test_user_be_003_1_s1__get_by_username_returns_user():
    # GIVEN - Story: USER-BE-003.1, Scenario: S1
    service, _ = _service()
    service.register("alice", "alice@example.com")

    # WHEN
    result = service.get_by_username("alice")

    # THEN
    assert result["username"] == "alice"
    assert "user_id" in result


def test_user_be_003_1_s2__get_by_username_unknown_raises():
    # GIVEN - Story: USER-BE-003.1, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="user_not_found"):
        service.get_by_username("nobody")


def test_user_be_002_2_s1__update_profile_display_name():
    # GIVEN - Story: USER-BE-002.2, Scenario: S1
    service, _ = _service()
    result = service.register("alice", "alice@example.com")
    uid = result["user_id"]

    # WHEN
    service.update_profile(uid, display_name="Alice Smith")

    # THEN
    user = service.get_by_username("alice")
    assert user["display_name"] == "Alice Smith"


def test_user_be_002_2_s2__update_profile_unknown_user_raises():
    # GIVEN - Story: USER-BE-002.2, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="user_not_found"):
        service.update_profile("u-ghost", display_name="X")


def test_user_be_001_1_s1__follow_relationship_created():
    # GIVEN - Story: USER-BE-001.1, Scenario: S1
    service, repo = _service()

    # WHEN
    service.follow("u-bob", "u-alice")

    # THEN
    assert repo.exists("u-bob", "u-alice")


def test_user_be_001_1_s2__duplicate_follow_returns_conflict():
    # GIVEN - Story: USER-BE-001.1, Scenario: S2
    service, _ = _service()
    service.follow("u-bob", "u-alice")

    # WHEN / THEN
    with pytest.raises(ValueError, match="already_following"):
        service.follow("u-bob", "u-alice")


def test_user_be_001_2_s1__unfollow_removes_relationship():
    # GIVEN - Story: USER-BE-001.2, Scenario: S1
    service, repo = _service()
    service.follow("u-bob", "u-alice")

    # WHEN
    service.unfollow("u-bob", "u-alice")

    # THEN
    assert not repo.exists("u-bob", "u-alice")


def test_user_be_001_2_s2__unfollow_non_followed_user_raises():
    # GIVEN - Story: USER-BE-001.2, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="not_following"):
        service.unfollow("u-bob", "u-alice")
