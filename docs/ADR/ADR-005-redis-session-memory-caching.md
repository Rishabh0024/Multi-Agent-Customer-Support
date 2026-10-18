# ADR-005: Redis for Session Conversation Sliding Window Memory

## Context
Conversational AI agents must maintain multi-turn context (what the customer asked earlier in the session) without exceeding LLM context windows or incurring runaway token costs.

## Decision
We implemented a **sliding window conversational memory buffer** using **Redis 7**.

## Rationale
1. **Low Latency:** In-memory key-value lookups complete in $<1\text{ ms}$, ensuring no perceptible overhead on user chat latency.
2. **Sliding Window Token Bounds:** Each session only maintains the last 8 turns (16 messages). Older messages are pruned from the active prompt context while remaining permanently archived in PostgreSQL.
3. **Automatic TTL Expiration:** Keys automatically expire after 48 hours of inactivity, preventing memory leaks in Redis.

## Consequences
* **Positive:** Sub-millisecond context retrieval, predictable LLM API costs, and decoupling of short-term conversational cache from permanent transactional records.
* **Negative:** Additional infrastructure component. We implemented an in-memory dictionary fallback when running tests or development without a local Redis daemon.
