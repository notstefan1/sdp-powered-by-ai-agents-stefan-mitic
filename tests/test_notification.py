"""Tests for NOTIF-BE-001.1, NOTIF-BE-001.2"""

from src.notification import NotificationRepository, NotificationService


def _service():
    repo = NotificationRepository()
    return NotificationService(repo), repo


def test_notif_be_001_1_s1__notification_row_created_for_each_mentioned_user():
    # GIVEN — Story: NOTIF-BE-001.1, Scenario: S1
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
