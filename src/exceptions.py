"""Domain exceptions - replaces stringly-typed ValueError raises."""


class UsernameTakenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class AlreadyFollowingError(Exception):
    pass


class NotFollowingError(Exception):
    pass


class RecipientNotFoundError(Exception):
    pass


class PostTooLongError(Exception):
    pass


class AuthorRequiredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class NotificationNotFoundError(Exception):
    pass
