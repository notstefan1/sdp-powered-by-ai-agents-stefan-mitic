# FEED-STORY-002: Feed Cache Miss / SQL Fallback

**Architecture Reference**: Section 5.3 - Feed Service Components; Section 6.2 - Runtime: Read Feed; Section 4.1 - Reliability strategy
**Priority**: Supporting


> AS A user
> I WANT my feed to load correctly even when the Redis cache is cold or evicted
> SO THAT I always see up-to-date posts regardless of cache state

### SCENARIO 1: Feed is rebuilt from SQL on cache miss and cache is backfilled

**Scenario ID**: FEED-STORY-002-S1

:::{admonition} GIVEN
:class: note
* My Redis feed key does not exist (cold start or eviction)
* I follow `@alice` who has published 3 posts
:::

:::{admonition} WHEN
:class: tip
* I request my feed
:::

:::{admonition} THEN
:class: important
* Posts are fetched from PostgreSQL via a SQL join on `follows`
* The Redis cache is backfilled with `ZADD`
* Posts are returned in reverse chronological order
:::

### SCENARIO 2: Subsequent request is served from the backfilled cache

**Scenario ID**: FEED-STORY-002-S2

:::{admonition} GIVEN
:class: note
* A cache miss triggered a SQL fallback and backfilled the cache
:::

:::{admonition} WHEN
:class: tip
* I request my feed a second time
:::

:::{admonition} THEN
:class: important
* The feed is served from Redis (no SQL query)
* The result is identical to the first response
:::

### SCENARIO 3: Cache miss with no followees returns empty feed

**Scenario ID**: FEED-STORY-002-S3

:::{admonition} GIVEN
:class: note
* My Redis feed key does not exist
* I follow nobody
:::

:::{admonition} WHEN
:class: tip
* I request my feed
:::

:::{admonition} THEN
:class: important
* An empty list is returned
* No error is raised
:::

---

## FEED-FE-002.1: Feed Loading State

**Architecture Reference**: Section 5.3 - Feed Reader
**Parent**: FEED-STORY-002


> AS A user
> I WANT a loading indicator while my feed is being fetched
> SO THAT I know the app is working during a cache-miss rebuild

### SCENARIO 1: Loading spinner shown during fetch

**Scenario ID**: FEED-FE-002.1-S1

:::{admonition} GIVEN
:class: note
* The feed request is in-flight
:::

:::{admonition} WHEN
:class: tip
* The home page renders
:::

:::{admonition} THEN
:class: important
* A loading spinner is displayed until the response arrives
:::

### SCENARIO 2: Feed renders after load completes

**Scenario ID**: FEED-FE-002.1-S2

:::{admonition} GIVEN
:class: note
* The feed response has arrived
:::

:::{admonition} WHEN
:class: tip
* The component updates
:::

:::{admonition} THEN
:class: important
* The spinner is replaced by the post list
:::

---

## FEED-BE-002.1: SQL Fallback with Cache Backfill

**Architecture Reference**: Section 5.3 - Feed Reader; Section 6.2 - SQL fallback path
**Parent**: FEED-STORY-002


> AS A developer
> I WANT `FeedService.get_feed` to fall back to SQL and backfill Redis when the cache key is absent
> SO THAT feed reads are resilient to cache eviction

### SCENARIO 1: SQL fallback returns posts and backfills cache

**Scenario ID**: FEED-BE-002.1-S1

:::{admonition} GIVEN
:class: note
* `FeedCache` has no key for `user_id`
* The follow repository has followees for `user_id`
* The post repository has posts from those followees
:::

:::{admonition} WHEN
:class: tip
* `get_feed(user_id)` is called
:::

:::{admonition} THEN
:class: important
* Posts are collected from the post repository filtered by followee IDs
* Each post is written into the cache via `zadd`
* The post IDs are returned in reverse chronological order
:::

### SCENARIO 2: Second call hits cache, not SQL

**Scenario ID**: FEED-BE-002.1-S2

:::{admonition} GIVEN
:class: note
* A previous cache-miss call has backfilled the cache
:::

:::{admonition} WHEN
:class: tip
* `get_feed(user_id)` is called again
:::

:::{admonition} THEN
:class: important
* `cache.exists(user_id)` returns `True`
* The result is served from `cache.zrevrange` without touching the post repository
:::

---

## FEED-INFRA-002.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping (`api`, `worker`)
**Parent**: FEED-STORY-002


> AS A developer
> I WANT the Docker image to build and both `api` and `worker` containers to start
> SO THAT the fallback path is exercisable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: FEED-INFRA-002.1-S1

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

---

## FEED-INFRA-002.2: Redis Sorted Set Survives Container Restart

**Architecture Reference**: Section 4.3 - Feed materialisation → Redis sorted set
**Parent**: FEED-STORY-002


> AS A developer
> I WANT to understand that Redis data is ephemeral by default
> SO THAT the SQL fallback is the correct recovery path after a Redis restart

### SCENARIO 1: Cache miss after Redis restart triggers SQL fallback

**Scenario ID**: FEED-INFRA-002.2-S1

:::{admonition} GIVEN
:class: note
* The `redis` container has been restarted (data lost)
* Posts exist in PostgreSQL
:::

:::{admonition} WHEN
:class: tip
* `GET /feed` is called
:::

:::{admonition} THEN
:class: important
* The feed is rebuilt from SQL
* The Redis key is backfilled
* Posts are returned correctly
:::

---

## FEED-INFRA-002.3: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: FEED-STORY-002


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT the fallback path is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: FEED-INFRA-002.3-S1

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
* All feed fallback tests pass
* Exit code is 0
:::
