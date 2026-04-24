"""Tests for NOTIF-BE-001.1, NOTIF-BE-001.2"""

import pytest

from src.notification import (
    DbNotificationRepository,
    Notification,
    NotificationRepository,
    NotificationService,
)


def test_notif_infra_002_2_s1__db_repo_reraises_non_unique_errors(monkeypatch):
    # GIVEN - Story: NOTIF-INFRA-002.2 - only UniqueViolation should be swallowed;
    # other DB errors must propagate so the worker does not xack a notification
    # that was never actually saved.
    from unittest.mock import MagicMock, patch

    import psycopg

    repo = DbNotificationRepository()
    n = Notification(
        notification_id="n-1",
        recipient_id="u-alice",
        post_id="post-1",
        author_id="u-bob",
        type="mention",
    )

    # Simulate a non-unique DB error (e.g. disk full / schema mismatch)
    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.side_effect = psycopg.OperationalError("disk full")

    with (
        patch("src.db.get_connection", return_value=mock_conn),
        pytest.raises(psycopg.OperationalError),
    ):
        repo.save(n)


def _service():
    repo = NotificationRepository()
    return NotificationService(repo), repo


def test_notif_be_001_1_s1__notification_row_created_for_each_mentioned_user():
    # GIVEN - Story: NOTIF-BE-001.1, Scenario: S1
    service, repo = _service()
    event = {
        "post_id": "post-1",
        "author_id": "u-bob",
        "mentioned_user_ids": ["u-alice", "u-carol"],
    }

    # WHEN
    service.handle_post_created(event)

    # THEN
    alice_notifs = repo.unread_for("u-alice")
    carol_notifs = repo.unread_for("u-carol")
    assert len(alice_notifs) == 1
    assert alice_notifs[0].type == "mention"
    assert alice_notifs[0].post_id == "post-1"
    assert alice_notifs[0].author_id == "u-bob"
    assert len(carol_notifs) == 1


def test_notif_be_001_1_s2__event_with_no_mentions_is_ignored():
    # GIVEN - Story: NOTIF-BE-001.1, Scenario: S2
    service, repo = _service()
    event = {"post_id": "post-2", "author_id": "u-bob", "mentioned_user_ids": []}

    # WHEN
    service.handle_post_created(event)

    # THEN
    assert repo.unread_for("u-alice") == []


def test_notif_be_001_2_s1__returns_unread_notifications():
    # GIVEN - Story: NOTIF-BE-001.2, Scenario: S1
    service, _ = _service()
    service.handle_post_created(
        {"post_id": "post-1", "author_id": "u-bob", "mentioned_user_ids": ["u-alice"]}
    )
    service.handle_post_created(
        {"post_id": "post-2", "author_id": "u-carol", "mentioned_user_ids": ["u-alice"]}
    )

    # WHEN
    result = service.get_unread("u-alice")

    # THEN
    assert len(result) == 2
    assert all(n.recipient_id == "u-alice" for n in result)
    assert all(not n.read for n in result)


def test_notif_be_003_1_s1__mark_read_sets_read_flag():
    # GIVEN - Story: NOTIF-BE-003.1, Scenario: S1
    service, _ = _service()
    service.handle_post_created(
        {"post_id": "post-1", "author_id": "u-bob", "mentioned_user_ids": ["u-alice"]}
    )
    notif = service.get_unread("u-alice")[0]

    # WHEN
    service.mark_read(notif.notification_id)

    # THEN
    assert service.get_unread("u-alice") == []


def test_notif_be_003_1_s2__cannot_mark_other_users_notification_as_read():
    # GIVEN - notification belongs to alice
    service, _ = _service()
    service.handle_post_created(
        {"post_id": "post-1", "author_id": "u-bob", "mentioned_user_ids": ["u-alice"]}
    )
    notif = service.get_unread("u-alice")[0]

    # WHEN / THEN - bob cannot mark it read
    with pytest.raises(ValueError, match="notification_not_found"):
        service.mark_read_for("u-bob", notif.notification_id)
