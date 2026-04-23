# Demo Script

A social network built with FastAPI, PostgreSQL, Redis, and Docker.

---

## Story Coverage

| Story ID | Title | Demo Step |
|---|---|---|
| AUTH-STORY-001 | Log in and maintain a session | Step 1 |
| USER-STORY-002 | Register / manage account | Step 1 |
| USER-STORY-001 | Follow / unfollow a user | Step 3 |
| USER-STORY-003 | View user profile | Step 6 |
| POST-STORY-001 | Publish a post | Step 2 |
| POST-STORY-002 | Share post permalink | Step 7 |
| FEED-STORY-001 | Read aggregated feed | Step 2 |
| FEED-STORY-002 | Feed cache miss / SQL fallback | Step 8 |
| NOTIF-STORY-001 | Receive @mention notification | Step 4 |
| NOTIF-STORY-002 | Notification delivery on service recovery | Step 4 |
| NOTIF-STORY-003 | Mark notification as read | Step 4 |
| MSG-STORY-001 | Send and receive a direct message | Step 5 |
| INFRA-STORY-001 | Local Docker Compose stack starts end-to-end | Step 9 |

---

## Prerequisites

- Docker and Docker Compose installed
- Ports 8000 free

---

## Setup (do this before the demo)

**1. Start the stack**

```bash
docker compose up -d --build
```

Wait for all containers to be healthy (~10s), then verify:

```bash
curl http://localhost:8000/health
# {"status":"ok","postgres":"ok","redis":"ok"}
```

**2. Seed demo data**

```bash
docker compose run --rm \
  -e DATABASE_URL=postgresql://app:app@postgres:5432/app `# pragma: allowlist secret` \
  -e REDIS_URL=redis://redis:6379 \
  api python scripts/seed.py
```

This creates three users with pre-existing posts, follows, and DMs:

| Username | Password     |
|----------|--------------|
| alice    | password123  |
| bob      | password123  |
| carol    | password123  |

**3. Open the app**

Navigate to **http://localhost:8000** in your browser.

---

## Demo Flow

### Step 1 - Authentication
*Stories: AUTH-STORY-001, AUTH-BE-001.1, AUTH-BE-001.2*

- Show the login/register tabs
- Register a **new account** (e.g. `dave` / `password123`) - show it redirects to login on success
- Log in as `dave` - show the feed is empty ("No posts yet")
- Log out
- Log in as **alice**

> **Talking point:** JWT-based auth. Token stored in localStorage, auto-logout if token becomes invalid.

---

### Step 2 - Feed & Publishing
*Stories: POST-STORY-001, POST-BE-001.1, POST-BE-001.2, FEED-STORY-001, FEED-BE-001.1*

- As `alice`, show the feed - posts from bob and carol appear (she follows both)
- Type a post in the compose box - show the character counter
- Submit - post appears at the top of the feed immediately
- Click **Refresh** - post is still there (persisted in PostgreSQL)

> **Talking point:** Feed is materialised in Redis sorted sets (fan-out on write). On cache miss it falls back to a SQL query and backfills Redis.

---

### Step 3 - Follow / Unfollow
*Stories: USER-STORY-001, USER-BE-001.1, USER-BE-001.2, FEED-BE-001.2*

- Go to **People** tab
- Search for `dave` (the account you just created)
- Click **Follow** - button changes to Unfollow
- Click **Unfollow** - button reverts
- Open a second browser tab, log in as `dave`
- As `alice`, post something
- As `dave`, refresh the feed - alice's post appears (fan-out via Redis Stream + worker)

> **Talking point:** Follow relationships stored in PostgreSQL. Feed fan-out is async via the worker consuming the `posts:events` Redis Stream.

---

### Step 4 - @Mention Notifications
*Stories: NOTIF-STORY-001, NOTIF-BE-001.1, NOTIF-STORY-002, NOTIF-INFRA-001.3*

- As `alice`, publish a post containing `@dave`
- Switch to the `dave` tab
- Within ~10 seconds the **notification bell badge** appears
- Click **Notifications** - see "@alice mentioned you in a post"
- Click **Mark read** - badge disappears

> **Talking point:** Worker consumes `posts:events` stream, resolves @mentions via DB lookup, writes notification rows. At-least-once delivery via consumer groups and XAUTOCLAIM on restart.

---

### Step 5 - Direct Messages
*Stories: MSG-STORY-001, MSG-BE-001.1, MSG-BE-001.2, MSG-STORY-001-S3 (data isolation)*

- As `alice`, go to **Messages** tab
- Search for `bob` - click **Message**
- Existing conversation with bob is loaded (seeded data)
- Send a new message - it appears in the thread
- Switch to `bob`'s tab - go to Messages, search `alice`, open thread - message is there

> **Talking point:** DMs are stored in a separate `messages` table, never joined with public post queries (data isolation rule NF-04).

---

### Step 6 - Profile Page
*Stories: USER-STORY-003, USER-BE-003.1, USER-BE-003.2, USER-BE-003.3*

- Click **Profile** in the nav - shows your own posts and follower/following counts
- In the feed, click any **@username** - opens their profile
- Profile shows their posts, follower count, and a Follow/Unfollow button

---

### Step 7 - Post Permalink
*Stories: POST-STORY-002, POST-BE-002.1*

- In the feed, click **permalink** on any post
- Opens in a new tab showing just that post (shareable URL by post ID)

---

### Step 8 - Persistence Across Restarts
*Stories: INFRA-STORY-001-S3, FEED-STORY-002*

```bash
docker compose restart api worker
```

- Refresh the browser - auto-logout (token still valid but shows the flow)
- Log back in - all posts, follows, and DMs are still there

> **Talking point:** PostgreSQL data is on a named Docker volume (`pgdata`). Redis feed cache is rebuilt from SQL on cold start.

---

### Step 9 - Health & Infrastructure
*Stories: INFRA-STORY-001, INFRA-BE-001.1, INFRA-BE-001.2, INFRA-BE-001.3*

```bash
curl http://localhost:8000/health
# {"status":"ok","postgres":"ok","redis":"ok"}
```

Show `docker compose ps` - four containers running: `api`, `worker`, `postgres`, `redis`.

> **Talking point:** Single `docker compose up` starts the full stack. DB migrations run automatically on API startup from `.sql` files.

---

## Teardown

```bash
docker compose down -v   # removes containers AND data volume
```

To keep data between sessions:

```bash
docker compose down      # stops containers, preserves volume
docker compose up -d     # restarts with existing data
```

---

## Architecture Summary (one slide)

```
Browser → FastAPI (api:8000)
              ├── PostgreSQL  (users, follows, posts, messages, notifications)
              ├── Redis       (feed sorted sets + posts:events stream)
              └── Worker      (consumes stream → fan-out + notifications)
```

- **Feed reads:** Redis ZREVRANGE → SQL fallback on miss
- **Post writes:** DB insert → Redis Stream event → worker fans out
- **Notifications:** async, at-least-once via Redis Streams consumer groups
- **Auth:** JWT (HS256), validated on every protected route
