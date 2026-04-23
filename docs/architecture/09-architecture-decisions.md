# Chapter 9: Architecture Decisions

## ADR-001: Fan-out on Write for Feed Generation

**Status:** Accepted

**Context:**
Feed reads are the dominant workload. Two strategies exist: fan-out on write (pre-compute each follower's feed at post time) and fan-out on read (compute feed at query time from the social graph).

**Decision:**
Use fan-out on write. Each new post is pushed into every follower's Redis sorted set by the Feed Updater consumer.

**Rationale:**
- Feed reads become a single `ZREVRANGE` + batched `SELECT IN` - predictably fast regardless of follower count.
- For a lightweight network with moderate follower counts, write amplification is acceptable.

**Consequences:**
- Feed reads are O(1) in Redis.
- Write amplification for users with many followers (mitigated by async fan-out).
- Users with very large follower counts (celebrity problem) may need a hybrid strategy in future.

---

## ADR-002: Redis Streams as Event Bus

**Status:** Accepted

**Context:**
Async processing is needed for feed fan-out and notifications. Options: Redis Streams, Kafka, RabbitMQ, or direct async tasks.

**Decision:**
Use Redis Streams with consumer groups.

**Rationale:**
- Redis is already in the stack for feed caching.
- Redis Streams provide at-least-once delivery, consumer groups for load sharing, and a dead-letter pattern - sufficient for this scope without adding a new infrastructure component.

**Consequences:**
- No additional broker to operate.
- Redis becomes a more critical dependency (both cache and bus).
- Migrating to Kafka later is possible by replacing only the `EventEmitter` and consumer bootstrap code.

---

## ADR-003: Single PostgreSQL Instance with Schema-per-Service Boundaries

**Status:** Accepted

**Context:**
True microservice databases (one DB per service) add operational complexity. A single shared DB risks tight coupling.

**Decision:**
Use one PostgreSQL instance but enforce ownership: each service module owns its tables and is the only code that queries them directly.

**Rationale:**
- Keeps deployment simple while preserving logical boundaries.
- The `messages` table is never queried outside the Messaging Service - enforced by code review and module structure, not by network isolation.

**Consequences:**
- Simple deployment and transactions.
- Coupling risk if boundaries are violated - mitigated by module structure and linting rules.
- Can be split into separate databases later by extracting the service module.

---

## ADR-004: Async Services Must Not Block the Post Write Path

**Status:** Accepted

**Context:**
Feed fan-out and notification delivery could be done synchronously in the POST /posts handler, but this would couple post latency to follower count and notification service availability.

**Decision:**
The POST /posts handler returns 201 as soon as the post is persisted and the event is enqueued. Fan-out and notifications are handled by background consumers.

**Rationale:**
- Satisfies NF-02 (notification < 5 s) and NF-03 (system operational if notification service is down) without blocking the user.

**Consequences:**
- Feed and notifications are eventually consistent (acceptable for a social network).
- Requires monitoring of consumer lag to detect delivery delays.
