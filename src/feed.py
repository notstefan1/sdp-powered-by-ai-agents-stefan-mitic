"""Feed Service - FEED-BE-001.1, FEED-BE-001.2"""

from dataclasses import dataclass, field


@dataclass
class FeedCache:
    """In-memory Redis sorted-set substitute (used in tests)."""

    _data: dict[str, list[tuple[float, str]]] = field(default_factory=dict)

    def zadd(self, user_id: str, score: float, post_id: str) -> None:
        self._data.setdefault(user_id, [])
        self._data[user_id].append((score, post_id))
        self._data[user_id].sort(key=lambda x: x[0], reverse=True)

    def zrevrange(self, user_id: str) -> list[str]:
        return [post_id for _, post_id in self._data.get(user_id, [])]

    def exists(self, user_id: str) -> bool:
        return user_id in self._data


class RedisFeedCache:
    """Redis sorted-set backed feed cache."""

    def __init__(self, redis_url: str):
        import redis

        self._r = redis.from_url(redis_url)

    def _key(self, user_id: str) -> str:
        return f"feed:{user_id}"

    def zadd(self, user_id: str, score: float, post_id: str) -> None:
        self._r.zadd(self._key(user_id), {post_id: score})

    def zrevrange(self, user_id: str) -> list[str]:
        return [v.decode() for v in self._r.zrevrange(self._key(user_id), 0, -1)]

    def exists(self, user_id: str) -> bool:
        return self._r.exists(self._key(user_id)) > 0


class FeedService:
    def __init__(self, cache: FeedCache, follow_repo, post_repo):
        self._cache = cache
        self._follow_repo = follow_repo  # FollowRepository from user.py
        self._post_repo = post_repo  # PostRepository from post.py

    def get_feed(self, user_id: str) -> list[str]:
        """FEED-BE-001.1 - return post IDs from cache; fall back to SQL on miss."""
        if self._cache.exists(user_id):
            return self._cache.zrevrange(user_id)
        # SQL fallback: own posts + followees' posts
        followees = self._follow_repo.followees_of(user_id)
        authors = set(followees) | {user_id}
        posts = [p for p in self._post_repo._store.values() if p.author_id in authors]
        posts.sort(key=lambda p: p.post_id, reverse=True)
        post_ids = [p.post_id for p in posts]
        for i, pid in enumerate(reversed(post_ids)):
            self._cache.zadd(user_id, float(i), pid)
        return post_ids

    def fan_out(self, post_id: str, author_id: str, timestamp: float) -> None:
        """FEED-BE-001.2 - write post into each follower's feed cache."""
        followers = self._follow_repo.followers_of(author_id)
        for follower_id in followers:
            self._cache.zadd(follower_id, timestamp, post_id)
