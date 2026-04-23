# Chapter 11: Risks and Technical Debts

## 11.1 Risks

| ID   | Risk                                      | Likelihood | Impact | Mitigation                                                                 |
|------|-------------------------------------------|------------|--------|----------------------------------------------------------------------------|
| R-01 | Fan-out write amplification (high-follower users) | Low  | High   | Implement hybrid fan-out (skip fan-out above threshold; merge at read time) |
| R-02 | Redis becomes single point of failure     | Medium     | High   | Redis Sentinel or Cluster; SQL fallback for feed reads                     |
| R-03 | Consumer lag causes stale feeds           | Medium     | Medium | Monitor consumer group lag; alert on lag > 10 s                            |
| R-04 | DB boundary violations (services querying each other's tables) | Medium | Medium | Enforce via module linting (e.g. `import-linter`) and code review |

## 11.2 Technical Debts

| ID   | Debt                                                  | Impact                          | Resolution Path                                      |
|------|-------------------------------------------------------|---------------------------------|------------------------------------------------------|
| D-01 | Single PostgreSQL instance                            | Scaling bottleneck at high load | Add read replicas; eventually split per-service DBs  |
| D-02 | No full-text search on posts                          | Poor @mention / hashtag search  | Add PostgreSQL `tsvector` index or Elasticsearch     |
| D-03 | No rate limiting on POST /posts                       | Spam / abuse risk               | Add token-bucket rate limiter in API Gateway         |
| D-04 | Notification delivery is fire-and-forget to push provider | Missed push notifications  | Add delivery receipt tracking and retry logic        |
