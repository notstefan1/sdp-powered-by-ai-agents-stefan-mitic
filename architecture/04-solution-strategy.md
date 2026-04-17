# Chapter 4: Solution Strategy

## 4.1 Core Strategies

| Goal          | Strategy                                                                                      |
|---------------|-----------------------------------------------------------------------------------------------|
| Performance   | Materialise feeds in Redis at write time (fan-out on write) so reads are a single cache lookup |
| Reliability   | Async event processing via Redis Streams; core post/read path has no hard dependency on notification or feed services |
| Security      | Direct messages stored in a separate `messages` table, never joined with public post queries  |
| Maintainability | Logical services as Python packages with explicit public APIs; shared DB but separate schemas |

## 4.2 Key Architectural Decisions (summary)

1. **Fan-out on write** for feed generation — acceptable for a lightweight network with moderate follower counts.
2. **Redis Streams** as the event bus — keeps the stack minimal (Redis already present for caching).
3. **Single PostgreSQL instance** with schema-per-service boundaries — avoids distributed transactions while keeping deployment simple.
4. **Notification service is async and optional** — a failure there does not affect posting or feed reads.

## 4.3 Technology Mapping

| Concern              | Technology          |
|----------------------|---------------------|
| API                  | FastAPI (Python)    |
| Social graph + users | PostgreSQL          |
| Posts                | PostgreSQL          |
| Feed materialisation | Redis (sorted set)  |
| Event bus            | Redis Streams       |
| Notifications        | PostgreSQL + async consumer |
| Direct messages      | PostgreSQL          |
