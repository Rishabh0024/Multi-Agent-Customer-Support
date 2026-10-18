# ADR-003: Selection of PostgreSQL as Primary Relational Store

## Context
While vector stores handle semantic knowledge retrieval, support operations require ACID-compliant relational storage for user accounts, session tracking, conversation histories, and support ticket management.

## Decision
We chose **PostgreSQL 16** with asynchronous SQLAlchemy (`asyncpg`) as the relational database.

## Rationale
1. **ACID Compliance & Reliability:** Essential for ticket lifecycle management (`open` -> `escalated` -> `resolved`) and financial/order auditing.
2. **Async Driver Ecosystem:** PostgreSQL with `asyncpg` matches FastAPI's non-blocking asynchronous event loop, handling thousands of concurrent connections with minimal CPU overhead.
3. **Relational Modeling:** Clean foreign-key constraints linking Users -> Chat Sessions -> Messages -> Tickets -> Feedback.

## Consequences
* **Positive:** Enterprise-grade reliability, rich indexing, and direct integration with existing analytics tools.
* **Negative:** Requires running a database daemon (PostgreSQL) or Docker container. We mitigated local testing hurdles by implementing an automatic SQLite fallback.
