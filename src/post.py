"""Post Service - POST-BE-001.1, POST-BE-001.2"""

import re
import uuid
from dataclasses import dataclass, field


@dataclass
class Post:
    post_id: str
    author_id: str
    text: str
    mentioned_user_ids: list[str] = field(default_factory=list)


class PostRepository:
    def __init__(self):
        self._store: dict[str, Post] = {}

    def save(self, post: Post) -> None:
        self._store[post.post_id] = post

    def get(self, post_id: str) -> Post | None:
        return self._store.get(post_id)


class EventEmitter:
    def __init__(self):
        self.events: list[dict] = []

    def emit(self, event: dict) -> None:
        self.events.append(event)


class MentionParser:
    """POST-BE-001.2 - extract @mentions and resolve to user IDs."""

    def __init__(self, user_lookup: dict[str, str]):
        # user_lookup: {username -> user_id}
        self._lookup = user_lookup

    def parse(self, text: str) -> list[str]:
        usernames = re.findall(r"@(\w+)", text)
        return [self._lookup[u] for u in usernames if u in self._lookup]


class PostService:
    MAX_LENGTH = 280

    def __init__(
        self,
        repo: PostRepository,
        emitter: EventEmitter,
        mention_parser: MentionParser,
    ):
        self._repo = repo
        self._emitter = emitter
        self._mention_parser = mention_parser

    def publish(self, author_id: str, text: str) -> dict:
        """POST-BE-001.1 - publish a post; raises ValueError if invalid."""
        if not author_id:
            raise ValueError("author_id required")
        if len(text) > self.MAX_LENGTH:
            raise ValueError("Post exceeds 280 characters")
        post_id = str(uuid.uuid4())
        mentioned = self._mention_parser.parse(text)
        post = Post(
            post_id=post_id,
            author_id=author_id,
            text=text,
            mentioned_user_ids=mentioned,
        )
        self._repo.save(post)
        self._emitter.emit(
            {
                "post_id": post_id,
                "author_id": author_id,
                "mentioned_user_ids": mentioned,
            }
        )
        return {"post_id": post_id}
