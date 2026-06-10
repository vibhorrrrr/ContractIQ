<div align="center">

# ContractIQ

**AI-Powered Contract Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

Transform contracts from static legal documents into **actionable business intelligence**.

Upload any contract → Get instant risk analysis, clause extraction, and executive summaries — every finding traced to source text.

</div>

---

## Features

| Feature | Description |
|---|---|
| **Clause Extraction** | Automatically identifies and categorizes 10 clause types — Liability, Indemnification, Termination, Renewal, Payment Terms, Data Privacy, Confidentiality, IP, Governing Law, Exclusivity |
| **Risk Scoring** | Weighted risk scoring (0–10) with severity levels: Low, Medium, High, Critical |
| **Executive Summaries** | AI-generated contract risk summaries for quick decision-making |
| **Source Tracing** | Every finding links to the exact verbatim paragraph from the uploaded document |
| **Model Fallback** | Primary: GPT-4o → Fallback: Claude Sonnet if OpenAI fails or rate-limits |
| **Multi-Tenant** | Company-isolated data — every query enforces `company_id` scoping |
| **Async Pipeline** | Background processing via Redis queue — upload returns instantly |

---

## Preview

> **Screenshots & demo video coming soon** — the platform is under active development.
> Star the repo to stay updated!

---

## Architecture

```
┌─────────────────┐         ┌──────────────────┐        ┌────────────┐
│   Next.js 15    │────────▶│   FastAPI         │───────▶│ PostgreSQL │
│   + Clerk Auth  │  REST   │   (async)         │  ORM   │ + pgvector │
└─────────────────┘         └────────┬─────────┘        └────────────┘
                                     │
                              ┌──────┴──────┐
                              │ Redis Queue  │
                              └──────┬──────┘
                                     │
                            ┌────────▼────────┐
                            │ Analysis Worker  │
                            │  ┌────────────┐  │
                            │  │  OpenAI    │  │
                            │  │  Anthropic │  │
                            │  └────────────┘  │
                            └─────────────────┘
```

**Backend follows a strict layered architecture:**
```
API Routes → Services → Repositories → ORM Models
```
No business logic in routes. No raw SQL outside repositories. Fully async.

---

## Project Structure

```
contractiq/
├── backend/
│   ├── app/
│   │   ├── api/v1/            # FastAPI route handlers
│   │   │   ├── contracts.py   # Upload, list, detail, status, delete
│   │   │   ├── dashboard.py   # Aggregate stats
│   │   │   └── health.py      # Health check (no auth)
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy ORM models (6 tables)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── repositories/      # Database access layer
│   │   ├── services/          # Business logic + AI pipeline
│   │   └── workers/           # Background job processor
│   ├── alembic/               # Database migrations
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/            # Sign-in / Sign-up (Clerk)
│   │   ├── (app)/             # Authenticated app shell
│   │   │   ├── dashboard/     # Stats, risk distribution, recent uploads
│   │   │   └── contracts/     # List + upload, [id] detail view
│   │   ├── layout.tsx         # Root layout with Clerk provider
│   │   └── page.tsx           # Landing page
│   ├── lib/                   # API client, utilities
│   └── middleware.ts          # Route protection
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 (App Router), React, Tailwind CSS |
| **Auth** | Clerk (JWT-based, JWKS verification) |
| **Backend** | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| **Database** | PostgreSQL 15+ with pgvector extension |
| **Queue** | Redis 7+ (job queue for async processing) |
| **AI** | OpenAI GPT-4o (primary), Anthropic Claude (fallback) |
| **Parsing** | pdfplumber → PyMuPDF (fallback), python-docx |

---

## Quick Start

### Prerequisites

- **Node.js** 20+ &nbsp;·&nbsp; **Python** 3.12+ &nbsp;·&nbsp; **PostgreSQL** 15+ &nbsp;·&nbsp; **Redis** 7+

### 1. Clone & Configure

```bash
git clone https://github.com/vibhorrrrr/ContractIQ.git
cd ContractIQ

# Create env files from templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Fill in your API keys (OpenAI, Anthropic, Clerk)
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Database setup
psql -U postgres -c "CREATE DATABASE contractiq;"
psql -U postgres -d contractiq -c "CREATE EXTENSION IF NOT EXISTS vector;"
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# Start background worker (separate terminal)
python -m app.workers.analysis_worker
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Verify

```bash
curl http://localhost:8000/health
# → {"status":"ok","db":"ok","redis":"ok"}
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📡 API Endpoints

All endpoints (except health) require `Authorization: Bearer <clerk_jwt>`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check (DB + Redis) |
| `POST` | `/api/v1/contracts/upload` | Upload contract (multipart/form-data) |
| `GET` | `/api/v1/contracts` | List all contracts for company |
| `GET` | `/api/v1/contracts/{id}` | Full contract detail + clauses + risks |
| `GET` | `/api/v1/contracts/{id}/status` | Poll processing status |
| `DELETE` | `/api/v1/contracts/{id}` | Delete contract and all related data |
| `GET` | `/api/v1/dashboard/stats` | Aggregate company dashboard stats |

---

## ⚙️ Environment Variables

<details>
<summary><b>Backend</b> — <code>backend/.env</code></summary>

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL async connection string |
| `REDIS_URL` | Redis connection string |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `CLERK_SECRET_KEY` | Clerk secret key for JWT verification |
| `CLERK_JWT_ISSUER` | Clerk JWT issuer URL |
| `STORAGE_MODE` | `local` (dev) or `s3` (production) |

</details>

<details>
<summary><b>Frontend</b> — <code>frontend/.env.local</code></summary>

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY` | Clerk secret key |
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

</details>

---

## Risk Scoring

```
Per-clause weights:  CRITICAL = 3.0  |  HIGH = 2.0  |  MEDIUM = 1.0  |  LOW = 0.2

Contract score = sum(weights) capped at 10.0

 0.0 – 3.0  →  LOW
 3.1 – 5.0  →  MEDIUM
 5.1 – 7.5  →  HIGH
 7.6 – 10.0 →  CRITICAL
```

---

## Roadmap

- [ ] **Batch Upload** — upload multiple contracts at once
- [ ] **Clause Comparison** — side-by-side diff between contract versions
- [ ] **Export Reports** — PDF/CSV export of risk analysis
- [ ] **Webhook Notifications** — alert on high-risk clause detection
- [ ] **Custom Clause Templates** — define company-specific clause categories
- [ ] **Docker Compose** — one-command local development setup
- [ ] **Role-Based Access Control** — viewer / editor / admin roles

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**If you find ContractIQ useful, consider giving it a ⭐**

</div>
