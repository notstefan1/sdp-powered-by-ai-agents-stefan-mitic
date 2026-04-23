# Social Network Platform

A lightweight social network where users publish short posts, follow each other, receive an aggregated feed, get notified on @mentions, and exchange private direct messages.

## What this project covers

This project was built as part of a hands-on course in AI-assisted software development. Each module introduced an AI agent that automated a core engineering workflow:

- **Architecture** - arc42 documentation generated chapter by chapter with C4/PlantUML diagrams
- **Requirements** - user stories derived from architecture using DDD bounded contexts and Pareto prioritization
- **CI/CD** - Dockerfile and GitHub Actions pipeline generated from project structure
- **TDD/BDD** - features implemented scenario by scenario under strict RED-GREEN-REFACTOR discipline

## System at a glance

| Concern | Choice |
|---|---|
| Transport | REST over HTTP |
| Auth | JWT Bearer tokens |
| Primary store | PostgreSQL (schema-per-service) |
| Cache / feed store | Redis |
| Async events | Redis Streams |
| Deployment | Docker Compose |

## Domains

| Domain | Responsibility |
|---|---|
| User | Registration, login, profile |
| Post | Publishing short messages |
| Feed | Aggregated timeline per user |
| Social Graph | Follow / unfollow relationships |
| Notification | @mention alerts |
| Messaging | Private direct messages |

## Documentation

- [Architecture](architecture/01-introduction-and-goals) - full arc42 documentation
- [User Stories](user-stories/README) - story inventory and Pareto backlog
