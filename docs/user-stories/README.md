# User Stories - Story Inventory

## 📊 Pareto Progress: 5/5 core stories complete (100%)
🎯 Core functionality coverage: ~80% of value delivered

> ⚠️ **INFRA stories target local Docker Compose + pytest** (not AWS).
> All compute is Docker containers; all monitoring is pytest output and container logs.

---

## Core Stories (20% → 80% value)

| ID | Story | Status |
|---|---|---|
| [POST-STORY-001](post-publishing.md) | Publish a post | ✅ Done |
| [USER-STORY-001](user-social-graph.md) | Follow / unfollow a user | ✅ Done |
| [FEED-STORY-001](feed.md) | Read aggregated feed | ✅ Done |
| [NOTIF-STORY-001](notification.md) | Receive @mention notification | ✅ Done |
| [MSG-STORY-001](messaging.md) | Send and receive a direct message | ✅ Done |

---

## Foundational Platform Stories

| ID | Story | Status |
|---|---|---|
| [AUTH-STORY-001](auth.md) | Log in and maintain a session | 📄 Documented |
| [INFRA-STORY-001](infra-stack.md) | Local Docker Compose stack starts end-to-end | 📄 Documented |

---

## Essential Product Stories

| ID | Story | Status |
|---|---|---|
| [USER-STORY-002](user-account.md) | Register / manage account | 📄 Documented |
| [USER-STORY-003](user-profile.md) | View user profile | 📄 Documented |
| [NOTIF-STORY-003](notification-read.md) | Mark notification as read | 📄 Documented |

---

## Supporting Stories (resilience / discoverability)

| ID | Story | Status |
|---|---|---|
| [POST-STORY-002](post-permalink.md) | Share post permalink | 📄 Documented |
| [FEED-STORY-002](feed-fallback.md) | Feed cache miss / SQL fallback | 📄 Documented |
| [NOTIF-STORY-002](notification-recovery.md) | Notification delivery on service recovery | 📄 Documented |

---

## Recommended Implementation Flow

For a working end-to-end platform, stories are recommended in this order:

1. [INFRA-STORY-001](infra-stack.md) - stack starts
2. [USER-STORY-002](user-account.md) - register
3. [AUTH-STORY-001](auth.md) - login
4. [POST-STORY-001](post-publishing.md) - publish
5. [USER-STORY-001](user-social-graph.md) - follow
6. [FEED-STORY-001](feed.md) - read feed
7. [USER-STORY-003](user-profile.md) - view profile
8. [NOTIF-STORY-001](notification.md) - mention notification
9. [NOTIF-STORY-003](notification-read.md) - mark read
10. [MSG-STORY-001](messaging.md) - direct message

Supporting stories can be added after the core product loop is validated.

---

## Gap Analysis (what was missing before this revision)

| Gap | Impact | Resolved by |
|---|---|---|
| No auth story | Platform cannot authenticate any request | [AUTH-STORY-001](auth.md) |
| No docker-compose.yml story | Platform stack cannot start | [INFRA-STORY-001](infra-stack.md) |
| No DB migration story | Tables are never created | [INFRA-BE-001.2](infra-stack.md) |
| No health endpoint story | Compose healthcheck has no target | [INFRA-BE-001.1](infra-stack.md) |
| No profile page story | Follow button has no surface to appear on | [USER-STORY-003](user-profile.md) |
| No mark-read story | Notification badge never clears | [NOTIF-STORY-003](notification-read.md) |
| Password hashing undocumented | Security gap in architecture | [AUTH-INFRA-001.2](auth.md), [Chapter 8](../architecture/08-crosscutting-concepts.md) |
| `get_by_author` missing | Profile page cannot list posts | [USER-BE-003.2](user-profile.md) |
