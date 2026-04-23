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
