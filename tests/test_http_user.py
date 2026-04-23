"""Tests for minimal HTTP follow endpoint behavior."""

from src.app import App


def test_follow_endpoint_creates_relationship_for_authenticated_user():
    # GIVEN
    app = App()

    # WHEN
    status_code, body = app.handle_request(
        "POST", "/users/u-alice/follow", auth_user_id="u-bob"
    )

    # THEN
    assert status_code == 201
    assert body == {"status": "ok"}
    assert app.follow_repo.exists("u-bob", "u-alice")
