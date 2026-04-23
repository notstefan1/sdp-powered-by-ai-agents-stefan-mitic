# NOTIF-STORY-003: Mark Notification as Read

**Architecture Reference**: Section 5.1 - Notification Service; Section 8.4 - Data Privacy
**Priority**: Supporting (essential for accurate unread-state UX)


> AS A user
> I WANT to mark notifications as read
> SO THAT the unread badge clears after I have seen them

### SCENARIO 1: Notification is marked as read

**Scenario ID**: NOTIF-STORY-003-S1

:::{admonition} GIVEN
:class: note
* I have 1 unread notification
:::

:::{admonition} WHEN
:class: tip
* I open the notification list
:::

:::{admonition} THEN
:class: important
* The notification is marked as read
* The unread badge disappears
:::

### SCENARIO 2: Already-read notification is not duplicated

**Scenario ID**: NOTIF-STORY-003-S2

:::{admonition} GIVEN
:class: note
* A notification is already marked as read
:::

:::{admonition} WHEN
:class: tip
* `mark_read` is called again for the same notification
:::

:::{admonition} THEN
:class: important
* No error is raised
* The notification remains in the read state
:::

---

## NOTIF-FE-003.1: Notification Bell Clears on Open

**Architecture Reference**: Section 5.1 - Notification Service
**Parent**: NOTIF-STORY-003


> AS A user
> I WANT the unread badge to clear when I open the notification list
> SO THAT I know I have seen all pending notifications

### SCENARIO 1: Badge clears after opening notification panel

**Scenario ID**: NOTIF-FE-003.1-S1

:::{admonition} GIVEN
:class: note
* The bell shows a badge with count 2
:::

:::{admonition} WHEN
:class: tip
* I click the bell icon
:::

:::{admonition} THEN
:class: important
* Both notifications are marked as read
* The badge disappears
:::

---

## NOTIF-BE-003.1: Mark Notification as Read

**Architecture Reference**: Section 5.1 - Notification Service
**Parent**: NOTIF-STORY-003


> AS A developer
> I WANT a `mark_read(notification_id)` method on `NotificationService`
> SO THAT clients can clear the unread state

### SCENARIO 1: Notification read flag is set to True

**Scenario ID**: NOTIF-BE-003.1-S1

:::{admonition} GIVEN
:class: note
* A notification with `read=False` exists
:::

:::{admonition} WHEN
:class: tip
* `mark_read(notification_id)` is called
:::

:::{admonition} THEN
:class: important
* The notification's `read` field is `True`
* It no longer appears in `get_unread(recipient_id)`
:::

### SCENARIO 2: Unknown notification_id raises error

**Scenario ID**: NOTIF-BE-003.1-S2

:::{admonition} GIVEN
:class: note
* No notification with the given ID exists
:::

:::{admonition} WHEN
:class: tip
* `mark_read(notification_id)` is called
:::

:::{admonition} THEN
:class: important
* `ValueError("notification_not_found")` is raised
:::

---

## NOTIF-INFRA-003.1: Docker Image Builds and Container Starts

**Architecture Reference**: Section 7 - Deployment View
**Parent**: NOTIF-STORY-003


> AS A developer
> I WANT the Docker image to build and the `api` container to start
> SO THAT the mark-read endpoint is reachable locally

### SCENARIO 1: Image builds without errors

**Scenario ID**: NOTIF-INFRA-003.1-S1

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

## NOTIF-INFRA-003.2: pytest Suite Runs Inside Docker

**Architecture Reference**: Section 7 - Deployment View
**Parent**: NOTIF-STORY-003


> AS A developer
> I WANT the full pytest suite to execute inside the Docker container
> SO THAT mark-read behaviour is verified in CI

### SCENARIO 1: Tests are discovered and executed

**Scenario ID**: NOTIF-INFRA-003.2-S1

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
* All mark-read tests pass
* Exit code is 0
:::
