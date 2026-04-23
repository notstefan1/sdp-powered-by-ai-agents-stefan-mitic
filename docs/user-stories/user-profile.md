# USER-STORY-003: View User Profile

**Architecture Reference**: Section 5.1 - User Service; Section 5.2 - Post Repository
**Priority**: Core (foundational for follow/unfollow via the profile surface)


> AS A user
> I WANT to view another user's profile and their posts
> SO THAT I can decide whether to follow them

### SCENARIO 1: Profile page shows user info and posts

**Scenario ID**: USER-STORY-003-S1

:::{admonition} GIVEN
:class: note
* User `@alice` exists and has published 3 posts
:::

:::{admonition} WHEN
:class: tip
* I navigate to `/@alice`
:::

:::{admonition} THEN
:class: important
* Alice's username, display name, and follower/following counts are shown
* Her 3 posts are listed in reverse chronological order
:::

### SCENARIO 2: Profile page shows follow/unfollow button

**Scenario ID**: USER-STORY-003-S2

:::{admonition} GIVEN
:class: note
* I am authenticated and viewing `@alice`'s profile
:::

:::{admonition} WHEN
:class: tip
* The page loads
:::

:::{admonition} THEN
:class: important
* A "Follow" button is shown if I don't follow her
* An "Unfollow" button is shown if I do follow her
:::

### SCENARIO 3: Unknown username returns 404

**Scenario ID**: USER-STORY-003-S3

:::{admonition} GIVEN
:class: note
* No user with the given username exists
:::

:::{admonition} WHEN
:class: tip
* I navigate to `/@nobody`
:::

:::{admonition} THEN
:class: important
* A "User not found" message is displayed
:::

---

## USER-FE-003.1: Profile Page Component

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-003


> AS A user
> I WANT a profile page at `/@{username}`
> SO THAT I can see a user's info and posts

### SCENARIO 1: Profile renders user info and post list

**Scenario ID**: USER-FE-003.1-S1

:::{admonition} GIVEN
:class: note
* I navigate to `/@alice`
:::

:::{admonition} WHEN
:class: tip
* The page loads
:::

:::{admonition} THEN
:class: important
* Username, display name, follower count, and following count are displayed
* Posts are listed newest-first
:::

### SCENARIO 2: Follow button state reflects current relationship

**Scenario ID**: USER-FE-003.1-S2

:::{admonition} GIVEN
:class: note
* I follow `@alice`
:::

:::{admonition} WHEN
:class: tip
* I view her profile
:::

:::{admonition} THEN
:class: important
* The button reads "Unfollow"
* Clicking it calls `DELETE /users/{user_id}/follow` and updates to "Follow"
:::

---

## USER-BE-003.1: Get User by Username

**Architecture Reference**: Section 5.1 - User Service
**Parent**: USER-STORY-003


> AS A developer
> I WANT a `get_by_username(username)` method on `UserService`
> SO THAT profile pages can resolve a username to a full user record

### SCENARIO 1: Existing user is returned

**Scenario ID**: USER-BE-003.1-S1

:::{admonition} GIVEN
:class: note
* A user with `username="alice"` is registered
:::

:::{admonition} WHEN
:class: tip
* `get_by_username("alice")` is called
:::

:::{admonition} THEN
:class: important
* The user record is returned with `user_id`, `username`, `display_name`
:::

### SCENARIO 2: Unknown username raises error

**Scenario ID**: USER-BE-003.1-S2

:::{admonition} GIVEN
:class: note
* No user with the given username exists
:::

:::{admonition} WHEN
:class: tip
* `get_by_username("nobody")` is called
:::

:::{admonition} THEN
:class: important
* `ValueError("user_not_found")` is raised
:::

---

## USER-BE-003.2: Get Posts by Author

**Architecture Reference**: Section 5.2 - Post Repository
**Parent**: USER-STORY-003


> AS A developer
> I WANT a `get_by_author(author_id)` method on `PostRepository`
> SO THAT a user's profile page can list their posts

### SCENARIO 1: Posts returned in reverse chronological order

**Scenario ID**: USER-BE-003.2-S1

:::{admonition} GIVEN
:class: note
* `author_id="u-alice"` has published 3 posts
:::

:::{admonition} WHEN
:class: tip
* `get_by_author("u-alice")` is called
:::

:::{admonition} THEN
:class: important
* All 3 posts are returned, newest first
:::

### SCENARIO 2: Author with no posts returns empty list

**Scenario ID**: USER-BE-003.2-S2

:::{admonition} GIVEN
:class: note
* `author_id="u-new"` has published no posts
:::

:::{admonition} WHEN
:class: tip
* `get_by_author("u-new")` is called
:::

:::{admonition} THEN
:class: important
* An empty list is returned
:::

---

## USER-BE-003.3: Get Follower and Following Counts

**Architecture Reference**: Section 5.1 - User Service (social graph)
**Parent**: USER-STORY-003


> AS A developer
> I WANT `follower_count(user_id)` and `following_count(user_id)` on `UserService`
> SO THAT profile pages can display social graph stats

### SCENARIO 1: Counts reflect current follow relationships

**Scenario ID**: USER-BE-003.3-S1

:::{admonition} GIVEN
:class: note
* `u-alice` has 2 followers and follows 1 user
:::

:::{admonition} WHEN
:class: tip
* `follower_count("u-alice")` and `following_count("u-alice")` are called
:::

:::{admonition} THEN
:class: important
* `follower_count` returns `2`
* `following_count` returns `1`
:::

---

## USER-INFRA-003.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View
**Parent**: USER-STORY-003


> AS A developer
> I WANT the Docker image to build and the `api` container to start
> SO THAT profile endpoints are reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: USER-INFRA-003.1-S1

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

## USER-INFRA-003.2: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: USER-STORY-003


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT profile behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: USER-INFRA-003.2-S1

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
* All profile tests pass
* Exit code is 0
:::
