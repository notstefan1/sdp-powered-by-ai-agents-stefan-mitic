"""Messaging Service - MSG-BE-001.1, MSG-BE-001.2"""

import uuid
from dataclasses import dataclass


@dataclass
class Message:
    message_id: str
    sender_id: str
    recipient_id: str
    text: str


class MessageRepository:
    def __init__(self):
        self._store: list[Message] = []

    def save(self, m: Message) -> None:
        self._store.append(m)

    def conversation(self, user_a: str, user_b: str) -> list[Message]:
        return [
            m for m in self._store if {m.sender_id, m.recipient_id} == {user_a, user_b}
        ]


class DbMessageRepository:
    def save(self, m: Message) -> None:
        from src.db import get_connection

        with get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (message_id, sender_id, recipient_id, text)"
                " VALUES (%s, %s, %s, %s)",
                (m.message_id, m.sender_id, m.recipient_id, m.text),
            )
            conn.commit()

    def conversation(self, user_a: str, user_b: str) -> list[Message]:
        from src.db import get_connection

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT message_id, sender_id, recipient_id, text FROM messages"
                " WHERE (sender_id=%s AND recipient_id=%s)"
                " OR (sender_id=%s AND recipient_id=%s)"
                " ORDER BY created_at",
                (user_a, user_b, user_b, user_a),
            )
            return [
                Message(message_id=r[0], sender_id=r[1], recipient_id=r[2], text=r[3])
                for r in cur.fetchall()
            ]


class MessagingService:
    def __init__(self, repo: MessageRepository, known_users: set[str], emitter=None):
        self._repo = repo
        self._users = known_users
        self._emitter = emitter  # optional EventEmitter for async DM notifications

    def send(self, sender_id: str, recipient_id: str, text: str) -> dict:
        """MSG-BE-001.1 - persist DM; raises if recipient unknown."""
        if recipient_id not in self._users:
            raise ValueError("recipient_not_found")
        msg = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            text=text,
        )
        self._repo.save(msg)
        if self._emitter:
            self._emitter.emit(
                {
                    "type": "dm.created",
                    "message_id": msg.message_id,
                    "sender_id": sender_id,
                    "recipient_id": recipient_id,
                }
            )
        return {"message_id": msg.message_id}

    def get_conversation(self, user_id: str, other_id: str) -> list[Message]:
        """MSG-BE-001.2 - return conversation in chronological order."""
        return self._repo.conversation(user_id, other_id)
