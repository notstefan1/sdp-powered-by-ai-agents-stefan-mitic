# POST-STORY-001: Publish a Post

**Architecture Reference**: Section 5.2 — Post Service Components; Section 6.1 — Runtime: Publish a Post
**Priority**: Core

---

## Original Story

AS A user
I WANT to publish a short public message
SO THAT my followers can see it in their feed and mentioned users are notified

### SCENARIO 1: Successful post publish

**Scenario ID**: POST-STORY-001-S1

**GIVEN**
* I am authenticated
* My post text is ≤ 280 characters

**WHEN**
* I submit the post

**THEN**
* The post is persisted in the database
* A `post.created` event is emitted to Redis Streams
* I receive a 201 response with the post ID
* The HTTP response returns before feed fan-out or notification completes

### SCENARIO 2: Post with @mention

**Scenario ID**: POST-STORY-001-S2

**GIVEN**
* My post text contains `@username`
* `@username` is a registered user

**WHEN**
* I submit the post

**THEN**
* The post is persisted
* The `post.created` event includes `mentioned_user_ids: [@username's ID]`

### SCENARIO 3: Post exceeds character limit

**Scenario ID**: POST-STORY-001-S3

**GIVEN**
* My post text is > 280 characters

**WHEN**
* I submit the post

**THEN**
* The post is rejected with HTTP 422
* No event is emitted

---

## POST-FE-001.1: Post Compose Component

**Architecture Reference**: Section 5.2 — Post Router
**Parent**: POST-STORY-001

AS A user
I WANT a text input with a submit button
SO THAT I can write and publish a post

### SCENARIO 1: Submit valid post

**Scenario ID**: POST-FE-001.1-S1

**GIVEN**
* I am on the home page
* The compose box is empty

**WHEN**
* I type a message and click "Post"

**THEN**
* The post appears in my timeline immediately (optimistic update)
* The compose box clears

### SCENARIO 2: Character limit feedback

**Scenario ID**: POST-FE-001.1-S2

**GIVEN**
* I am typing in the compose box

**WHEN**
* My text exceeds 280 characters

**THEN**
* A character counter turns red
* The submit button is disabled

---

## POST-BE-001.1: Publish Post API Endpoint

**Architecture Reference**: Section 5.2 — Post Router → Post Publisher
**Parent**: POST-STORY-001

AS A developer
I WANT a `POST /posts` endpoint
SO THAT clients can publish posts

### SCENARIO 1: Valid post is persisted and event emitted

**Scenario ID**: POST-BE-001.1-S1

**GIVEN**
* Request has a valid JWT
* Body `{ "text": "Hello @alice" }` is ≤ 280 chars

**WHEN**
* `POST /posts` is called

**THEN**
* Post row is inserted into `posts` table with `author_id` from JWT
* `post.created` event `{ post_id, author_id, mentioned_user_ids }` is written to Redis Stream
* Response is `201 { "post_id": "<uuid>" }`

### SCENARIO 2: Unauthenticated request is rejected

**Scenario ID**: POST-BE-001.1-S2

**GIVEN**
* Request has no JWT or an invalid JWT

**WHEN**
* `POST /posts` is called

**THEN**
* Response is `401 Unauthorized`
* No database write occurs

---

## POST-BE-001.2: Mention Parser

**Architecture Reference**: Section 5.2 — Mention Parser
**Parent**: POST-STORY-001

AS A developer
I WANT the post service to extract @mentions from post text
SO THAT mentioned user IDs are included in the emitted event

### SCENARIO 1: Single mention resolved

**Scenario ID**: POST-BE-001.2-S1

**GIVEN**
* Post text is `"Hello @alice"`
* User `alice` exists with `user_id = "u-123"`

**WHEN**
* Mention parser processes the text

**THEN**
* Returns `mentioned_user_ids: ["u-123"]`

### SCENARIO 2: Unknown mention ignored

**Scenario ID**: POST-BE-001.2-S2

**GIVEN**
* Post text contains `@nobody`
* No user with username `nobody` exists

**WHEN**
* Mention parser processes the text

**THEN**
* Returns `mentioned_user_ids: []`
* No error is raised

---

## POST-INFRA-001.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 — Deployment View; Section 7.3 — Container Mapping (`api`)
**Parent**: POST-STORY-001

AS A developer
I WANT the Docker image to build successfully and the `api` container to start
SO THAT the `POST /posts` endpoint is reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: POST-INFRA-001.1-S1

**GIVEN**
* A `Dockerfile` exists at the project root

**WHEN**
* `docker build -t kata-tests .` is executed

**THEN**
* The build exits with code 0
* No dependency installation errors appear in the output

### SCENARIO 2: Container starts and health check passes

**Scenario ID**: POST-INFRA-001.1-S2

**GIVEN**
* The image has been built successfully

**WHEN**
* `docker compose up api` is executed and `GET /health` is called

**THEN**
* Response is `200 OK`

---

## POST-INFRA-001.2: Create Posts Table (PostgreSQL)

**Architecture Reference**: Section 5.2 — Post Repository; Section 4.3 — Technology Mapping
**Parent**: POST-STORY-001

AS A developer
I WANT a `posts` table created via migration when the `postgres` container starts
SO THAT published posts are persisted

### SCENARIO 1: Post row is insertable

**Scenario ID**: POST-INFRA-001.2-S1

**GIVEN**
* The `postgres` container is running
* The migration has created the `posts` table with columns `(post_id, author_id, text, created_at)`

**WHEN**
* A valid post row is inserted

**THEN**
* The row is retrievable by `post_id`

---

## POST-INFRA-001.3: Configure Redis Stream for post.created Events

**Architecture Reference**: Section 4.2 — Redis Streams as event bus; Section 6.1
**Parent**: POST-STORY-001

AS A developer
I WANT the `posts:events` Redis Stream and consumer groups created at startup
SO THAT the Post Service can emit events consumed by Feed and Notification services

### SCENARIO 1: Event is written and readable by consumer group

**Scenario ID**: POST-INFRA-001.3-S1

**GIVEN**
* The `redis` container is running
* Consumer groups `feed-service` and `notification-service` are registered on stream `posts:events`

**WHEN**
* A `post.created` event is written to the stream

**THEN**
* Both consumer groups can read the event via `XREADGROUP`

---

## POST-INFRA-001.4: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 — Deployment View; Section 7.3 — Container Mapping
**Parent**: POST-STORY-001

AS A developer
I WANT the full pytest suite to execute inside the Docker container
SO THAT post-publishing behaviour is verified in the same environment as CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: POST-INFRA-001.4-S1

**GIVEN**
* The Docker image has been built

**WHEN**
* `docker run --rm kata-tests` is executed

**THEN**
* pytest discovers tests under `tests/`
* All post-publishing tests pass
* Exit code is 0
