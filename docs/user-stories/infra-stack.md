# INFRA-STORY-001: Local Docker Compose Stack Starts End-to-End

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping
**Priority**: Core (platform cannot run without this)


> AS A developer
> I WANT a single `docker compose up` command to start the full stack
> SO THAT the platform runs locally without manual setup

### SCENARIO 1: Full stack starts with one command

**Scenario ID**: INFRA-STORY-001-S1

:::{admonition} GIVEN
:class: note
* Docker and Docker Compose are installed
* A `docker-compose.yml` exists at the project root
:::

:::{admonition} WHEN
:class: tip
* `docker compose up` is executed
:::

:::{admonition} THEN
:class: important
* `postgres`, `redis`, `api`, and `worker` containers all reach healthy state
* `GET http://localhost:8000/health` returns `200 OK`
:::

### SCENARIO 2: Database tables are created automatically on first start

**Scenario ID**: INFRA-STORY-001-S2

:::{admonition} GIVEN
:class: note
* The `postgres` container starts for the first time (empty volume)
:::

:::{admonition} WHEN
:class: tip
* The `api` container starts
:::

:::{admonition} THEN
:class: important
* All tables (`users`, `follows`, `posts`, `notifications`, `messages`) are created via migration before the first request is served
:::

### SCENARIO 3: Stack restarts cleanly without data loss

**Scenario ID**: INFRA-STORY-001-S3

:::{admonition} GIVEN
:class: note
* The stack has been running and data has been written
:::

:::{admonition} WHEN
:class: tip
* `docker compose restart` is executed
:::

:::{admonition} THEN
:class: important
* PostgreSQL data persists (mounted volume)
* The API is reachable again within 30 seconds
:::

---

## INFRA-FE-001.1: Health / Status Page

**Architecture Reference**: Section 7 - Deployment View
**Parent**: INFRA-STORY-001


> AS A developer
> I WANT a `/health` endpoint visible in the browser
> SO THAT I can confirm the stack is running during local validation

### SCENARIO 1: Health endpoint returns service status

**Scenario ID**: INFRA-FE-001.1-S1

:::{admonition} GIVEN
:class: note
* The `api` container is running
:::

:::{admonition} WHEN
:class: tip
* `GET /health` is called
:::

:::{admonition} THEN
:class: important
* Response is `200 OK` with `{ "status": "ok", "postgres": "ok", "redis": "ok" }`
:::

---

## INFRA-BE-001.1: Health Check Endpoint

**Architecture Reference**: Section 7 - Deployment View; Section 8.3 - Observability
**Parent**: INFRA-STORY-001


> AS A developer
> I WANT a `GET /health` endpoint that probes PostgreSQL and Redis
> SO THAT container orchestration and CI can verify the stack is ready

### SCENARIO 1: All dependencies healthy

**Scenario ID**: INFRA-BE-001.1-S1

:::{admonition} GIVEN
:class: note
* PostgreSQL and Redis are reachable
:::

:::{admonition} WHEN
:class: tip
* `GET /health` is called
:::

:::{admonition} THEN
:class: important
* Response is `200 OK` with `{ "status": "ok", "postgres": "ok", "redis": "ok" }`
:::

### SCENARIO 2: Degraded dependency reported

**Scenario ID**: INFRA-BE-001.1-S2

:::{admonition} GIVEN
:class: note
* Redis is unreachable
:::

:::{admonition} WHEN
:class: tip
* `GET /health` is called
:::

:::{admonition} THEN
:class: important
* Response is `200 OK` with `{ "status": "degraded", "postgres": "ok", "redis": "error" }`
* The API does not crash
:::

---

## INFRA-BE-001.2: Database Migrations Run at Startup

**Architecture Reference**: Section 7 - Deployment View; Section 4.3 - Technology Mapping
**Parent**: INFRA-STORY-001


> AS A developer
> I WANT all database tables created automatically when the `api` container starts
> SO THAT no manual SQL setup is needed for local and CI environments

### SCENARIO 1: All tables exist after first startup

**Scenario ID**: INFRA-BE-001.2-S1

:::{admonition} GIVEN
:class: note
* PostgreSQL is running with an empty database
:::

:::{admonition} WHEN
:class: tip
* The `api` container starts
:::

:::{admonition} THEN
:class: important
* Tables `users`, `follows`, `posts`, `notifications`, `messages` all exist
* The `users` table has a unique constraint on `username`
* The `notifications` table has a unique constraint on `(recipient_id, type, entity_type, entity_id)`
:::

### SCENARIO 2: Migrations are idempotent

**Scenario ID**: INFRA-BE-001.2-S2

:::{admonition} GIVEN
:class: note
* Tables already exist from a previous run
:::

:::{admonition} WHEN
:class: tip
* The `api` container restarts and runs migrations again
:::

:::{admonition} THEN
:class: important
* No error is raised
* Existing data is preserved
:::

---

## INFRA-BE-001.3: docker-compose.yml Defines All Services

**Architecture Reference**: Section 7.3 - Container Mapping
**Parent**: INFRA-STORY-001


> AS A developer
> I WANT a `docker-compose.yml` that defines `api`, `worker`, `postgres`, and `redis`
> SO THAT the full stack starts with one command

### SCENARIO 1: All four services are defined

**Scenario ID**: INFRA-BE-001.3-S1

:::{admonition} GIVEN
:class: note
* `docker-compose.yml` exists
:::

:::{admonition} WHEN
:class: tip
* `docker compose config` is run
:::

:::{admonition} THEN
:class: important
* Services `api`, `worker`, `postgres`, `redis` are all present
* `api` depends on `postgres` and `redis`
* `worker` depends on `postgres` and `redis`
* A named volume is mounted for PostgreSQL data persistence
:::

---

## INFRA-INFRA-001.1: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: INFRA-STORY-001


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT infrastructure behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: INFRA-INFRA-001.1-S1

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
* All tests pass
* Exit code is 0
:::
