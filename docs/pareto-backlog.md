# Pareto-Prioritized Backlog (80/20 Rule)

## Principle
20% of features deliver 80% of user value. Core stories are prioritized first to maximize impact before investing in supporting functionality.

---

## 🎯 Core Stories — 20% effort → ~80% value

| Priority | ID | Story | Value Driver |
|---|---|---|---|
| 1 | POST-STORY-001 | Publish a post | Primary user action; without it the platform has no content |
| 2 | USER-STORY-001 | Follow / unfollow a user | Defines the social graph; enables personalized feeds |
| 3 | FEED-STORY-001 | Read aggregated feed | Core consumption loop; drives daily active usage |
| 4 | NOTIF-STORY-001 | Receive @mention notification | Closes the engagement loop; brings users back |
| 5 | MSG-STORY-001 | Send and receive a direct message | Enables private interaction; key retention driver |

**Status: 5/5 complete ✅**

---

## 🔧 Supporting Stories — 80% effort → ~20% value

| Priority | ID | Story | Value Driver |
|---|---|---|---|
| 6 | USER-STORY-002 | Register / manage account | Prerequisite for all features but low incremental value once auth exists |
| 7 | POST-STORY-002 | Share post permalink | Improves discoverability; secondary engagement |
| 8 | FEED-STORY-002 | Feed cache miss / SQL fallback | Resilience improvement; edge case handling |
| 9 | NOTIF-STORY-002 | Notification delivery on service recovery | Reliability improvement; low user-facing impact |

**Status: 0/4 complete ⏳**

---

## Rationale

The five core stories form the minimum viable social loop:
1. A user **publishes** content
2. Other users **follow** them to subscribe
3. Followers **read** the content in their feed
4. Authors are **notified** when mentioned, driving re-engagement
5. Users **message** each other privately, deepening relationships

Supporting stories improve resilience and discoverability but do not unlock new user behaviors — they are deferred until the core loop is validated.
