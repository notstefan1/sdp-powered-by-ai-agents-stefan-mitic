"""Tests for FEED-BE-001.1, FEED-BE-001.2"""

from src.feed import FeedCache, FeedService
from src.post import PostRepository
from src.user import FollowRepository


def _setup():
    follow_repo = FollowRepository()
    post_repo = PostRepository()
    cache = FeedCache()
    return follow_repo, post_repo, cache, FeedService(cache, follow_repo, post_repo)


def test_feed_be_001_1_s1__feed_served_from_cache():
    # GIVEN — Story: FEED-BE-001.1, Scenario: S1
    _, _, cache, feed_service = _setup()
    cache.zadd("u-bob", 1000.0, "post-abc")
    cache.zadd("u-bob", 2000.0, "post-xyz")

    # WHEN
    result = feed_service.get_feed("u-bob")

    # THEN
    assert result == ["post-xyz", "post-abc"]
