# ADR-006: Render Free-Tier Optimization, 750-Hour Quota Math & Anti-Sleep Strategy

## 1. Context & Problem Statement
Deploying a production-style agentic AI system on zero-cost infrastructure introduces three primary operational constraints on Render's Free Web Service tier:
1. **Inactivity Sleep (Cold Starts):** Render automatically suspends (spins down) free web services after **15 minutes of zero inbound HTTP traffic**. When a user arrives, spin-up latency (cold start) takes 30–60 seconds, severely degrading conversational UX.
2. **750 Instance Hours per Month Quota:** Render allocates exactly 750 free compute hours per calendar month shared across all free services under an account.
3. **Anti-Bot & Fixed-IP Cron Detection:** Naive third-party pingers sending requests from a single fixed IP address every few minutes with default HTTP headers (e.g., standard `curl/7.x`) can trigger Cloudflare / Render WAF rate-limiting, blocking the keep-alive signal.

---

## 2. The 750-Hour Math Breakdown

| Metric | Calculation | Impact |
| :--- | :--- | :--- |
| **Hours in a 30-Day Month** | $30 \times 24 = 720\text{ hours}$ | 30 hours remaining buffer |
| **Hours in a 31-Day Month** | $31 \times 24 = 744\text{ hours}$ | 6 hours remaining buffer |
| **Render Monthly Free Quota**| **750 hours** | Hard account-wide monthly ceiling |
| **Deployment Overlap Cost** | ~0.2 hours per build | Rebuilds run old & new containers concurrently |

### What Happens When 750 Hours Expire?
* If CI/CD rebuilds or multiple services push usage beyond 750 hours, Render immediately puts the service into **Suspended (503 Service Unavailable)** state.
* **Automatic Recovery:** On the **1st day of the next calendar month at 00:00 UTC**, the quota resets to 750 hours automatically, and the service re-activates with zero manual intervention.
* **Downtime Duration:** If exceeded due to rebuilds, downtime typically lasts between **12 to 36 hours** at the very end of the month.

---

## 3. Decisions & Bypasses

### 3.1 Distributed Multi-IP Keep-Alive (GitHub Actions Workflow)
* **Architecture:** Implemented `.github/workflows/keep-alive.yml` triggering every 14 minutes.
* **Anti-Bot Bypass:** Runs on GitHub's rotating Azure runner IP pools worldwide, preventing IP-based rate limiting or blacklisting.
* **Jitter & Real Headers:** Injects random delay jitter (0–30s) and authentic browser `User-Agent` headers.

### 3.2 Dedicated Ultra-Lightweight `/api/ping` Endpoint
* Standard `/api/health` queries Redis and Qdrant connections. Pinging it every 14 minutes wastes compute and database pools.
* `/api/ping` executes in memory in $<1\text{ ms}$, ensuring Render's activity timer resets while consuming negligible CPU and memory.

### 3.3 Decoupled Persistence (NeonDB Serverless + Qdrant Cloud)
* By hosting PostgreSQL on NeonDB and Vector Store on Qdrant Cloud, **Render only handles stateless API compute**.
* NeonDB serverless compute has its own free tier (0.5 GiB RAM, 100 active hours) and auto-pauses in 5 minutes, completely isolated from Render's 750 hours.

### 3.4 16-Hour Schedule Strategy (Zero-Downtime Guarantee)
* For guaranteed 0-downtime across all 31 days including rebuilds, the cron can be configured to keep the app awake during business/waking hours (e.g., 08:00 AM – 12:00 AM = 16 hours/day).
* $16\text{ hours/day} \times 31\text{ days} = 496\text{ hours/month}$, leaving a massive **254-hour safety margin**.
