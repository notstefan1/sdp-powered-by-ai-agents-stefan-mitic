"""Tests for USER-BE-001.1, USER-BE-001.2"""

import pytest

from src.user import FollowRepository, UserService


def _service():
    repo = FollowRepository()
    return UserService(repo, {"u-alice", "u-bob"}), repo


def test_user_be_001_1_s1__follow_relationship_created():
    # GIVEN — Story: USER-BE-001.1, Scenario: S1
    service, repo = _service()

    # WHEN
    service.follow("u-bob", "u-alice")

    # THEN
    assert repo.exists("u-bob", "u-alice")


def test_user_be_001_1_s2__duplicate_follow_returns_conflict():
    # GIVEN — Story: USER-BE-001.1, Scenario: S2
    service, _ = _service()
    service.follow("u-bob", "u-alice")

    # WHEN / THEN
    with pytest.raises(ValueError, match="already_following"):
        service.follow("u-bob", "u-alice")


def test_user_be_001_2_s1__unfollow_removes_relationship():
    # GIVEN — Story: USER-BE-001.2, Scenario: S1
    service, repo = _service()
    service.follow("u-bob", "u-alice")

    # WHEN
    service.unfollow("u-bob", "u-alice")

    # THEN
    assert not repo.exists("u-bob", "u-alice")


def test_user_be_001_2_s2__unfollow_non_followed_user_raises():
    # GIVEN — Story: USER-BE-001.2, Scenario: S2
    service, _ = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="not_following"):
        service.unfollow("u-bob", "u-alice")
