# FEED-STORY-001: Read Aggregated Feed

**Architecture Reference**: Section 5.3 - Feed Service Components; Section 6.2 - Runtime: Read Feed
**Priority**: Core

---

## Original Story


> AS A user
> I WANT to see an aggregated feed of posts from people I follow
> SO THAT I can stay up to date with their activity

### SCENARIO 1: Feed returned from Redis cache

**Scenario ID**: FEED-STORY-001-S1

:::{admonition} GIVEN
:class: note
* I am authenticated
* I follow at least one user who has published posts
* My feed is materialised in Redis
:::

:::{admonition} WHEN
:class: tip
* I request my feed
:::

:::{admonition} THEN
:class: important
* Posts are returned in reverse chronological order
* Response time is < 200 ms (p95)
:::

### SCENARIO 2: Feed falls back to SQL on cache miss

**Scenario ID**: FEED-STORY-001-S2

:::{admonition} GIVEN
:class: note
* I am authenticated
* My Redis feed key does not exist (cold start or eviction)
:::

:::{admonition} WHEN
:class: tip
* I request my feed
:::

:::{admonition} THEN
:class: important
* Posts are fetched via SQL query
* The Redis cache is backfilled
* Posts are returned in reverse chronological order
:::

### SCENARIO 3: Empty feed for user with no follows

**Scenario ID**: FEED-STORY-001-S3

:::{admonition} GIVEN
:class: note
* I am authenticated
* I follow nobody
:::

:::{admonition} WHEN
:class: tip
* I request my feed
:::

:::{admonition} THEN
:class: important
* Response is `200 OK` with an empty list
:::

---

## FEED-FE-001.1: Feed Timeline Component

**Architecture Reference**: Section 5.3 - Feed Reader
**Parent**: FEED-STORY-001


> AS A user
> I WANT a scrollable timeline of posts
> SO THAT I can read my feed

### SCENARIO 1: Posts render in reverse chronological order

**Scenario ID**: FEED-FE-001.1-S1

:::{admonition} GIVEN
:class: note
* My feed contains posts
:::

:::{admonition} WHEN
:class: tip
* I open the home page
:::

:::{admonition} THEN
:class: important
* Posts are displayed newest-first
* Each post shows author, text, and timestamp
:::

### SCENARIO 2: Empty state shown when feed is empty

**Scenario ID**: FEED-FE-001.1-S2

:::{admonition} GIVEN
:class: note
* My feed is empty
:::

:::{admonition} WHEN
:class: tip
* I open the home page
:::

:::{admonition} THEN
:class: important
* An empty state message is displayed (e.g. "Follow someone to see posts here")
:::

---

## FEED-BE-001.1: Get Feed API Endpoint

**Architecture Reference**: Section 5.3 - Feed Reader; Section 6.2
**Parent**: FEED-STORY-001


> AS A developer
> I WANT a `GET /feed` endpoint
> SO THAT clients can retrieve the authenticated user's feed

### SCENARIO 1: Feed served from Redis

**Scenario ID**: FEED-BE-001.1-S1

:::{admonition} GIVEN
:class: note
* Request has a valid JWT
* Redis key `feed:{user_id}` exists with post IDs
:::

:::{admonition} WHEN
:class: tip
* `GET /feed` is called
:::

:::{admonition} THEN
:class: important
* `ZREVRANGE feed:{user_id}` is executed on Redis
* Post details are fetched via batched `SELECT … WHERE post_id IN (…)`
* Response is `200 OK` with ordered post list
:::

### SCENARIO 2: Feed served from SQL on cache miss

**Scenario ID**: FEED-BE-001.1-S2

:::{admonition} GIVEN
:class: note
* Redis key `feed:{user_id}` does not exist
:::

:::{admonition} WHEN
:class: tip
* `GET /feed` is called
:::

:::{admonition} THEN
:class: important
* Posts are fetched from PostgreSQL via SQL join on `follows`
* Redis cache is backfilled with `ZADD`
* Response is `200 OK` with ordered post list
:::

---

## FEED-BE-001.2: Feed Fan-out Consumer

**Architecture Reference**: Section 5.3 - Feed Updater; Section 4.2 - Fan-out on write
**Parent**: FEED-STORY-001


> AS A developer
> I WANT a Redis Streams consumer that fans out `post.created` events
> SO THAT each follower's feed cache is updated at write time

### SCENARIO 1: Fan-out writes to all followers' feed keys

**Scenario ID**: FEED-BE-001.2-S1

:::{admonition} GIVEN
:class: note
* A `post.created` event arrives with `{ post_id, author_id }`
* `author_id` has 3 followers: `u-1`, `u-2`, `u-3`
:::

:::{admonition} WHEN
:class: tip
* The Feed Updater processes the event
:::

:::{admonition} THEN
:class: important
* `ZADD feed:u-1 <timestamp> <post_id>` is executed
* `ZADD feed:u-2 <timestamp> <post_id>` is executed
* `ZADD feed:u-3 <timestamp> <post_id>` is executed
:::

---

## FEED-INFRA-001.1: Docker Image Builds and Feed Service Container Starts

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping (`api`, `worker`)
**Parent**: FEED-STORY-001


> AS A developer
> I WANT the Docker image to build and both `api` and `worker` containers to start
> SO THAT the feed endpoint and fan-out consumer are operational locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: FEED-INFRA-001.1-S1

:::{admonition} GIVEN
:class: note
* A `Dockerfile` exists at the project root
:::

:::{admonition} WHEN
:class: tip
* `docker build -t kata-tests .` is executed
:::

:::{admonition} THEN
:class: important
* The build exits with code 0
:::

### SCENARIO 2: api container health check passes

**Scenario ID**: FEED-INFRA-001.1-S2

:::{admonition} GIVEN
:class: note
* `docker compose up api` is running
:::

:::{admonition} WHEN
:class: tip
* `GET /health` is called
:::

:::{admonition} THEN
:class: important
* Response is `200 OK`
:::

---

## FEED-INFRA-001.2: Provision Redis Sorted Sets for Feed Cache

**Architecture Reference**: Section 4.3 - Feed materialisation → Redis sorted set
**Parent**: FEED-STORY-001


> AS A developer
> I WANT Redis running and accessible to the Feed Service
> SO THAT feed sorted sets can be read and written

### SCENARIO 1: Feed key is writable and readable

**Scenario ID**: FEED-INFRA-001.2-S1

:::{admonition} GIVEN
:class: note
* The `redis` container is running and reachable by the `api` container
:::

:::{admonition} WHEN
:class: tip
* `ZADD feed:u-1 1000 post-abc` is executed followed by `ZREVRANGE feed:u-1 0 -1`
:::

:::{admonition} THEN
:class: important
* `post-abc` is returned
:::

---

## FEED-INFRA-001.3: Register Feed Service Consumer Group on Redis Stream

**Architecture Reference**: Section 4.2 - Redis Streams; Section 5.3 - Feed Updater
**Parent**: FEED-STORY-001


> AS A developer
> I WANT the `feed-service` consumer group registered on the `posts:events` stream at startup
> SO THAT fan-out events are consumed reliably

### SCENARIO 1: Consumer group receives post.created events

**Scenario ID**: FEED-INFRA-001.3-S1

:::{admonition} GIVEN
:class: note
* Consumer group `feed-service` is registered on stream `posts:events`
:::

:::{admonition} WHEN
:class: tip
* A `post.created` event is written to the stream
:::

:::{admonition} THEN
:class: important
* The Feed Updater reads it via `XREADGROUP GROUP feed-service`
* The event is acknowledged after successful fan-out
:::

---

## FEED-INFRA-001.4: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: FEED-STORY-001


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT feed behaviour is verified in the same environment as CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: FEED-INFRA-001.4-S1

:::{admonition} GIVEN
:class: note
* The Docker image has been built
:::

:::{admonition} WHEN
:class: tip
* `docker run --rm kata-tests` is executed
:::

:::{admonition} THEN
:class: important
* pytest discovers tests under `tests/`
* All feed tests pass
* Exit code is 0
:::
