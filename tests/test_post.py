"""Tests for POST-BE-001.1, POST-BE-001.2"""

import pytest

from src.post import EventEmitter, MentionParser, PostRepository, PostService


def test_post_be_001_1_s1__valid_post_persisted_and_event_emitted():
    # GIVEN — Story: POST-BE-001.1, Scenario: S1
    repo = PostRepository()
    emitter = EventEmitter()
    parser = MentionParser({"alice": "u-123"})
    service = PostService(repo, emitter, parser)

    # WHEN
    result = service.publish("u-bob", "Hello @alice")

    # THEN
    assert "post_id" in result
    post = repo.get(result["post_id"])
    assert post.author_id == "u-bob"
    assert post.text == "Hello @alice"
    assert len(emitter.events) == 1
    event = emitter.events[0]
    assert event["post_id"] == result["post_id"]
    assert event["author_id"] == "u-bob"
    assert event["mentioned_user_ids"] == ["u-123"]


def test_post_be_001_1_s2__unauthenticated_request_rejected():
    # GIVEN — Story: POST-BE-001.1, Scenario: S2
    repo = PostRepository()
    emitter = EventEmitter()
    service = PostService(repo, emitter, MentionParser({}))

    # WHEN / THEN
    with pytest.raises(ValueError, match="author_id required"):
        service.publish("", "Hello world")
    assert len(emitter.events) == 0


def test_post_be_001_2_s1__single_mention_resolved():
    # GIVEN — Story: POST-BE-001.2, Scenario: S1
    parser = MentionParser({"alice": "u-123"})

    # WHEN
    mentioned = parser.parse("Hello @alice")

    # THEN
    assert mentioned == ["u-123"]


def test_post_be_001_2_s2__unknown_mention_ignored():
    # GIVEN — Story: POST-BE-001.2, Scenario: S2
    parser = MentionParser({})

    # WHEN
    mentioned = parser.parse("Hello @nobody")

    # THEN
    assert mentioned == []
