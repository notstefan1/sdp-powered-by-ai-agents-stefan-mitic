# NOTIF-STORY-001: Receive @mention Notification

**Architecture Reference**: Section 5.1 — Notification Service; Section 6.1 — Runtime: Publish a Post with @mention
**Priority**: Core

---

## Original Story

AS A user
I WANT to be notified when someone mentions me in a post
SO THAT I can respond or engage with the conversation

### SCENARIO 1: Notification created for mentioned user

**Scenario ID**: NOTIF-STORY-001-S1

**GIVEN**
* User `@alice` is mentioned in a post by `@bob`
* The `post.created` event includes `mentioned_user_ids: [alice_id]`

**WHEN**
* The Notification Service processes the event

**THEN**
* An in-app notification is stored for `@alice`
* The notification references the post and the author `@bob`

### SCENARIO 2: Notification delivered within 5 seconds

**Scenario ID**: NOTIF-STORY-001-S2

**GIVEN**
* `@alice` is online
* A `post.created` event with `mentioned_user_ids: [alice_id]` is emitted

**WHEN**
* The Notification Service processes the event

**THEN**
* `@alice` sees the notification within 5 seconds (NF-02)

### SCENARIO 3: Notification Service down — event is not lost

**Scenario ID**: NOTIF-STORY-001-S3

**GIVEN**
* The Notification Service is temporarily down
* A `post.created` event is written to the Redis Stream

**WHEN**
* The Notification Service recovers

**THEN**
* The unprocessed event is consumed from the stream
* The notification is created (at-least-once delivery via Redis Streams consumer groups)

---

## NOTIF-FE-001.1: Notification Bell Component

**Architecture Reference**: Section 5.1 — Notification Service
**Parent**: NOTIF-STORY-001

AS A user
I WANT a notification bell indicator in the UI
SO THAT I can see when I have unread notifications

### SCENARIO 1: Unread count badge appears

**Scenario ID**: NOTIF-FE-001.1-S1

**GIVEN**
* I have 2 unread notifications

**WHEN**
* I view any page

**THEN**
* The bell icon shows a badge with count "2"

### SCENARIO 2: Notification list shows mention detail

**Scenario ID**: NOTIF-FE-001.1-S2

**GIVEN**
* I have a notification for a mention by `@bob`

**WHEN**
* I click the bell icon

**THEN**
* The notification reads "@bob mentioned you in a post"
* Clicking it navigates to the post

---

## NOTIF-BE-001.1: Mention Notification Consumer

**Architecture Reference**: Section 5.1 — Notification Service (async consumer); Section 6.1
**Parent**: NOTIF-STORY-001

AS A developer
I WANT a Redis Streams consumer that creates notifications for @mentions
SO THAT mentioned users are notified asynchronously

### SCENARIO 1: Notification row created for each mentioned user

**Scenario ID**: NOTIF-BE-001.1-S1

**GIVEN**
* A `post.created` event arrives with `mentioned_user_ids: ["u-alice", "u-carol"]`

**WHEN**
* The Notification Service processes the event

**THEN**
* Two rows are inserted into the `notifications` table, one per mentioned user
* Each row contains `{ recipient_id, post_id, author_id, type: "mention", read: false }`

### SCENARIO 2: Event with no mentions is ignored

**Scenario ID**: NOTIF-BE-001.1-S2

**GIVEN**
* A `post.created` event arrives with `mentioned_user_ids: []`

**WHEN**
* The Notification Service processes the event

**THEN**
* No notification rows are inserted
* The event is acknowledged

---

## NOTIF-BE-001.2: Get Notifications API Endpoint

**Architecture Reference**: Section 5.1 — Notification Service
**Parent**: NOTIF-STORY-001

AS A developer
I WANT a `GET /notifications` endpoint
SO THAT clients can retrieve unread notifications for the authenticated user

### SCENARIO 1: Returns unread notifications

**Scenario ID**: NOTIF-BE-001.2-S1

**GIVEN**
* Request has a valid JWT
* The authenticated user has 2 unread notifications

**WHEN**
* `GET /notifications` is called

**THEN**
* Response is `200 OK` with a list of 2 notification objects
* Each object includes `post_id`, `author_id`, `type`, `read`, `created_at`

---

## NOTIF-INFRA-001.1: Docker Image Builds and Worker Container Starts

**Architecture Reference**: Section 7 — Deployment View; Section 7.3 — Container Mapping (`api`, `worker`)
**Parent**: NOTIF-STORY-001

AS A developer
I WANT the Docker image to build and the `worker` container to start
SO THAT the async consumer and notifications endpoint are operational locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: NOTIF-INFRA-001.1-S1

**GIVEN**
* A `Dockerfile` exists at the project root

**WHEN**
* `docker build -t kata-tests .` is executed

**THEN**
* The build exits with code 0

### SCENARIO 2: api container health check passes

**Scenario ID**: NOTIF-INFRA-001.1-S2

**GIVEN**
* `docker compose up api` is running

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK`

---

## NOTIF-INFRA-001.2: Create Notifications Table (PostgreSQL)

**Architecture Reference**: Section 4.3 — Notifications → PostgreSQL
**Parent**: NOTIF-STORY-001

AS A developer
I WANT a `notifications` table created via migration when the `postgres` container starts
SO THAT in-app notifications are persisted

### SCENARIO 1: Notification row is insertable and queryable

**Scenario ID**: NOTIF-INFRA-001.2-S1

**GIVEN**
* The `postgres` container is running
* The migration has created the `notifications` table with columns `(notification_id, recipient_id, post_id, author_id, type, read, created_at)`

**WHEN**
* A notification row is inserted

**THEN**
* The row is retrievable by `recipient_id` filtered on `read = false`

---

## NOTIF-INFRA-001.3: Register Notification Service Consumer Group on Redis Stream

**Architecture Reference**: Section 4.2 — Redis Streams; Section 6.1 — at-least-once delivery
**Parent**: NOTIF-STORY-001

AS A developer
I WANT the `notification-service` consumer group registered on the `posts:events` stream at startup
SO THAT mention events are consumed reliably even after a container restart

### SCENARIO 1: Unprocessed events are consumed after recovery

**Scenario ID**: NOTIF-INFRA-001.3-S1

**GIVEN**
* The `redis` container is running
* Consumer group `notification-service` is registered on stream `posts:events`
* 3 events were written while the `worker` container was down (pending entries)

**WHEN**
* The `worker` container restarts and calls `XREADGROUP GROUP notification-service`

**THEN**
* All 3 pending events are delivered and processed
* Each event is acknowledged with `XACK`

---

## NOTIF-INFRA-001.4: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 — Deployment View
**Parent**: NOTIF-STORY-001

AS A developer
I WANT the full pytest suite to execute inside the Docker container
SO THAT notification behaviour is verified in the same environment as CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: NOTIF-INFRA-001.4-S1

**GIVEN**
* The Docker image has been built

**WHEN**
* `docker run --rm kata-tests` is executed

**THEN**
* pytest discovers tests under `tests/`
* All notification tests pass
* Exit code is 0
