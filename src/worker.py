"""Worker process - Redis Streams consumers for feed fan-out and notifications."""

import json
import logging
import os
import time

import redis

from src.db import run_migrations
from src.feed import RedisFeedCache
from src.notification import DbNotificationRepository, NotificationService
from src.user import DbFollowRepository

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

STREAM = "posts:events"
GROUP = "notification-service"
CONSUMER = "worker-1"


def ensure_consumer_groups(r: redis.Redis) -> None:
    for stream in [STREAM]:
        try:
            r.xgroup_create(stream, GROUP, id="0", mkstream=True)
            log.info("Created consumer group %s on %s", GROUP, stream)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise


def process_once(r: redis.Redis) -> int:
    """Read and process one batch of events. Returns number processed."""
    notif_repo = DbNotificationRepository()
    notif_service = NotificationService(notif_repo)
    follow_repo = DbFollowRepository()
    feed_cache = RedisFeedCache(os.environ["REDIS_URL"])

    # reclaim any pending (unacked) entries first
    claimed = r.xautoclaim(STREAM, GROUP, CONSUMER, min_idle_time=60000, start_id="0-0")
    messages = claimed[1] if claimed else []

    # then read new entries
    new = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=10, block=100)
    if new:
        messages = messages + new[0][1]

    processed = 0
    for msg_id, fields in messages:
        try:
            _handle(fields, notif_service, follow_repo, feed_cache)
            r.xack(STREAM, GROUP, msg_id)
            processed += 1
        except Exception:
            log.exception("Failed to process %s", msg_id)

    return processed


def _handle(fields, notif_service, follow_repo, feed_cache) -> None:
    post_id = fields[b"post_id"].decode()
    author_id = fields[b"author_id"].decode()
    mentioned = json.loads(fields.get(b"mentioned_user_ids", b"[]"))
    ts = time.time()

    # fan-out to followers
    for follower_id in follow_repo.followers_of(author_id):
        feed_cache.zadd(follower_id, ts, post_id)

    # notifications for mentions
    notif_service.handle_post_created(
        {
            "post_id": post_id,
            "author_id": author_id,
            "mentioned_user_ids": mentioned,
        }
    )


def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    redis_url = os.environ.get("REDIS_URL")
    if not db_url or not redis_url:
        raise RuntimeError("DATABASE_URL and REDIS_URL must be set")

    run_migrations()
    r = redis.from_url(redis_url)
    ensure_consumer_groups(r)
    log.info("Worker started, consuming %s", STREAM)

    while True:
        try:
            n = process_once(r)
            if n:
                log.info("Processed %d events", n)
        except Exception:
            log.exception("Worker error, retrying in 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()
