# Social Network Platform

A lightweight social network where users publish short posts, follow each other, receive an aggregated feed, get notified on @mentions, and exchange private direct messages.

Built as the hands-on project for the **Software Development Processes Powered by AI Agents** course - each engineering workflow (architecture, requirements, CI/CD, TDD/BDD) was automated by a dedicated AI agent.

## Features

- User registration, login, and profile management (JWT auth)
- Publish short public posts with @mention support
- Follow / unfollow users and read an aggregated feed
- Real-time @mention notifications via Redis Streams
- Private direct messaging (strictly isolated from public feed)
- Shareable post permalinks

## Tech stack

| Concern | Choice |
|---|---|
| API | FastAPI + Uvicorn |
| Auth | JWT Bearer tokens (PyJWT + bcrypt) |
| Database | PostgreSQL 16 |
| Cache / feed store | Redis 7 |
| Async events | Redis Streams (background worker) |
| Deployment | Docker Compose |

## Project structure

```
src/
  api.py          # FastAPI app - HTTP layer
  auth.py         # JWT auth service
  user.py         # User & social graph service
  post.py         # Post publishing service
  feed.py         # Feed aggregation service
  notification.py # @mention notification service
  messaging.py    # Private direct messaging service
  worker.py       # Redis Streams background worker
  db.py           # DB connection & migrations
migrations/
  001_initial.sql # Schema
tests/            # Unit + integration tests (pytest)
docs/             # arc42 architecture docs & user stories
```

## Prerequisites

- Docker and Docker Compose

## Running locally

1. Copy the example env file:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up
```

The API is available at `http://localhost:8000`.
Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## Running tests

Unit tests (no infrastructure required):

```bash
docker compose run --rm -e TESTING=1 api pytest tests/ -v --tb=short
```

Full test suite including integration tests (requires postgres + redis):

```bash
docker compose --profile test run --rm test
```

## Environment variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret key for signing JWT tokens (min 32 chars) |
| `POSTGRES_USER` | Postgres username (used by Docker Compose) |
| `POSTGRES_PASSWORD` | Postgres password (used by Docker Compose) |
| `POSTGRES_DB` | Postgres database name (used by Docker Compose) |

See `.env.example` for defaults.

## CI

GitHub Actions runs two jobs on every push to `main`, `feature/**`, and `fix/**`:

- **unit-tests** - runs pytest inside Docker with `TESTING=1` (no external services)
- **integration-tests** - runs pytest against live Postgres and Redis service containers

## Documentation

Full project documentation lives under `docs/`:

- [`docs/architecture/`](docs/architecture/01-introduction-and-goals.md) - arc42 architecture documentation with C4/PlantUML diagrams
- [`docs/user-stories/`](docs/user-stories/README.md) - user story inventory and Pareto backlog
- [`docs/ddd-ubiquitous-language.md`](docs/ddd-ubiquitous-language.md) - domain glossary
