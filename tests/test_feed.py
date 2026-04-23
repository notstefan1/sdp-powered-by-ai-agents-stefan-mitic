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


def test_feed_be_001_1_s2__feed_served_from_sql_on_cache_miss():
    # GIVEN — Story: FEED-BE-001.1, Scenario: S2
    from src.post import EventEmitter, MentionParser, PostService

    follow_repo, post_repo, cache, feed_service = _setup()
    follow_repo.add("u-bob", "u-alice")
    post_id = PostService(post_repo, EventEmitter(), MentionParser({})).publish(
        "u-alice", "Hello"
    )["post_id"]

    # WHEN
    result = feed_service.get_feed("u-bob")

    # THEN
    assert post_id in result
    assert cache.exists("u-bob")


def test_feed_story_001_s3__empty_feed_for_user_with_no_follows():
    # GIVEN — Story: FEED-STORY-001, Scenario: S3
    _, _, _, feed_service = _setup()

    # WHEN
    result = feed_service.get_feed("u-nobody")

    # THEN
    assert result == []


def test_feed_be_001_2_s1__fan_out_writes_to_all_followers():
    # GIVEN — Story: FEED-BE-001.2, Scenario: S1
    follow_repo, _, cache, feed_service = _setup()
    follow_repo.add("u-1", "u-alice")
    follow_repo.add("u-2", "u-alice")
    follow_repo.add("u-3", "u-alice")

    # WHEN
    feed_service.fan_out("post-abc", "u-alice", 1000.0)

    # THEN
    assert "post-abc" in cache.zrevrange("u-1")
    assert "post-abc" in cache.zrevrange("u-2")
    assert "post-abc" in cache.zrevrange("u-3")
