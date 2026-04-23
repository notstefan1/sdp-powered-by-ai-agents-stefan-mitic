# USER-STORY-002: Register / Manage Account

**Architecture Reference**: Section 5.1 - User Service; Section 4.3 - Technology Mapping (social graph + users → PostgreSQL)
**Priority**: Supporting


> AS A visitor
> I WANT to register an account and manage my profile
> SO THAT I can participate in the platform

### SCENARIO 1: Successful registration

**Scenario ID**: USER-STORY-002-S1

:::{admonition} GIVEN
:class: note
* The username is not already taken
* The email is not already registered
:::

:::{admonition} WHEN
:class: tip
* I submit a registration form with username and email
:::

:::{admonition} THEN
:class: important
* A user record is created with a generated `user_id`
* The response contains `user_id` and `username`
:::

### SCENARIO 2: Duplicate username rejected

**Scenario ID**: USER-STORY-002-S2

:::{admonition} GIVEN
:class: note
* A user with the same username already exists
:::

:::{admonition} WHEN
:class: tip
* I attempt to register with that username
:::

:::{admonition} THEN
:class: important
* Registration is rejected with a `username_taken` error
* No duplicate record is created
:::

### SCENARIO 3: Update display name

**Scenario ID**: USER-STORY-002-S3

:::{admonition} GIVEN
:class: note
* I am a registered user
:::

:::{admonition} WHEN
:class: tip
* I update my display name
:::

:::{admonition} THEN
:class: important
* The new display name is persisted and returned on profile lookup
:::

---

## USER-FE-002.1: Registration Form Component

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-002


> AS A visitor
> I WANT a registration form
> SO THAT I can create an account

### SCENARIO 1: Valid form submits successfully

**Scenario ID**: USER-FE-002.1-S1

:::{admonition} GIVEN
:class: note
* The registration form is empty
:::

:::{admonition} WHEN
:class: tip
* I fill in username and email and submit
:::

:::{admonition} THEN
:class: important
* I am redirected to the home page
* My username is shown in the nav bar
:::

### SCENARIO 2: Duplicate username shows inline error

**Scenario ID**: USER-FE-002.1-S2

:::{admonition} GIVEN
:class: note
* The username is already taken
:::

:::{admonition} WHEN
:class: tip
* I submit the form
:::

:::{admonition} THEN
:class: important
* An inline error "Username already taken" is displayed
* The form is not cleared
:::

---

## USER-FE-002.2: Profile Edit Component

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-002


> AS A registered user
> I WANT an edit profile form
> SO THAT I can update my display name

### SCENARIO 1: Display name update is reflected immediately

**Scenario ID**: USER-FE-002.2-S1

:::{admonition} GIVEN
:class: note
* I am on my profile page
:::

:::{admonition} WHEN
:class: tip
* I change my display name and save
:::

:::{admonition} THEN
:class: important
* The new display name appears on the profile page without a full reload
:::

---

## USER-BE-002.1: Register User

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-002


> AS A developer
> I WANT a `register(username, email)` method on `UserService`
> SO THAT new accounts can be created with unique usernames

### SCENARIO 1: New user is created and returned

**Scenario ID**: USER-BE-002.1-S1

:::{admonition} GIVEN
:class: note
* No user with the given username exists
:::

:::{admonition} WHEN
:class: tip
* `register(username, email)` is called
:::

:::{admonition} THEN
:class: important
* A user record is stored with a generated `user_id`
* The returned dict contains `user_id` and `username`
:::

### SCENARIO 2: Duplicate username raises error

**Scenario ID**: USER-BE-002.1-S2

:::{admonition} GIVEN
:class: note
* A user with the same username already exists
:::

:::{admonition} WHEN
:class: tip
* `register(username, email)` is called again with the same username
:::

:::{admonition} THEN
:class: important
* `ValueError("username_taken")` is raised
* No second record is created
:::

---

## USER-BE-002.2: Update Profile

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-002


> AS A developer
> I WANT an `update_profile(user_id, display_name)` method on `UserService`
> SO THAT users can change their display name

### SCENARIO 1: Display name is updated

**Scenario ID**: USER-BE-002.2-S1

:::{admonition} GIVEN
:class: note
* A registered user exists
:::

:::{admonition} WHEN
:class: tip
* `update_profile(user_id, display_name="New Name")` is called
:::

:::{admonition} THEN
:class: important
* The user record reflects the new display name
:::

### SCENARIO 2: Unknown user raises error

**Scenario ID**: USER-BE-002.2-S2

:::{admonition} GIVEN
:class: note
* No user with the given `user_id` exists
:::

:::{admonition} WHEN
:class: tip
* `update_profile(user_id, display_name="X")` is called
:::

:::{admonition} THEN
:class: important
* `ValueError("user_not_found")` is raised
:::

---

## USER-INFRA-002.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping (`api`)
**Parent**: USER-STORY-002


> AS A developer
> I WANT the Docker image to build and the `api` container to start
> SO THAT account management endpoints are reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: USER-INFRA-002.1-S1

:::{admonition} GIVEN
:class: note
* A `Dockerfile` exists at the project root
:::

:::{admonition} WHEN
:class: tip
* `docker build -t kata-tests .` is executed
:::

:::{admonition} THEN
:class: important
* The build exits with code 0
:::

---

## USER-INFRA-002.2: Users Table Supports Account Fields

**Architecture Reference**: Section 4.3 - Technology Mapping (social graph + users → PostgreSQL)
**Parent**: USER-STORY-002


> AS A developer
> I WANT the `users` table to store `(user_id, username, email, display_name, created_at)` with a unique constraint on `username`
> SO THAT account registration and profile updates are persisted

### SCENARIO 1: User row is insertable and queryable by username

**Scenario ID**: USER-INFRA-002.2-S1

:::{admonition} GIVEN
:class: note
* The `postgres` container is running
* The `users` table exists with a unique constraint on `username`
:::

:::{admonition} WHEN
:class: tip
* A user row is inserted
:::

:::{admonition} THEN
:class: important
* The row is retrievable by `username`
* A duplicate `username` insert raises a unique constraint violation
:::

---

## USER-INFRA-002.3: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: USER-STORY-002


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT account management behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: USER-INFRA-002.3-S1

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
* All account management tests pass
* Exit code is 0
:::
