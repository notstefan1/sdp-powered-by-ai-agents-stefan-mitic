# Chapter 1: Introduction and Goals

## 1.1 Purpose

A lightweight social network where users publish short messages, follow each other, receive an aggregated feed, get notified on @mentions, and exchange private direct messages.

The focus of this architecture exercise is **data flow**, not CRUD: how follows affect feed generation, how mentions trigger notifications, and how public posts are separated from private messaging.

---

## 1.2 Requirements Overview

### Functional Requirements

| ID   | Requirement                                                                 |
|------|-----------------------------------------------------------------------------|
| F-01 | Users can publish short public messages (posts)                             |
| F-02 | Users can follow / unfollow other users                                     |
| F-03 | Users see an aggregated feed of posts from everyone they follow             |
| F-04 | Posts may contain @mentions, which trigger notifications to mentioned users |
| F-05 | Users can share a permalink to any public post                              |
| F-06 | Users can send and receive private direct messages (not in public feed)     |

### Non-Functional Requirements

| ID    | Requirement                                                              |
|-------|--------------------------------------------------------------------------|
| NF-01 | Feed reads must be fast (target < 200 ms p95)                            |
| NF-02 | Notification delivery should be near-real-time (< 5 s end-to-end)       |
| NF-03 | The system must remain operational if the notification service is down   |
| NF-04 | Public posts and private messages must be strictly isolated              |
| NF-05 | The architecture must support independent scaling of read-heavy services |

---

## 1.3 Quality Goals

| Priority | Quality Goal      | Motivation                                                        |
|----------|-------------------|-------------------------------------------------------------------|
| 1        | Performance       | Feed reads are the dominant workload; latency directly affects UX |
| 2        | Reliability       | Core posting and reading must work even if async services degrade |
| 3        | Security          | Private messages must never appear in public feeds or APIs        |
| 4        | Maintainability   | Clear service boundaries allow independent evolution              |

---

## 1.4 Stakeholders

| Role              | Expectation                                                        |
|-------------------|--------------------------------------------------------------------|
| End User          | Fast feed, reliable notifications, private messaging               |
| Developer         | Clear service boundaries, easy local setup                         |
| Operator          | Observable system, independent deployability of services           |
