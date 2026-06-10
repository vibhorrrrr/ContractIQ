# ContractIQ 

**AI-Powered Contract Intelligence Platform**

ContractIQ transforms static legal documents into actionable business intelligence. By leveraging advanced LLMs, it automatically extracts key clauses, identifies legal risks, generates risk scores, and produces executive summaries—turning days of manual legal review into seconds of automated insight. Every finding is directly traceable to the source text.

---

## Features

- **Automated Clause Extraction**: Identifies and categorizes key clauses (Liability, Indemnification, Termination, Data Privacy, etc.).
- **Intelligent Risk Scoring**: Flags non-standard language and assigns severity levels (Low, Medium, High, Critical) with a 0-10 overall contract score.
- **Executive Summaries**: Instantly generates human-readable summaries of the contract's risk profile.
- **Source Tracing**: Every AI finding highlights the exact verbatim paragraph from the uploaded document.
- **Multi-Tenant Dashboard**: Secure, company-isolated environment with analytics on total contracts and risk distribution.
- **Format Support**: Processes both PDF and DOCX files.

## Technology Stack

- **Frontend**: Next.js 15 (App Router), React, Tailwind CSS, Clerk (Auth)
- **Backend**: FastAPI (Python), SQLAlchemy (Async), Pydantic
- **Database / Queue**: PostgreSQL (with pgvector), Redis
- **AI / Parsing**: OpenAI (GPT-4o primary) / Anthropic (Claude fallback), pdfplumber, PyMuPDF, python-docx

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL 15+ (with `pgvector` extension)
- Redis 7+

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Setup database (Ensure PostgreSQL is running)
psql -U postgres -c "CREATE DATABASE contractiq;"
psql -U postgres -d contractiq -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000

# Start background worker (In a separate terminal window)
python -m app.workers.analysis_worker
```

### 2. Frontend Setup

```bash
cd frontend
npm install

# Start the Next.js development server
npm run dev
```
The frontend will be available at `http://localhost:3000`.

### 3. Environment Variables

You need to configure environment variables for both the frontend and backend.
- Copy `backend/.env` and fill in your `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.
- Copy `frontend/.env.local` and add your Clerk API keys. 

*(See `CONTRACTIQ_MASTER_CONTEXT.md` for a full configuration reference).*

## Verification

Check if the backend services are running correctly:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","db":"ok","redis":"ok"}
```
