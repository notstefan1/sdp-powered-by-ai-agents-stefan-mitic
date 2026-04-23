"""Tests for USER-BE-001.1, USER-BE-001.2"""

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
