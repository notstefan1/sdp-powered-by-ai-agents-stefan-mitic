# FEED-STORY-001: Read Aggregated Feed

**Architecture Reference**: Section 5.3 — Feed Service Components; Section 6.2 — Runtime: Read Feed
**Priority**: Core

---

## Original Story

AS A user
I WANT to see an aggregated feed of posts from people I follow
SO THAT I can stay up to date with their activity

### SCENARIO 1: Feed returned from Redis cache

**Scenario ID**: FEED-STORY-001-S1

**GIVEN**
* I am authenticated
* I follow at least one user who has published posts
* My feed is materialised in Redis

**WHEN**
* I request my feed

**THEN**
* Posts are returned in reverse chronological order
* Response time is < 200 ms (p95)

### SCENARIO 2: Feed falls back to SQL on cache miss

**Scenario ID**: FEED-STORY-001-S2

**GIVEN**
* I am authenticated
* My Redis feed key does not exist (cold start or eviction)

**WHEN**
* I request my feed

**THEN**
* Posts are fetched via SQL query
* The Redis cache is backfilled
* Posts are returned in reverse chronological order

### SCENARIO 3: Empty feed for user with no follows

**Scenario ID**: FEED-STORY-001-S3

**GIVEN**
* I am authenticated
* I follow nobody

**WHEN**
* I request my feed

**THEN**
* Response is `200 OK` with an empty list

---

## FEED-FE-001.1: Feed Timeline Component

**Architecture Reference**: Section 5.3 — Feed Reader
**Parent**: FEED-STORY-001

AS A user
I WANT a scrollable timeline of posts
SO THAT I can read my feed

### SCENARIO 1: Posts render in reverse chronological order

**Scenario ID**: FEED-FE-001.1-S1

**GIVEN**
* My feed contains posts

**WHEN**
* I open the home page

**THEN**
* Posts are displayed newest-first
* Each post shows author, text, and timestamp

### SCENARIO 2: Empty state shown when feed is empty

**Scenario ID**: FEED-FE-001.1-S2

**GIVEN**
* My feed is empty

**WHEN**
* I open the home page

**THEN**
* An empty state message is displayed (e.g. "Follow someone to see posts here")

---

## FEED-BE-001.1: Get Feed API Endpoint

**Architecture Reference**: Section 5.3 — Feed Reader; Section 6.2
**Parent**: FEED-STORY-001

AS A developer
I WANT a `GET /feed` endpoint
SO THAT clients can retrieve the authenticated user's feed

### SCENARIO 1: Feed served from Redis

**Scenario ID**: FEED-BE-001.1-S1

**GIVEN**
* Request has a valid JWT
* Redis key `feed:{user_id}` exists with post IDs

**WHEN**
* `GET /feed` is called

**THEN**
* `ZREVRANGE feed:{user_id}` is executed on Redis
* Post details are fetched via batched `SELECT … WHERE post_id IN (…)`
* Response is `200 OK` with ordered post list

### SCENARIO 2: Feed served from SQL on cache miss

**Scenario ID**: FEED-BE-001.1-S2

**GIVEN**
* Redis key `feed:{user_id}` does not exist

**WHEN**
* `GET /feed` is called

**THEN**
* Posts are fetched from PostgreSQL via SQL join on `follows`
* Redis cache is backfilled with `ZADD`
* Response is `200 OK` with ordered post list

---

## FEED-BE-001.2: Feed Fan-out Consumer

**Architecture Reference**: Section 5.3 — Feed Updater; Section 4.2 — Fan-out on write
**Parent**: FEED-STORY-001

AS A developer
I WANT a Redis Streams consumer that fans out `post.created` events
SO THAT each follower's feed cache is updated at write time

### SCENARIO 1: Fan-out writes to all followers' feed keys

**Scenario ID**: FEED-BE-001.2-S1

**GIVEN**
* A `post.created` event arrives with `{ post_id, author_id }`
* `author_id` has 3 followers: `u-1`, `u-2`, `u-3`

**WHEN**
* The Feed Updater processes the event

**THEN**
* `ZADD feed:u-1 <timestamp> <post_id>` is executed
* `ZADD feed:u-2 <timestamp> <post_id>` is executed
* `ZADD feed:u-3 <timestamp> <post_id>` is executed

---

## FEED-INFRA-001.1: Deploy Feed Service

**Architecture Reference**: Section 5.1 — Feed Service container
**Parent**: FEED-STORY-001

AS A developer
I WANT the Feed Service deployed as a runnable unit
SO THAT the feed endpoint and fan-out consumer are operational

### SCENARIO 1: Service starts and health check passes

**Scenario ID**: FEED-INFRA-001.1-S1

**GIVEN**
* The Feed Service container is deployed

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK`

---

## FEED-INFRA-001.2: Provision Redis Sorted Sets for Feed Cache

**Architecture Reference**: Section 4.3 — Feed materialisation → Redis sorted set
**Parent**: FEED-STORY-001

AS A developer
I WANT Redis configured and accessible to the Feed Service
SO THAT feed sorted sets can be read and written

### SCENARIO 1: Feed key is writable and readable

**Scenario ID**: FEED-INFRA-001.2-S1

**GIVEN**
* Redis instance is running and reachable by the Feed Service

**WHEN**
* `ZADD feed:u-1 1000 post-abc` is executed followed by `ZREVRANGE feed:u-1 0 -1`

**THEN**
* `post-abc` is returned

---

## FEED-INFRA-001.3: Register Feed Service Consumer Group on Redis Stream

**Architecture Reference**: Section 4.2 — Redis Streams; Section 5.3 — Feed Updater
**Parent**: FEED-STORY-001

AS A developer
I WANT the `feed-service` consumer group registered on the `posts:events` stream
SO THAT fan-out events are consumed reliably

### SCENARIO 1: Consumer group receives post.created events

**Scenario ID**: FEED-INFRA-001.3-S1

**GIVEN**
* Consumer group `feed-service` is registered on stream `posts:events`

**WHEN**
* A `post.created` event is written to the stream

**THEN**
* The Feed Updater reads it via `XREADGROUP GROUP feed-service`
* The event is acknowledged after successful fan-out

---

## FEED-INFRA-001.4: CloudWatch Monitoring for Feed Service

**Architecture Reference**: Section 8 — Crosscutting Concepts (observability)
**Parent**: FEED-STORY-001

AS A developer
I WANT log groups and alarms for the Feed Service
SO THAT latency regressions and errors are observable

### SCENARIO 1: Latency alarm triggers on p95 > 200 ms

**Scenario ID**: FEED-INFRA-001.4-S1

**GIVEN**
* A CloudWatch alarm is configured on feed endpoint p95 latency > 200 ms

**WHEN**
* p95 latency exceeds 200 ms over a 5-minute window

**THEN**
* The alarm transitions to ALARM state
