# AUTH-STORY-001: Log In and Maintain a Session

**Architecture Reference**: Section 8.1 - Authentication & Authorisation; Section 3.4 - System Boundaries (auth provider assumed external)
**Priority**: Core (blocking - no other story works without an identity)


> AS A registered user
> I WANT to log in with my username and password
> SO THAT I receive a session token that authenticates all subsequent requests

### SCENARIO 1: Successful login returns a token

**Scenario ID**: AUTH-STORY-001-S1

:::{admonition} GIVEN
:class: note
* A user with `username="alice"` is registered
* The correct password is supplied
:::

:::{admonition} WHEN
:class: tip
* `POST /auth/login` is called with `{ "username": "alice", "password": "..." }`
:::

:::{admonition} THEN
:class: important
* Response is `200 OK` with `{ "token": "<jwt>", "user_id": "...", "username": "alice" }`
* The token encodes `user_id` in its payload
:::

### SCENARIO 2: Wrong password is rejected

**Scenario ID**: AUTH-STORY-001-S2

:::{admonition} GIVEN
:class: note
* A user with `username="alice"` is registered
:::

:::{admonition} WHEN
:class: tip
* `POST /auth/login` is called with an incorrect password
:::

:::{admonition} THEN
:class: important
* Response is `401 Unauthorized`
* No token is issued
:::

### SCENARIO 3: Unknown username is rejected

**Scenario ID**: AUTH-STORY-001-S3

:::{admonition} GIVEN
:class: note
* No user with the given username exists
:::

:::{admonition} WHEN
:class: tip
* `POST /auth/login` is called
:::

:::{admonition} THEN
:class: important
* Response is `401 Unauthorized`
:::

### SCENARIO 4: Protected endpoint rejects missing token

**Scenario ID**: AUTH-STORY-001-S4

:::{admonition} GIVEN
:class: note
* A request is made to any protected endpoint without a Bearer token
:::

:::{admonition} WHEN
:class: tip
* The request is processed
:::

:::{admonition} THEN
:class: important
* Response is `401 Unauthorized`
* The service layer is never called
:::

---

## AUTH-FE-001.1: Login Page

**Architecture Reference**: Section 8.1 - Authentication & Authorisation
**Parent**: AUTH-STORY-001


> AS A visitor
> I WANT a login form
> SO THAT I can authenticate and access the platform

### SCENARIO 1: Successful login redirects to feed

**Scenario ID**: AUTH-FE-001.1-S1

:::{admonition} GIVEN
:class: note
* I am on the login page
:::

:::{admonition} WHEN
:class: tip
* I enter valid credentials and submit
:::

:::{admonition} THEN
:class: important
* The token is stored (localStorage or cookie)
* I am redirected to the home feed
:::

### SCENARIO 2: Failed login shows error message

**Scenario ID**: AUTH-FE-001.1-S2

:::{admonition} GIVEN
:class: note
* I enter incorrect credentials
:::

:::{admonition} WHEN
:class: tip
* I submit the form
:::

:::{admonition} THEN
:class: important
* An inline error "Invalid username or password" is shown
* I remain on the login page
:::

### SCENARIO 3: Unauthenticated user is redirected to login

**Scenario ID**: AUTH-FE-001.1-S3

:::{admonition} GIVEN
:class: note
* I am not logged in
:::

:::{admonition} WHEN
:class: tip
* I navigate to any protected page (feed, profile, DMs)
:::

:::{admonition} THEN
:class: important
* I am redirected to `/login`
:::

---

## AUTH-BE-001.1: Login Endpoint

**Architecture Reference**: Section 8.1 - Authentication & Authorisation
**Parent**: AUTH-STORY-001


> AS A developer
> I WANT a `POST /auth/login` endpoint
> SO THAT clients can exchange credentials for a token

### SCENARIO 1: Valid credentials return a signed token

**Scenario ID**: AUTH-BE-001.1-S1

:::{admonition} GIVEN
:class: note
* `username` and `password` match a stored user record
:::

:::{admonition} WHEN
:class: tip
* `POST /auth/login` is called
:::

:::{admonition} THEN
:class: important
* A JWT is signed with a server secret
* The JWT payload contains `{ "sub": user_id, "username": username }`
* Response is `200 OK` with the token
:::

### SCENARIO 2: Invalid credentials return 401

**Scenario ID**: AUTH-BE-001.1-S2

:::{admonition} GIVEN
:class: note
* The password does not match
:::

:::{admonition} WHEN
:class: tip
* `POST /auth/login` is called
:::

:::{admonition} THEN
:class: important
* `ValueError("invalid_credentials")` is raised by the service
* The HTTP layer maps this to `401 Unauthorized`
:::

---

## AUTH-BE-001.2: Token Validation Middleware

**Architecture Reference**: Section 8.1 - Authentication & Authorisation
**Parent**: AUTH-STORY-001


> AS A developer
> I WANT a middleware/dependency that validates the Bearer token on every protected route
> SO THAT `user_id` is reliably injected into service calls

### SCENARIO 1: Valid token injects user_id

**Scenario ID**: AUTH-BE-001.2-S1

:::{admonition} GIVEN
:class: note
* A valid JWT is present in the `Authorization: Bearer` header
:::

:::{admonition} WHEN
:class: tip
* A protected endpoint is called
:::

:::{admonition} THEN
:class: important
* The token is decoded and `user_id` is extracted
* The service is called with the correct `user_id`
:::

### SCENARIO 2: Expired or tampered token is rejected

**Scenario ID**: AUTH-BE-001.2-S2

:::{admonition} GIVEN
:class: note
* The JWT signature is invalid or the token is expired
:::

:::{admonition} WHEN
:class: tip
* A protected endpoint is called
:::

:::{admonition} THEN
:class: important
* Response is `401 Unauthorized`
* The service layer is never called
:::

---

## AUTH-INFRA-001.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View
**Parent**: AUTH-STORY-001


> AS A developer
> I WANT the Docker image to build and the `api` container to start
> SO THAT the login endpoint is reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: AUTH-INFRA-001.1-S1

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

## AUTH-INFRA-001.2: Users Table Stores Hashed Passwords

**Architecture Reference**: Section 4.3 - Technology Mapping; Section 8.1 - Authentication
**Parent**: AUTH-STORY-001


> AS A developer
> I WANT the `users` table to include a `password_hash` column
> SO THAT credentials can be verified at login without storing plaintext passwords

### SCENARIO 1: Password hash is stored on registration

**Scenario ID**: AUTH-INFRA-001.2-S1

:::{admonition} GIVEN
:class: note
* The `users` table has a `password_hash` column
:::

:::{admonition} WHEN
:class: tip
* A user registers with a password
:::

:::{admonition} THEN
:class: important
* The stored value is a bcrypt hash, not the plaintext password
:::

---

## AUTH-INFRA-001.3: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: AUTH-STORY-001


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT auth behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: AUTH-INFRA-001.3-S1

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
* All auth tests pass
* Exit code is 0
:::
