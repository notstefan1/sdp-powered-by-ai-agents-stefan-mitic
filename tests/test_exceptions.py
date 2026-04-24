"""Tests that domain exception classes exist and are importable."""

from src.exceptions import (
    AlreadyFollowingError,
    InvalidCredentialsError,
    InvalidTokenError,
    NotFollowingError,
    NotificationNotFoundError,
    PostTooLongError,
    RecipientNotFoundError,
    UsernameTakenError,
    UserNotFoundError,
)


def test_domain_exceptions_are_subclasses_of_exception():
    for cls in [
        UsernameTakenError,
        UserNotFoundError,
        AlreadyFollowingError,
        NotFollowingError,
        RecipientNotFoundError,
        PostTooLongError,
        InvalidCredentialsError,
        InvalidTokenError,
        NotificationNotFoundError,
    ]:
        assert issubclass(cls, Exception)
        assert not issubclass(
            cls, ValueError
        ), f"{cls.__name__} must not be a ValueError subclass"
