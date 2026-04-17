# Domain-Driven Design: Ubiquitous Language

## Core Domain: Social Networking Platform

### Bounded Contexts

#### 1. User Context
- **User** — A registered account holder who can publish posts and interact with others
- **Profile** — Public information associated with a User (username, bio, avatar)
- **Authentication** — Process of verifying User identity
- **Registration** — Process of creating a new User account

#### 2. Social Graph Context
- **Follow** — A unidirectional relationship where one User subscribes to another's content
- **Follower** — A User who follows another User
- **Following** — A User being followed by another User
- **Social Graph** — The network of Follow relationships between Users

#### 3. Post Publishing Context
- **Post** — A short public message (≤280 characters) created by a User
- **Publish** — The act of creating and persisting a Post
- **Mention** — A reference to another User within a Post using `@username` syntax
- **Post ID** — Unique identifier for a Post

#### 4. Feed Context
- **Feed** — A time-ordered collection of Posts from Users a User follows
- **Fan-out** — The process of distributing a Post to all Followers' Feeds
- **Feed Cache** — Redis-based storage for pre-computed Feeds
- **Aggregation** — The process of collecting Posts into a Feed

#### 5. Notification Context
- **Notification** — An alert sent to a User about relevant activity
- **@mention Notification** — A Notification triggered when a User is mentioned in a Post
- **Notification Delivery** — The process of sending a Notification to a User

#### 6. Messaging Context
- **Direct Message (DM)** — A private message sent between two Users
- **Conversation** — A thread of Direct Messages between two Users
- **Message Delivery** — The process of transmitting a Direct Message to the recipient

### Domain Events

- **post.created** — Emitted when a Post is successfully published
- **user.followed** — Emitted when a Follow relationship is established
- **user.unfollowed** — Emitted when a Follow relationship is removed
- **mention.detected** — Emitted when a Mention is found in a Post
- **message.sent** — Emitted when a Direct Message is sent

### Aggregates

- **User Aggregate** — Root: User; Entities: Profile, Authentication credentials
- **Post Aggregate** — Root: Post; Value Objects: Post content, timestamp, mentions
- **Social Graph Aggregate** — Root: User; Entities: Follow relationships
- **Feed Aggregate** — Root: Feed; Entities: Cached Post references
- **Conversation Aggregate** — Root: Conversation; Entities: Direct Messages

### Value Objects

- **Username** — Unique identifier string for a User
- **Post Content** — Text content of a Post (max 280 characters)
- **Timestamp** — Point in time when an event occurred
- **Post ID** — Immutable unique identifier for a Post

### Services

- **Post Service** — Handles Post creation and persistence
- **Feed Service** — Manages Feed aggregation and caching
- **Notification Service** — Delivers Notifications to Users
- **Social Graph Service** — Manages Follow relationships
- **Messaging Service** — Handles Direct Message delivery
