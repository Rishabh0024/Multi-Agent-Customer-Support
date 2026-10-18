# ADR-004: Frontend Architecture: React, TypeScript, Vite, and TanStack Query

## Context
The customer support system needs both a polished, low-latency customer chat widget and an operations dashboard for support agents to manage escalated tickets in real time.

## Decision
We implemented the frontend using **React 18 + TypeScript + Vite + Tailwind CSS + Axios + TanStack React Query + React Router v6**.

## Rationale
1. **Developer Experience & Performance:** Vite delivers sub-second Hot Module Replacement (HMR) and optimized Rollup production bundles.
2. **Server State Synchronization:** TanStack React Query eliminates manual boilerplate for loading spinners, caching, auto-polling (10-second polling for escalated tickets), and cache invalidation.
3. **Type Safety:** TypeScript ensures end-to-end type safety between FastAPI Pydantic response models and frontend view states.
4. **Client-Side Routing:** React Router v6 cleanly separates the Customer Chat view (`/`), Support Desk Dashboard (`/tickets`), and Knowledge Base Explorer (`/knowledge`).

## Consequences
* **Positive:** Modern reactive UI with zero layout shifts, automated polling, and clean architecture.
* **Negative:** Requires a Node.js build step before container deployment.
