# ADR-001: Selection of Qdrant as Primary Vector Database

## Context
The customer support system requires low-latency, scalable semantic search over unstructured policy and FAQ documents to support retrieval-augmented generation (RAG).

## Decision
We selected **Qdrant** as our vector search engine over alternatives such as Pinecone, ChromaDB, and Weaviate.

## Rationale
1. **Performance:** Implemented in Rust, Qdrant provides industry-leading nearest neighbor search throughput and low memory footprint using HNSW indexes.
2. **Payload Filtering:** Qdrant supports complex metadata filtering (e.g., category, department) directly alongside vector distance metrics in a single query stage.
3. **Self-Hosting & Portability:** Can be run locally via Docker with persistent disk storage, avoiding cloud lock-in and high recurring API costs.
4. **Developer Experience:** Clean Python SDK (`qdrant-client`) supporting both remote server connections and in-memory execution for testing.

## Consequences
* **Positive:** High queries-per-second (QPS), predictable costs, and full data sovereignty.
* **Negative:** Requires managing a Docker container compared to fully-managed SaaS vector databases like Pinecone.
