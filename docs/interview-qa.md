# Technical Interview Guide: Multi-Agent Customer Support Assistant

### 1. Why use a Multi-Agent architecture instead of a single prompt with RAG?
**Answer:** A monolithic prompt handling intent classification, emotion scoring, semantic retrieval, ticket escalation, and brand persona quickly suffers from prompt clutter, conflicting instructions, and token bloat. By separating responsibilities into modular agents using **LangGraph**, each agent executes a focused task with strict input/output contracts. For example, if a user demands a manager, the Coordinator and Sentiment agents can bypass the RAG retrieval step entirely, saving vector compute and LLM latency.

### 2. How does LangGraph improve upon traditional LangChain Agent chains?
**Answer:** Traditional chains are linear (DAGs) and lack cyclic loops, state persistence, and explicit branching logic. LangGraph models the multi-agent workflow as a stateful graph (`StateGraph`), enabling conditional routing based on state variables (such as `escalation_required` and `intent`). This makes debugging deterministic, allows state inspection after every node transition, and supports human-in-the-loop interventions.

### 3. Why choose Qdrant over Pinecone or ChromaDB?
**Answer:** 
* **Qdrant:** Built in Rust, offering sub-millisecond approximate nearest neighbor (ANN) search via HNSW graphs, native payload filtering (hybrid search), and self-hosting capability via Docker without vendor lock-in.
* **Pinecone:** Closed-source, cloud-only, and carries recurring subscription costs.
* **ChromaDB:** Great for local prototyping, but less performant at production scale compared to Rust-based Qdrant.

### 4. Why use PostgreSQL alongside Qdrant?
**Answer:** Vector stores are optimized for high-dimensional similarity queries, but are not designed for ACID-compliant transactional workflows, complex relational joins, foreign keys, or audit logs. PostgreSQL stores normalized customer profiles, chat session histories, and support ticket states (`open`, `escalated`, `resolved`), ensuring data integrity.

### 5. How does Redis handle conversational memory without blowing token limits?
**Answer:** Instead of re-sending the entire conversation history to the LLM on every turn, we implement a **sliding window buffer** of the last $N$ turns (e.g. 8 turns = 16 messages). Redis caches these serialized messages as JSON with a 48-hour TTL, providing sub-millisecond access and keeping prompt token size strictly bounded.

### 6. What happens if a user is angry and demands immediate escalation?
**Answer:** The `CoordinatorAgent` identifies the `escalation_request` or `complaint` intent, and the `SentimentAgent` detects negative keywords or low sentiment scores ($\le 0.35$). The LangGraph conditional edge routes directly to the `EscalationAgent`, generating a unique ticket (`TICK-XXXXX`) in PostgreSQL with `urgent` priority. The `ResponseAgent` formats a empathetic response assuring human intervention.

### 7. How do you prevent hallucinations in the RAG pipeline?
**Answer:** 
1. We set a cosine similarity score threshold ($0.25$) on Qdrant searches.
2. The RAG system prompt explicitly enforces strict grounding: *"Answer only using the provided context. If the documentation does not cover the answer, state that you do not know and offer human assistance."*
3. The response includes citations referencing the source document title and category.

### 8. How did you design the frontend and why React + Vite + React Query?
**Answer:** React with Vite provides lightning-fast HMR and bundle optimization. TanStack React Query handles server-state synchronization (caching, automated polling of escalated tickets every 10 seconds, background re-fetching, and optimistic mutations). Tailwind CSS provides a clean, responsive interface without heavyweight UI component libraries.

### 9. What fallback mechanisms exist if external services fail?
**Answer:** 
* If OpenAI API is down or key is missing, the backend runs on deterministic rule-based heuristics and local mock embeddings.
* If PostgreSQL is unreachable during local testing, an automatic SQLite fallback (`customersupport_local.db`) engages.
* If Redis is down, an in-memory dictionary cache fallback ensures the app never crashes.
* If Qdrant server is down, an in-memory Qdrant client (`:memory:`) takes over.

### 10. How would you scale this system to 100,000 daily active users?
**Answer:**
1. **Horizontal Scaling:** Deploy FastAPI backend replicas behind an AWS Application Load Balancer (ALB) or Kubernetes Ingress.
2. **Qdrant Clustering:** Deploy Qdrant in distributed cluster mode with sharding across multiple nodes.
3. **Redis Sentinel / Cluster:** High availability Redis cluster for distributed session state.
4. **Read Replicas:** PostgreSQL read replicas to offload ticket dashboard queries from transactional chat writes.
