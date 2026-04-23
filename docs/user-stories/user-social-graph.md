# USER-STORY-001: Follow / Unfollow a User

**Architecture Reference**: Section 5.1 — User Service; Section 3.4 — System Boundaries (social graph)
**Priority**: Core

---

## Original Story

AS A user
I WANT to follow and unfollow other users
SO THAT their posts appear in or are removed from my feed

### SCENARIO 1: Successfully follow a user

**Scenario ID**: USER-STORY-001-S1

**GIVEN**
* I am authenticated
* I am not already following `@alice`

**WHEN**
* I follow `@alice`

**THEN**
* The follow relationship is persisted
* `@alice`'s future posts appear in my feed

### SCENARIO 2: Successfully unfollow a user

**Scenario ID**: USER-STORY-001-S2

**GIVEN**
* I am authenticated
* I am currently following `@alice`

**WHEN**
* I unfollow `@alice`

**THEN**
* The follow relationship is removed
* `@alice`'s posts no longer appear in my feed

### SCENARIO 3: Follow a user I already follow

**Scenario ID**: USER-STORY-001-S3

**GIVEN**
* I am already following `@alice`

**WHEN**
* I attempt to follow `@alice` again

**THEN**
* Response is `409 Conflict`
* No duplicate relationship is created

---

## USER-FE-001.1: Follow / Unfollow Button Component

**Architecture Reference**: Section 5.1 — User Service
**Parent**: USER-STORY-001

AS A user
I WANT a follow/unfollow toggle button on user profiles
SO THAT I can manage who I follow

### SCENARIO 1: Follow button triggers follow action

**Scenario ID**: USER-FE-001.1-S1

**GIVEN**
* I am viewing `@alice`'s profile
* I am not following `@alice`

**WHEN**
* I click "Follow"

**THEN**
* The button changes to "Unfollow"
* A success indicator is shown

### SCENARIO 2: Unfollow button triggers unfollow action

**Scenario ID**: USER-FE-001.1-S2

**GIVEN**
* I am viewing `@alice`'s profile
* I am currently following `@alice`

**WHEN**
* I click "Unfollow"

**THEN**
* The button changes to "Follow"

---

## USER-BE-001.1: Follow User API Endpoint

**Architecture Reference**: Section 5.1 — User Service (social graph)
**Parent**: USER-STORY-001

AS A developer
I WANT a `POST /users/{user_id}/follow` endpoint
SO THAT clients can create follow relationships

### SCENARIO 1: Follow relationship is created

**Scenario ID**: USER-BE-001.1-S1

**GIVEN**
* Request has a valid JWT
* `user_id` exists and is not the authenticated user
* No existing follow relationship

**WHEN**
* `POST /users/{user_id}/follow` is called

**THEN**
* A row is inserted into the `follows` table `(follower_id, followee_id)`
* Response is `201 Created`

### SCENARIO 2: Duplicate follow returns conflict

**Scenario ID**: USER-BE-001.1-S2

**GIVEN**
* Follow relationship already exists

**WHEN**
* `POST /users/{user_id}/follow` is called

**THEN**
* Response is `409 Conflict`
* No duplicate row is inserted

---

## USER-BE-001.2: Unfollow User API Endpoint

**Architecture Reference**: Section 5.1 — User Service (social graph)
**Parent**: USER-STORY-001

AS A developer
I WANT a `DELETE /users/{user_id}/follow` endpoint
SO THAT clients can remove follow relationships

### SCENARIO 1: Follow relationship is removed

**Scenario ID**: USER-BE-001.2-S1

**GIVEN**
* Request has a valid JWT
* Follow relationship exists

**WHEN**
* `DELETE /users/{user_id}/follow` is called

**THEN**
* The row is deleted from the `follows` table
* Response is `204 No Content`

### SCENARIO 2: Unfollow non-followed user

**Scenario ID**: USER-BE-001.2-S2

**GIVEN**
* No follow relationship exists

**WHEN**
* `DELETE /users/{user_id}/follow` is called

**THEN**
* Response is `404 Not Found`

---

## USER-INFRA-001.1: Docker Image Builds and User Service Container Starts

**Architecture Reference**: Section 7 — Deployment View; Section 7.3 — Container Mapping (`api`)
**Parent**: USER-STORY-001

AS A developer
I WANT the Docker image to build and the `api` container to start
SO THAT follow/unfollow endpoints are reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: USER-INFRA-001.1-S1

**GIVEN**
* A `Dockerfile` exists at the project root

**WHEN**
* `docker build -t kata-tests .` is executed

**THEN**
* The build exits with code 0

### SCENARIO 2: Container starts and health check passes

**Scenario ID**: USER-INFRA-001.1-S2

**GIVEN**
* `docker compose up api` is running

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK`

---

## USER-INFRA-001.2: Create Follows Table (PostgreSQL)

**Architecture Reference**: Section 4.3 — Technology Mapping (social graph → PostgreSQL)
**Parent**: USER-STORY-001

AS A developer
I WANT a `follows` table created via migration when the `postgres` container starts
SO THAT follow relationships are persisted

### SCENARIO 1: Follow row is insertable and queryable

**Scenario ID**: USER-INFRA-001.2-S1

**GIVEN**
* The `postgres` container is running
* The migration has created the `follows` table with columns `(follower_id, followee_id, created_at)` and a unique constraint on `(follower_id, followee_id)`

**WHEN**
* A follow row is inserted

**THEN**
* The row is retrievable by `follower_id`
* A duplicate insert raises a unique constraint violation

---

## USER-INFRA-001.3: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 — Deployment View
**Parent**: USER-STORY-001

AS A developer
I WANT the full pytest suite to execute inside the Docker container
SO THAT social graph behaviour is verified in the same environment as CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: USER-INFRA-001.3-S1

**GIVEN**
* The Docker image has been built

**WHEN**
* `docker run --rm kata-tests` is executed

**THEN**
* pytest discovers tests under `tests/`
* All user/social-graph tests pass
* Exit code is 0
