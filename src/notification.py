"""Notification Service - NOTIF-BE-001.1, NOTIF-BE-001.2"""

import uuid
from dataclasses import dataclass


@dataclass
class Notification:
    notification_id: str
    recipient_id: str
    post_id: str
    author_id: str
    type: str
    read: bool = False


class NotificationRepository:
    def __init__(self):
        self._store: list[Notification] = []

    def save(self, n: Notification) -> None:
        self._store.append(n)

    def unread_for(self, recipient_id: str) -> list[Notification]:
        return [n for n in self._store if n.recipient_id == recipient_id and not n.read]


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self._repo = repo

    def handle_post_created(self, event: dict) -> None:
        """NOTIF-BE-001.1 - create a notification for each mentioned user."""
        for uid in event.get("mentioned_user_ids", []):
            self._repo.save(
                Notification(
                    notification_id=str(uuid.uuid4()),
                    recipient_id=uid,
                    post_id=event["post_id"],
                    author_id=event["author_id"],
                    type="mention",
                )
            )

    def get_unread(self, recipient_id: str) -> list[Notification]:
        """NOTIF-BE-001.2 - return unread notifications for a user."""
        return self._repo.unread_for(recipient_id)
