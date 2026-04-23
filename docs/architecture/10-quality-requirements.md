# Chapter 10: Quality Requirements

## 10.1 Quality Scenarios

| ID   | Quality Attribute | Scenario                                                                 | Measure / Target                        |
|------|-------------------|--------------------------------------------------------------------------|-----------------------------------------|
| Q-01 | Performance       | User opens their feed                                                    | p95 response < 200 ms                   |
| Q-02 | Performance       | User publishes a post                                                    | p95 response < 300 ms (excludes fan-out)|
| Q-03 | Reliability       | Notification Service crashes                                             | Post and feed reads continue unaffected |
| Q-04 | Reliability       | Redis restarts (feed cache lost)                                         | Feed falls back to SQL; no data loss    |
| Q-05 | Security          | Attacker calls GET /feed with another user's token                       | Returns only the authenticated user's feed |
| Q-06 | Security          | Attacker calls GET /messages for a conversation they are not part of     | 403 Forbidden                           |
| Q-07 | Maintainability   | Developer adds a new notification type                                   | Change confined to Notification Service only |
| Q-08 | Scalability       | Traffic doubles                                                          | Scale `api` and `worker` containers horizontally without schema changes |
