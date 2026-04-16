# MSG-STORY-001: Send and Receive a Direct Message

**Architecture Reference**: Section 5.1 — Messaging Service; Section 5.4 — Data Isolation Rule; Section 6.3 — Runtime: Send and Receive a Direct Message
**Priority**: Core

---

## Original Story

AS A user
I WANT to send and receive private direct messages
SO THAT I can communicate privately without messages appearing in public feeds

### SCENARIO 1: Successfully send a direct message

**Scenario ID**: MSG-STORY-001-S1

**GIVEN**
* I am authenticated
* The recipient is a registered user

**WHEN**
* I send a message to the recipient

**THEN**
* The message is persisted in the `messages` table
* The message does not appear in any public feed
* The recipient is notified asynchronously

### SCENARIO 2: Retrieve conversation history

**Scenario ID**: MSG-STORY-001-S2

**GIVEN**
* I am authenticated
* I have an existing conversation with `@alice`

**WHEN**
* I open the conversation with `@alice`

**THEN**
* All messages between me and `@alice` are returned in chronological order
* No messages from other conversations are included

### SCENARIO 3: DM is strictly isolated from public posts

**Scenario ID**: MSG-STORY-001-S3

**GIVEN**
* I have sent a DM to `@alice`

**WHEN**
* The feed or post service queries posts

**THEN**
* The `messages` table is never joined or queried by any service other than the Messaging Service (NF-04)

---

## MSG-FE-001.1: Direct Message Conversation UI

**Architecture Reference**: Section 5.1 — Messaging Service; Section 6.3
**Parent**: MSG-STORY-001

AS A user
I WANT a conversation view with a message input
SO THAT I can read and send direct messages

### SCENARIO 1: Messages displayed in chronological order

**Scenario ID**: MSG-FE-001.1-S1

**GIVEN**
* I open a conversation with `@alice`
* The conversation has 3 messages

**WHEN**
* The conversation view loads

**THEN**
* All 3 messages are shown oldest-first
* My messages are visually distinguished from `@alice`'s

### SCENARIO 2: Sending a message appends it to the conversation

**Scenario ID**: MSG-FE-001.1-S2

**GIVEN**
* I am in a conversation with `@alice`

**WHEN**
* I type a message and click "Send"

**THEN**
* The message appears at the bottom of the conversation immediately
* The input field clears

---

## MSG-BE-001.1: Send Direct Message API Endpoint

**Architecture Reference**: Section 5.1 — Messaging Service; Section 6.3
**Parent**: MSG-STORY-001

AS A developer
I WANT a `POST /messages` endpoint
SO THAT clients can send direct messages

### SCENARIO 1: Message is persisted and notification triggered

**Scenario ID**: MSG-BE-001.1-S1

**GIVEN**
* Request has a valid JWT
* Body `{ "recipient_id": "u-alice", "text": "Hello" }` is valid

**WHEN**
* `POST /messages` is called

**THEN**
* A row is inserted into the `messages` table with `sender_id`, `recipient_id`, `text`, `created_at`
* A notification event is dispatched asynchronously to the Notification Service
* Response is `201 Created` with the message ID

### SCENARIO 2: Message to non-existent user is rejected

**Scenario ID**: MSG-BE-001.1-S2

**GIVEN**
* `recipient_id` does not correspond to any registered user

**WHEN**
* `POST /messages` is called

**THEN**
* Response is `404 Not Found`
* No row is inserted

---

## MSG-BE-001.2: Get Conversation API Endpoint

**Architecture Reference**: Section 6.3 — DM retrieval is a direct SQL query scoped to two participants
**Parent**: MSG-STORY-001

AS A developer
I WANT a `GET /messages/{user_id}` endpoint
SO THAT clients can retrieve the conversation between the authenticated user and another user

### SCENARIO 1: Conversation returned in chronological order

**Scenario ID**: MSG-BE-001.2-S1

**GIVEN**
* Request has a valid JWT
* A conversation exists between the authenticated user and `user_id`

**WHEN**
* `GET /messages/{user_id}` is called

**THEN**
* Response is `200 OK` with messages ordered by `created_at` ascending
* Only messages between these two participants are returned

---

## MSG-INFRA-001.1: Deploy Messaging Service

**Architecture Reference**: Section 5.1 — Messaging Service container
**Parent**: MSG-STORY-001

AS A developer
I WANT the Messaging Service deployed as a runnable unit
SO THAT DM endpoints are reachable

### SCENARIO 1: Service starts and health check passes

**Scenario ID**: MSG-INFRA-001.1-S1

**GIVEN**
* The Messaging Service container is deployed

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK`

---

## MSG-INFRA-001.2: Create Messages Table (PostgreSQL)

**Architecture Reference**: Section 5.4 — Data Isolation Rule; Section 4.3 — Direct messages → PostgreSQL
**Parent**: MSG-STORY-001

AS A developer
I WANT a `messages` table in PostgreSQL owned exclusively by the Messaging Service
SO THAT DMs are persisted and strictly isolated from public post data

### SCENARIO 1: Message row is insertable and queryable by participants only

**Scenario ID**: MSG-INFRA-001.2-S1

**GIVEN**
* The `messages` table exists with columns `(message_id, sender_id, recipient_id, text, created_at)`
* No foreign keys reference the `posts` table

**WHEN**
* A message row is inserted

**THEN**
* The row is retrievable by `(sender_id, recipient_id)` pair
* No other service schema references this table

---

## MSG-INFRA-001.3: Configure Async Notification Event for DMs

**Architecture Reference**: Section 6.3 — recipient notified asynchronously via Notification Service
**Parent**: MSG-STORY-001

AS A developer
I WANT the Messaging Service to emit a notification event when a DM is sent
SO THAT the recipient is notified asynchronously

### SCENARIO 1: DM notification event is consumed by Notification Service

**Scenario ID**: MSG-INFRA-001.3-S1

**GIVEN**
* A DM is sent and a `dm.created` event is written to the Redis Stream
* The `notification-service` consumer group is registered on the stream

**WHEN**
* The Notification Service processes the event

**THEN**
* A notification row is created for the recipient with `type: "dm"`

---

## MSG-INFRA-001.4: CloudWatch Monitoring for Messaging Service

**Architecture Reference**: Section 8 — Crosscutting Concepts (observability)
**Parent**: MSG-STORY-001

AS A developer
I WANT log groups and alarms for the Messaging Service
SO THAT errors are observable

### SCENARIO 1: Error rate alarm triggers

**Scenario ID**: MSG-INFRA-001.4-S1

**GIVEN**
* A CloudWatch alarm is configured on 5xx error rate > 1% over 5 minutes

**WHEN**
* The Messaging Service returns > 1% 5xx responses in a 5-minute window

**THEN**
* The alarm transitions to ALARM state
