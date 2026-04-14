# Chapter 2: Architecture Constraints

## 2.1 Technical Constraints

| ID   | Constraint                                                                 |
|------|----------------------------------------------------------------------------|
| T-01 | API layer: Python + FastAPI                                                |
| T-02 | Primary persistence: PostgreSQL                                            |
| T-03 | Cache / feed store: Redis                                                  |
| T-04 | Async messaging: Redis Streams                                             |
| T-05 | All inter-service async communication goes through Redis Streams (no direct service-to-service HTTP for events) |

## 2.2 Organisational Constraints

| ID   | Constraint                                                                 |
|------|----------------------------------------------------------------------------|
| O-01 | Single codebase (monorepo), but with enforced module boundaries            |
| O-02 | Each logical service (user, post, feed, notification, messaging) is an independent Python package |

## 2.3 Conventions

| ID   | Constraint                                                                 |
|------|----------------------------------------------------------------------------|
| C-01 | C4 model for all architecture diagrams                                     |
| C-02 | ADR format: Status / Context / Decision / Rationale / Consequences         |
| C-03 | Public posts and private messages must never share a database table        |
