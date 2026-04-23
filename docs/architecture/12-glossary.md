# Chapter 12: Glossary

| Term                  | Definition                                                                                   |
|-----------------------|----------------------------------------------------------------------------------------------|
| Post                  | A short public message published by a user                                                   |
| Feed                  | An ordered list of posts from users that the authenticated user follows                      |
| Follow                | A directed relationship: user A follows user B means A sees B's posts in their feed         |
| @mention              | A `@username` token in a post text that triggers a notification to the named user           |
| Permalink             | A stable public URL pointing to a single post (e.g. `/posts/{post_id}`)                     |
| Direct Message (DM)   | A private message between two users, not visible in any public feed                         |
| Fan-out on Write      | Strategy where a new post is immediately pushed into each follower's feed cache at write time |
| Fan-out on Read       | Strategy where a user's feed is computed at query time by joining posts with the follow graph |
| Redis Streams         | A Redis data structure providing an append-only log with consumer group semantics            |
| Consumer Group        | A Redis Streams feature allowing multiple consumers to share processing of a stream          |
| Dead-Letter Queue (DLQ) | A stream where events are moved after repeated processing failures                         |
| correlation_id        | A UUID attached to every request and propagated through all log entries for traceability     |
| C4 Model              | A hierarchical diagramming approach: Context → Containers → Components → Code               |
| ADR                   | Architecture Decision Record - a short document capturing a significant architectural choice |
