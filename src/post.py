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

    def get_by_author(self, author_id: str) -> list[Post]:
        return sorted(
            [p for p in self._store.values() if p.author_id == author_id],
            key=lambda p: p.post_id,
            reverse=True,
        )


class DbPostRepository:
    def save(self, post: Post) -> None:
        from src.db import get_connection

        with get_connection() as conn:
            conn.execute(
                "INSERT INTO posts (post_id, author_id, text) VALUES (%s, %s, %s)",
                (post.post_id, post.author_id, post.text),
            )
            conn.commit()

    def get(self, post_id: str) -> Post | None:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT post_id, author_id, text FROM posts WHERE post_id = %s",
                (post_id,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return Post(post_id=row[0], author_id=row[1], text=row[2])

    def get_by_author(self, author_id: str) -> list[Post]:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT post_id, author_id, text FROM posts"
                " WHERE author_id = %s ORDER BY created_at DESC",
                (author_id,),
            )
            return [
                Post(post_id=r[0], author_id=r[1], text=r[2]) for r in cur.fetchall()
            ]

    @property
    def _store(self):
        """Compatibility shim for FeedService SQL fallback."""
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT post_id, author_id, text FROM posts")
            return {
                r[0]: Post(post_id=r[0], author_id=r[1], text=r[2])
                for r in cur.fetchall()
            }


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


class DbMentionParser:
    """Resolves @mentions via live DB lookup."""

    def parse(self, text: str) -> list[str]:
        from src.db import get_connection

        usernames = re.findall(r"@(\w+)", text)
        if not usernames:
            return []
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM users WHERE username = ANY(%s)", (usernames,)
            )
            return [r[0] for r in cur.fetchall()]


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
        event = {
            "post_id": post_id,
            "author_id": author_id,
            "mentioned_user_ids": mentioned,
        }
        self._emitter.emit(event)
        return event
