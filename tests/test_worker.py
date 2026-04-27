"""Tests for worker consumer group setup - POST-INFRA-001.3, FEED-INFRA-001.3"""

from unittest.mock import MagicMock

from src.worker import ensure_consumer_groups


def test_post_infra_001_3_s1__both_consumer_groups_registered_on_posts_events():
    # GIVEN - Story: POST-INFRA-001.3, Scenario: S1
    # Both feed-service and notification-service groups must be registered
    # so each can independently read post.created events via XREADGROUP.
    r = MagicMock()
    r.xgroup_create.return_value = True

    # WHEN
    ensure_consumer_groups(r)

    # THEN - both groups created on posts:events
    streams_and_groups = [
        (c.args[0], c.args[1]) for c in r.xgroup_create.call_args_list
    ]
    assert ("posts:events", "feed-service") in streams_and_groups
    assert ("posts:events", "notification-service") in streams_and_groups
