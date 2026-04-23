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

    def get_by_id(self, notification_id: str) -> Notification | None:
        return next(
            (n for n in self._store if n.notification_id == notification_id), None
        )


class DbNotificationRepository:
    def save(self, n: Notification) -> None:
        from src.db import get_connection

        with get_connection() as conn:
            try:
                conn.execute(
                    "INSERT INTO notifications"
                    " (notification_id, recipient_id, post_id, author_id,"
                    " type, entity_type, entity_id)"
                    " VALUES (%s,%s,%s,%s,%s,'post',%s)",
                    (
                        n.notification_id,
                        n.recipient_id,
                        n.post_id,
                        n.author_id,
                        n.type,
                        n.post_id,
                    ),
                )
                conn.commit()
            except Exception:
                conn.rollback()

    def unread_for(self, recipient_id: str) -> list[Notification]:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT notification_id, recipient_id, post_id, author_id, type"
                " FROM notifications WHERE recipient_id=%s AND read=false",
                (recipient_id,),
            )
            return [
                Notification(
                    notification_id=r[0],
                    recipient_id=r[1],
                    post_id=r[2],
                    author_id=r[3],
                    type=r[4],
                )
                for r in cur.fetchall()
            ]

    def get_by_id(self, notification_id: str) -> Notification | None:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT notification_id, recipient_id, post_id, author_id, type, read"
                " FROM notifications WHERE notification_id=%s",
                (notification_id,),
            )
            row = cur.fetchone()
        if not row:
            return None
        n = Notification(
            notification_id=row[0],
            recipient_id=row[1],
            post_id=row[2],
            author_id=row[3],
            type=row[4],
        )
        n.read = row[5]
        return n

    def mark_read_in_db(self, notification_id: str) -> None:
        from src.db import get_connection

        with get_connection() as conn:
            conn.execute(
                "UPDATE notifications SET read=true WHERE notification_id=%s",
                (notification_id,),
            )
            conn.commit()


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

    def mark_read(self, notification_id: str) -> None:
        """NOTIF-BE-003.1 - mark a notification as read."""
        n = self._repo.get_by_id(notification_id)
        if not n:
            raise ValueError("notification_not_found")
        n.read = True
        if hasattr(self._repo, "mark_read_in_db"):
            self._repo.mark_read_in_db(notification_id)
