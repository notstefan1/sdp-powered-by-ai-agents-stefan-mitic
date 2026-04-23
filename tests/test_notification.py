"""Tests for NOTIF-BE-001.1, NOTIF-BE-001.2"""

from src.notification import NotificationRepository, NotificationService


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
