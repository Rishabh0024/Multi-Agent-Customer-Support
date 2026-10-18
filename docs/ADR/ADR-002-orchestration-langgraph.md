# ADR-002: Multi-Agent Orchestration Using LangGraph

## Context
Multi-agent systems require explicit control over state transitions, conditional branching (e.g., routing to escalation vs RAG retrieval), and cyclical error recovery loops.

## Decision
We adopted **LangGraph** (built on top of LangChain) as the primary orchestration framework.

## Rationale
1. **Explicit Graph Topologies:** Unlike traditional linear chains, LangGraph allows modeling workflows as stateful graphs (`StateGraph`) with typed node functions and conditional edges.
2. **Deterministic Debugging:** The state dictionary is updated at each node, making it straightforward to inspect the `agent_trajectory`, intermediate confidence scores, and emotional classifications.
3. **Resilience:** If a specific sub-agent fails, the graph can catch the error and route to a fallback persona agent without terminating the entire conversation.

## Consequences
* **Positive:** High architectural clarity, testability, and seamless extensibility for adding new agents (e.g., billing tool agent).
* **Negative:** Slightly steeper learning curve than simple sequential chains.
