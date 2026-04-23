"""Tests for MSG-BE-001.1, MSG-BE-001.2, MSG-STORY-001"""

import pytest

from src.messaging import MessageRepository, MessagingService


def _service(emitter=None):
    repo = MessageRepository()
    return MessagingService(repo, {"u-alice", "u-bob"}, emitter), repo


def test_msg_be_001_1_s1__message_persisted_and_id_returned():
    # GIVEN — Story: MSG-BE-001.1, Scenario: S1
    service, repo = _service()

    # WHEN
    result = service.send("u-bob", "u-alice", "Hello")

    # THEN
    assert "message_id" in result
    msgs = repo.conversation("u-bob", "u-alice")
    assert len(msgs) == 1
    assert msgs[0].text == "Hello"
    assert msgs[0].sender_id == "u-bob"
    assert msgs[0].recipient_id == "u-alice"


def test_msg_be_001_1_s2__message_to_unknown_user_rejected():
    # GIVEN — Story: MSG-BE-001.1, Scenario: S2
    service, repo = _service()

    # WHEN / THEN
    with pytest.raises(ValueError, match="recipient_not_found"):
        service.send("u-bob", "u-ghost", "Hello")
    assert repo.conversation("u-bob", "u-ghost") == []


def test_msg_be_001_1_s1__dm_created_event_emitted():
    # GIVEN — Story: MSG-BE-001.1, Scenario: S1 (async notification)
    from src.post import EventEmitter

    emitter = EventEmitter()
    service, _ = _service(emitter)

    # WHEN
    result = service.send("u-bob", "u-alice", "Hello")

    # THEN
    assert len(emitter.events) == 1
    event = emitter.events[0]
    assert event["type"] == "dm.created"
    assert event["message_id"] == result["message_id"]
    assert event["sender_id"] == "u-bob"
    assert event["recipient_id"] == "u-alice"


def test_msg_be_001_2_s1__conversation_returned_in_chronological_order():
    # GIVEN — Story: MSG-BE-001.2, Scenario: S1
    service, _ = _service()
    service.send("u-bob", "u-alice", "First")
    service.send("u-alice", "u-bob", "Second")
    service.send("u-bob", "u-alice", "Third")

    # WHEN
    result = service.get_conversation("u-bob", "u-alice")

    # THEN
    assert [m.text for m in result] == ["First", "Second", "Third"]
