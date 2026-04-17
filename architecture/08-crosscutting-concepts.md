# Chapter 8: Cross-cutting Concepts

## 8.1 Authentication & Authorisation

- All API endpoints require a JWT Bearer token validated by the API Gateway middleware.
- The token is issued by an external Auth Provider (e.g. Auth0) and carries `sub` (user ID) and `scope` claims.
- The `user_id` extracted from the token is passed as a typed parameter to every service call — services never trust a user-supplied ID in the request body.
- DM endpoints additionally verify that the requesting user is a participant in the conversation.

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
- Notification payloads contain only IDs — the client fetches full content separately.
