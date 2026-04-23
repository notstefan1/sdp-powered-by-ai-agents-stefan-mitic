"""User Service - USER-BE-001.1, USER-BE-001.2"""


class FollowRepository:
    def __init__(self):
        self._follows: set[tuple[str, str]] = set()

    def exists(self, follower_id: str, followee_id: str) -> bool:
        return (follower_id, followee_id) in self._follows

    def add(self, follower_id: str, followee_id: str) -> None:
        self._follows.add((follower_id, followee_id))

    def remove(self, follower_id: str, followee_id: str) -> None:
        self._follows.discard((follower_id, followee_id))

    def followers_of(self, followee_id: str) -> list[str]:
        return [f for f, fe in self._follows if fe == followee_id]

    def followees_of(self, follower_id: str) -> list[str]:
        return [fe for f, fe in self._follows if f == follower_id]


class UserService:
    def __init__(self, repo: FollowRepository, known_users: set[str]):
        self._repo = repo
        self._users = known_users

    def follow(self, follower_id: str, followee_id: str) -> None:
        """USER-BE-001.1 - follow a user; raises if duplicate."""
        if self._repo.exists(follower_id, followee_id):
            raise ValueError("already_following")
        self._repo.add(follower_id, followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        """USER-BE-001.2 - unfollow a user; raises if not following."""
        if not self._repo.exists(follower_id, followee_id):
            raise ValueError("not_following")
        self._repo.remove(follower_id, followee_id)
