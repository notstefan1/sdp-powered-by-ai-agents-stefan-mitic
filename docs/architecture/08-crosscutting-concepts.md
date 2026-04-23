# Chapter 8: Cross-cutting Concepts

## 8.1 Authentication & Authorisation

- `POST /auth/login` accepts `{ username, password }` and returns a signed JWT.
- Passwords are stored as bcrypt hashes in the `users.password_hash` column - never plaintext.
- The JWT payload carries `{ "sub": user_id, "username": username }` and is signed with a server secret (`AUTH_SECRET` env var).
- All API endpoints except `POST /auth/login` and `POST /users` (register) require a `Authorization: Bearer <token>` header.
- The token is validated by a FastAPI dependency (`get_current_user`) that extracts `user_id` and injects it into every service call - services never trust a user-supplied ID in the request body.
- DM endpoints additionally verify that the requesting user is a participant in the conversation.

## 8.1.1 Auth Request Flow

```
POST /auth/login  →  AuthService.login(username, password)
                  →  verify bcrypt hash
                  →  sign JWT (HS256, 24h expiry)
                  →  return { token, user_id, username }
```

All other endpoints:
```
Request  →  get_current_user dependency  →  decode JWT  →  inject user_id
```

## 8.2 Error Handling

| Layer            | Strategy                                                                 |
|------------------|--------------------------------------------------------------------------|
| HTTP             | FastAPI exception handlers return RFC 7807 Problem JSON                  |
| Service          | Raise typed domain exceptions (e.g. `UserNotFound`, `PostNotFound`)      |
| Async consumers  | On processing failure: log error, XACK to avoid reprocessing poison messages after N retries; dead-letter to a `*.dlq` stream |
| Database         | Use transactions for multi-table writes (e.g. post + event in same tx)   |

## 8.3 Logging & Observability

- Structured JSON logs (via `structlog`) on every request and every event consumed.
- Each request carries a `correlation_id` (UUID) set at the gateway and propagated to all service calls and log entries.
- Key metrics to instrument: feed read latency, fan-out duration, notification delivery lag, DLQ depth.

## 8.4 Data Privacy

- Direct messages are never included in any public API response.
- Post permalinks are public by design; no access control on public posts.
- Notification payloads contain only IDs (`recipient_id`, `actor_id`, `entity_type`, `entity_id`) - the client fetches full content separately.

## 8.5 Database Migrations

- All tables are created automatically when the `api` container starts via a migration script (`scripts/migrate.py` or inline in `main.py`).
- Migrations are idempotent: running them multiple times does not fail or corrupt data.
- Tables created:
  - `users (user_id, username, email, password_hash, display_name, created_at)` - unique on `username`
  - `follows (follower_id, followee_id, created_at)` - unique on `(follower_id, followee_id)`
  - `posts (post_id, author_id, text, created_at)` - primary key on `post_id`
  - `notifications (notification_id, recipient_id, actor_id, entity_type, entity_id, type, read, created_at)` - unique on `(recipient_id, type, entity_type, entity_id)`
  - `messages (message_id, sender_id, recipient_id, text, created_at)` - primary key on `message_id`

## 8.6 Health Checks

- `GET /health` returns `{ "status": "ok", "postgres": "ok", "redis": "ok" }` when all dependencies are reachable.
- If Redis is down, the response is `{ "status": "degraded", "postgres": "ok", "redis": "error" }` - the API does not crash.
- Docker Compose uses this endpoint for container health checks.
