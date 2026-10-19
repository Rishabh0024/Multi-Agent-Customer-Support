# 🤖 Multi-Agent Customer Support Assistant

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.3-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-DC2626.svg)](https://qdrant.tech/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Cache-Redis_7-DC382D.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, placement-ready **Multi-Agent Customer Support Assistant** designed to autonomously resolve complex customer queries, retrieve grounded policy answers via semantic vector search, detect frustration in real time, and automatically escalate critical issues to human desks.

[Live](https://multi-agent-customer-support-three.vercel.app/)

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User([Customer]) <-->|React 18 + TS UI| Frontend[React + Vite + Tailwind]
    Frontend <-->|REST API| Backend[FastAPI Backend]

    subgraph Storage
        Backend <-->|Sliding Window Memory| Redis[(Redis 7)]
        Backend <-->|Tickets, Sessions & Logs| Postgres[(PostgreSQL 16)]
    end

    subgraph Multi-Agent LangGraph StateGraph
        Backend --> Coord[1. Coordinator Agent]
        Coord --> Sent[2. Sentiment & Emotion Agent]
        Sent -->|Explicit Escalation| Esc[4. Escalation Agent]
        Sent -->|General / Product Query| RAG[3. RAG Retrieval Agent]
        RAG -->|Score <= Threshold| Esc
        RAG -->|Normal Answer| Resp[5. Response Formatter Agent]
        Esc --> Resp
    end

    RAG <-->|Cosine ANN Search| Qdrant[(Qdrant Vector DB)]
    Resp -->|Formatted Response + Citations| Backend
```

---

## 🚀 Key Features

* **Decoupled Multi-Agent Graph:** Uses LangGraph to orchestrate 5 specialized agents with state tracking and trajectory visualization.
* **Vectorized Knowledge Base (RAG):** Stores return policies, warranty terms, shipping guidelines, and FAQs in **Qdrant** with 1536-dim embeddings.
* **Real-time Frustration & Sentiment Escalation:** Continuously scores customer emotional valence; automatically creates support tickets in **PostgreSQL** when frustration thresholds are breached.
* **Human Support Desk Dashboard:** Live operations dashboard built with **React Query** polling every 10s to inspect tickets, update statuses, and log agent notes.
* **Interactive Qdrant Playground:** Test semantic vector similarity scoring in real time directly from the Knowledge Base UI.
* **Resilient Graceful Fallbacks:** Built-in in-memory fallbacks for Qdrant, Redis, and SQLite so you can develop and run tests locally even without Docker.

---

## 🛠️ Tech Stack Breakdown

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend API** | FastAPI (Python 3.11+) | Async high-performance REST API, automatic OpenAPI / Swagger documentation. |
| **Agent Orchestration** | LangGraph + LangChain | Stateful multi-agent graph with conditional edge routing and trajectory tracking. |
| **Vector Database** | Qdrant | Fast Rust-based vector search engine using HNSW cosine similarity. |
| **Relational Database** | PostgreSQL 16 | ACID storage for users, sessions, conversation histories, and tickets. |
| **Memory & Cache** | Redis 7 | Sub-millisecond sliding window conversational buffer (8 turns). |
| **Frontend Framework** | React 18 + TypeScript + Vite | Modern reactive single-page app with lightning-fast HMR. |
| **State Management** | TanStack React Query v5 | Automated server-state caching, background refetching, and polling. |
| **Styling** | Tailwind CSS | Utility-first styling with responsive layouts and custom scrollbars. |
| **DevOps & Containers**| Docker & Docker Compose | Multi-container production deployment (`backend`, `frontend`, `postgres`, `qdrant`, `redis`). |
| **CI/CD** | GitHub Actions | Automated linting, test execution (Pytest), and build verification. |

---

## ⚡ Quickstart Guide

### Option 1: Run with Docker Compose (Recommended)

1. Make sure **Docker Desktop** is running.
2. In the project root, start all 5 services:
   ```bash
   docker compose up --build
   ```
3. Access the applications:
   * **Frontend UI (Customer Chat & Support Desk):** [http://localhost:5173](http://localhost:5173)
   * **Backend API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Qdrant Vector DB Web Console:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

### Option 2: Run Locally (Without Docker)

The backend includes automatic in-memory fallbacks for Qdrant, Redis, and SQLite, allowing you to run everything directly on your machine without external services running!

#### Step 1: Start Backend (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Backend will be running at [http://localhost:8000](http://localhost:8000)*

#### Step 2: Start Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be running at [http://localhost:5173](http://localhost:5173)*

---

## 🧪 Running Automated Tests

Run the complete integration and unit test suite with Pytest:

```bash
cd backend
pytest ../tests -v
```

Tests verify:
* Coordinator agent intent routing (greetings, RAG queries, complaints)
* Sentiment agent thresholding and escalation detection
* Qdrant vector index upsert and cosine similarity search
* End-to-end FastAPI chat, ticket creation, and knowledge endpoints

---

## 📂 Project Directory Structure

```text
Multi-Agent-Customer-Support/
├── backend/
│   ├── app/
│   │   ├── agents/          # Coordinator, Sentiment, RAG, Escalation, Response, Graph
│   │   ├── api/             # FastAPI routes (/chat, /tickets, /knowledge, /health)
│   │   ├── core/            # Config, logging, settings
│   │   ├── db/              # SQLAlchemy models (PostgreSQL) and sessionmaker
│   │   ├── memory/          # Redis sliding window session manager
│   │   ├── schemas/         # Pydantic v2 validation models
│   │   ├── services/        # Default enterprise knowledge base seeder
│   │   ├── vector_store/    # Qdrant client & embedding generator
│   │   └── main.py          # Application entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # ChatWindow, ChatInput, SentimentBadge, TicketList, KnowledgeManager
│   │   ├── pages/           # ChatPage, TicketsPage, KnowledgePage
│   │   ├── services/        # Axios API client & TanStack React Query hooks
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # React Router setup
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── tests/                   # Pytest test suite (agents, RAG, API, database)
├── docs/
│   ├── system-design.md     # Detailed architecture & Mermaid workflows
│   ├── database-design.md   # PostgreSQL schema & Qdrant vector specs
│   ├── resume-bullets.md    # Placement resume bullet points
│   ├── interview-qa.md      # 10+ technical interview questions & answers
│   └── ADR/                 # 5 Architecture Decision Records (Qdrant, LangGraph, etc.)
├── .github/workflows/
│   └── ci.yml               # Automated CI/CD pipeline
├── docker-compose.yml       # Production multi-container orchestration
└── README.md
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
