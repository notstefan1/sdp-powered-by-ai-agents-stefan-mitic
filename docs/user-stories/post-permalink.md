# POST-STORY-002: Share Post Permalink

**Architecture Reference**: Section 5.2 - Post Service Components; Section 5.2 - Post Repository
**Priority**: Supporting


> AS A user
> I WANT to share a direct link to a specific post
> SO THAT others can view it without scrolling through a feed

### SCENARIO 1: Permalink resolves to the correct post

**Scenario ID**: POST-STORY-002-S1

:::{admonition} GIVEN
:class: note
* A post with `post_id` exists
:::

:::{admonition} WHEN
:class: tip
* I navigate to `/posts/{post_id}`
:::

:::{admonition} THEN
:class: important
* The post's text, author, and timestamp are returned
* Response is `200 OK`
:::

### SCENARIO 2: Permalink for non-existent post returns 404

**Scenario ID**: POST-STORY-002-S2

:::{admonition} GIVEN
:class: note
* No post with the given `post_id` exists
:::

:::{admonition} WHEN
:class: tip
* I navigate to `/posts/{post_id}`
:::

:::{admonition} THEN
:class: important
* Response is `404 Not Found`
:::

---

## POST-FE-002.1: Post Permalink Page

**Architecture Reference**: Section 5.2 - Post Router
**Parent**: POST-STORY-002


> AS A user
> I WANT a dedicated page for a single post
> SO THAT I can share it via URL

### SCENARIO 1: Post page renders post content

**Scenario ID**: POST-FE-002.1-S1

:::{admonition} GIVEN
:class: note
* I open `/posts/{post_id}`
:::

:::{admonition} WHEN
:class: tip
* The page loads
:::

:::{admonition} THEN
:class: important
* The post text, author username, and timestamp are displayed
* A "Copy link" button is visible
:::

### SCENARIO 2: 404 page shown for missing post

**Scenario ID**: POST-FE-002.1-S2

:::{admonition} GIVEN
:class: note
* The `post_id` does not exist
:::

:::{admonition} WHEN
:class: tip
* The page loads
:::

:::{admonition} THEN
:class: important
* A "Post not found" message is displayed
:::

---

## POST-BE-002.1: Get Post by ID

**Architecture Reference**: Section 5.2 - Post Repository
**Parent**: POST-STORY-002


> AS A developer
> I WANT a `get(post_id)` method on `PostRepository`
> SO THAT a single post can be retrieved by its ID

### SCENARIO 1: Existing post is returned

**Scenario ID**: POST-BE-002.1-S1

:::{admonition} GIVEN
:class: note
* A post with `post_id` exists in the repository
:::

:::{admonition} WHEN
:class: tip
* `repo.get(post_id)` is called
:::

:::{admonition} THEN
:class: important
* The `Post` object is returned with correct `author_id` and `text`
:::

### SCENARIO 2: Missing post returns None

**Scenario ID**: POST-BE-002.1-S2

:::{admonition} GIVEN
:class: note
* No post with the given `post_id` exists
:::

:::{admonition} WHEN
:class: tip
* `repo.get(post_id)` is called
:::

:::{admonition} THEN
:class: important
* `None` is returned
:::

---

## POST-INFRA-002.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View; Section 7.3 - Container Mapping (`api`)
**Parent**: POST-STORY-002


> AS A developer
> I WANT the Docker image to build and the `api` container to start
> SO THAT the permalink endpoint is reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: POST-INFRA-002.1-S1

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

## POST-INFRA-002.2: Posts Table Supports Lookup by post_id

**Architecture Reference**: Section 5.2 - Post Repository; Section 4.3 - Technology Mapping
**Parent**: POST-STORY-002


> AS A developer
> I WANT the `posts` table to have a primary key on `post_id`
> SO THAT single-post lookups are efficient

### SCENARIO 1: Post row is retrievable by primary key

**Scenario ID**: POST-INFRA-002.2-S1

:::{admonition} GIVEN
:class: note
* The `postgres` container is running
* The `posts` table has `post_id` as primary key
:::

:::{admonition} WHEN
:class: tip
* `SELECT * FROM posts WHERE post_id = ?` is executed
:::

:::{admonition} THEN
:class: important
* The correct row is returned in O(1) via index
:::

---

## POST-INFRA-002.3: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: POST-STORY-002


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT permalink behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: POST-INFRA-002.3-S1

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
* All post permalink tests pass
* Exit code is 0
:::
