# NOTIF-STORY-002: Notification Delivery on Service Recovery

**Architecture Reference**: Section 5.1 - Notification Service; Section 4.2 - Redis Streams (at-least-once delivery); Section 6.1 - Notification Service down scenario
**Priority**: Supporting


> AS A user
> I WANT to receive notifications that were generated while the notification service was down
> SO THAT no mention or DM notification is silently lost during a service outage

### SCENARIO 1: Pending events are processed after worker restart

**Scenario ID**: NOTIF-STORY-002-S1

:::{admonition} GIVEN
:class: note
* The `worker` container was down
* 3 `post.created` events with mentions were written to the Redis Stream during the outage
:::

:::{admonition} WHEN
:class: tip
* The `worker` container restarts and calls `XREADGROUP GROUP notification-service`
:::

:::{admonition} THEN
:class: important
* All 3 pending events are delivered to the consumer
* A notification row is created for each mentioned user
* Each event is acknowledged with `XACK`
:::

### SCENARIO 2: Already-processed events are not re-delivered

**Scenario ID**: NOTIF-STORY-002-S2

:::{admonition} GIVEN
:class: note
* An event has been processed and acknowledged
:::

:::{admonition} WHEN
:class: tip
* The consumer restarts and reads from the stream
:::

:::{admonition} THEN
:class: important
* The acknowledged event is not re-delivered
* No duplicate notification is created
:::

### SCENARIO 3: Unacknowledged event is re-delivered on restart

**Scenario ID**: NOTIF-STORY-002-S3

:::{admonition} GIVEN
:class: note
* An event was consumed but not acknowledged before the worker crashed
:::

:::{admonition} WHEN
:class: tip
* The worker restarts and claims pending entries via `XAUTOCLAIM`
:::

:::{admonition} THEN
:class: important
* The event is re-processed
* The notification is created (idempotent: duplicate check prevents double insert)
:::

---

## NOTIF-FE-002.1: Notification Delivery Status Indicator

**Architecture Reference**: Section 5.1 - Notification Service
**Parent**: NOTIF-STORY-002


> AS A user
> I WANT to see notifications that arrived during a brief service interruption
> SO THAT I don't miss mentions that occurred while the service was recovering

### SCENARIO 1: Backlogged notifications appear after recovery

**Scenario ID**: NOTIF-FE-002.1-S1

:::{admonition} GIVEN
:class: note
* The notification service was briefly down
* 2 mention notifications were queued
:::

:::{admonition} WHEN
:class: tip
* The service recovers and I refresh the notification bell
:::

:::{admonition} THEN
:class: important
* Both notifications appear in the list
* The unread badge shows count 2
:::

---

## NOTIF-BE-002.1: Idempotent Notification Creation

**Architecture Reference**: Section 5.1 - Notification Service; Section 4.2 - at-least-once delivery
**Parent**: NOTIF-STORY-002


> AS A developer
> I WANT `NotificationService.handle_post_created` to be idempotent on duplicate events
> SO THAT re-delivered stream events do not create duplicate notifications

### SCENARIO 1: Duplicate event does not create a second notification

**Scenario ID**: NOTIF-BE-002.1-S1

:::{admonition} GIVEN
:class: note
* A `post.created` event for `post_id="post-1"` has already been processed
* A notification for `(recipient_id, post_id)` already exists
:::

:::{admonition} WHEN
:class: tip
* The same event is processed again (re-delivery)
:::

:::{admonition} THEN
:class: important
* No second notification row is created
* The existing notification is unchanged
:::

### SCENARIO 2: New event for same recipient creates a new notification

**Scenario ID**: NOTIF-BE-002.1-S2

:::{admonition} GIVEN
:class: note
* A notification for `(recipient_id="u-alice", post_id="post-1")` exists
:::

:::{admonition} WHEN
:class: tip
* A new event for `post_id="post-2"` mentioning `u-alice` is processed
:::

:::{admonition} THEN
:class: important
* A second notification is created for `post-2`
* Total unread count for `u-alice` is 2
:::

---

## NOTIF-INFRA-002.1: Docker Image Builds and Worker Container Starts

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping (`worker`)
**Parent**: NOTIF-STORY-002


> AS A developer
> I WANT the Docker image to build and the `worker` container to start
> SO THAT the recovery path is exercisable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: NOTIF-INFRA-002.1-S1

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

## NOTIF-INFRA-002.2: Notifications Table Has Unique Constraint on (recipient_id, type, entity_type, entity_id)

**Architecture Reference**: Section 4.3 - Notifications → PostgreSQL; Section 4.2 - at-least-once delivery
**Parent**: NOTIF-STORY-002


> AS A developer
> I WANT a unique constraint on `(recipient_id, type, entity_type, entity_id)` in the `notifications` table
> SO THAT duplicate stream re-deliveries cannot insert duplicate rows at the database level

### SCENARIO 1: Duplicate notification insert is rejected by the DB

**Scenario ID**: NOTIF-INFRA-002.2-S1

:::{admonition} GIVEN
:class: note
* The `postgres` container is running
* A notification row `(recipient_id="u-alice", type="mention", entity_type="post", entity_id="post-1")` exists
:::

:::{admonition} WHEN
:class: tip
* An identical row is inserted
:::

:::{admonition} THEN
:class: important
* A unique constraint violation is raised
* The original row is unchanged
:::

---

## NOTIF-INFRA-002.3: Consumer Group Pending Entry Recovery via XAUTOCLAIM

**Architecture Reference**: Section 4.2 - Redis Streams consumer groups; Section 6.1 - at-least-once delivery
**Parent**: NOTIF-STORY-002


> AS A developer
> I WANT the `notification-service` consumer to use `XAUTOCLAIM` on startup
> SO THAT messages pending from a crashed consumer are reclaimed and processed

### SCENARIO 1: Pending entries are reclaimed after worker restart

**Scenario ID**: NOTIF-INFRA-002.3-S1

:::{admonition} GIVEN
:class: note
* The `redis` container is running
* Consumer group `notification-service` is registered on stream `posts:events`
* 2 events are in the Pending Entry List (delivered but not acknowledged)
:::

:::{admonition} WHEN
:class: tip
* The worker restarts and calls `XAUTOCLAIM GROUP notification-service`
:::

:::{admonition} THEN
:class: important
* Both pending events are returned to the new consumer instance
* After processing, both are acknowledged with `XACK`
:::

---

## NOTIF-INFRA-002.4: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: NOTIF-STORY-002


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT notification recovery behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: NOTIF-INFRA-002.4-S1

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
* All notification recovery tests pass
* Exit code is 0
:::
