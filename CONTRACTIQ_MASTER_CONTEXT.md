# CONTRACTIQ — MASTER PROJECT CONTEXT
# Local Development Edition

---

## COMPANY OVERVIEW

**Company Name:** ContractIQ
**Tagline:** AI-Powered Contract Intelligence Platform
**Mission:** Transform contracts from static legal documents into actionable business intelligence.
**Vision:** Become the Bloomberg Terminal for contract intelligence and enterprise risk analysis.

---

## PROBLEM

Businesses sign thousands of contracts every year:

- Vendor Agreements
- SaaS Contracts
- Supplier Agreements
- NDAs / MSAs
- Procurement Contracts

Reviewing these contracts is expensive, slow, inconsistent, and difficult to scale.
Legal teams become bottlenecks. Business teams wait days for answers.
Critical risks are routinely missed — unlimited liability, auto-renewal traps,
vendor lock-in, poor payment terms, weak indemnification clauses.

---

## PRODUCT

ContractIQ allows users to upload contracts. The platform automatically:

1. Extracts key clauses
2. Identifies legal risks
3. Generates risk scores
4. Benchmarks clauses against industry norms
5. Produces executive summaries
6. Suggests negotiation points
7. Links every finding to the source paragraph

**Important:** The AI does NOT replace lawyers.
The AI acts as a contract intelligence assistant.
Every recommendation must be traceable to source text.

---

## IDEAL CUSTOMER

**Primary:**
- Procurement Teams
- CFOs / Legal Operations
- Mid-market Companies (50–2000 employees)
- PE-backed Companies

**Secondary:**
- Law Firms
- Enterprise Legal Teams

---

## MVP SCOPE

Version 1 supports ONLY:

- PDF Upload
- DOCX Upload
- Contract Parsing
- Clause Extraction
- Risk Analysis
- Executive Summary

Do NOT build:
- Workflow Management
- CLM Features
- Negotiation Tracking
- E-signatures
- CRM Integrations

---

## LOCAL DEVELOPMENT ENVIRONMENT

### Prerequisites — install before starting

```
Node.js       v20+         (https://nodejs.org)
Python        3.12+        (https://python.org)
PostgreSQL    15+          (https://postgresql.org)  — run locally
Redis         7+           (https://redis.io)        — run locally, for job queue
```

### Recommended local tools

```
pgAdmin 4     — PostgreSQL GUI
TablePlus     — alternative DB GUI
Postman       — API testing
```

### Port assignments (local)

```
Next.js frontend     http://localhost:3000
FastAPI backend      http://localhost:8000
PostgreSQL           localhost:5432
Redis                localhost:6379
```

---

## LOCAL DIRECTORY STRUCTURE

```
contractiq/
├── frontend/                  # Next.js 15 app
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/
│   │   │   └── sign-up/
│   │   ├── dashboard/
│   │   ├── contracts/
│   │   │   └── [id]/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── contracts/
│   │   └── dashboard/
│   ├── lib/
│   │   ├── api.ts             # API client (fetch wrappers)
│   │   └── utils.ts
│   ├── .env.local             # Frontend env vars (never commit)
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                   # FastAPI app
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── contracts.py
│   │   │       ├── dashboard.py
│   │   │       └── health.py
│   │   ├── core/
│   │   │   ├── config.py      # Settings via pydantic-settings
│   │   │   ├── database.py    # SQLAlchemy async engine
│   │   │   └── security.py    # Clerk JWT verification
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── contract.py
│   │   │   ├── clause.py
│   │   │   └── risk.py
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   ├── contract.py
│   │   │   ├── clause.py
│   │   │   └── risk.py
│   │   ├── services/          # Business logic layer
│   │   │   ├── contract_service.py
│   │   │   ├── parsing_service.py
│   │   │   ├── ai_service.py
│   │   │   └── storage_service.py
│   │   ├── repositories/      # Database access layer
│   │   │   ├── contract_repo.py
│   │   │   └── clause_repo.py
│   │   └── workers/
│   │       └── analysis_worker.py   # Background job processor
│   ├── alembic/               # DB migrations
│   ├── tests/
│   ├── .env                   # Backend env vars (never commit)
│   ├── requirements.txt
│   └── alembic.ini
│
├── .gitignore
└── README.md
```

---

## ENVIRONMENT VARIABLES

### Frontend — `frontend/.env.local`

```env
# Clerk (auth) — get from clerk.com dashboard
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend — `backend/.env`

```env
# App
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=your-local-secret-key-change-this

# Database — local PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/contractiq
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/contractiq

# Redis — local
REDIS_URL=redis://localhost:6379/0

# AI providers
OPENAI_API_KEY=sk-xxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx

# AI model config
PRIMARY_MODEL=gpt-4o
FALLBACK_MODEL=claude-sonnet-4-5
MAX_TOKENS_PER_CHUNK=6000
CHUNK_OVERLAP=200

# File upload
MAX_FILE_SIZE_MB=25
MAX_PAGES_PER_CONTRACT=150
ALLOWED_EXTENSIONS=pdf,docx
LOCAL_UPLOAD_DIR=./uploads       # local storage instead of S3

# Clerk (JWT verification)
CLERK_SECRET_KEY=sk_test_xxxxxxxxxx
CLERK_JWT_ISSUER=https://your-clerk-instance.clerk.accounts.dev

# Storage mode — "local" for development, "s3" for production
STORAGE_MODE=local
```

**Note on local storage:** In development, files are saved to `backend/uploads/`
instead of AWS S3. The `storage_service.py` reads `STORAGE_MODE` and switches
between local filesystem and S3 automatically. Never commit the `uploads/` folder.

---

## LOCAL DATABASE SETUP

### Step 1 — create the database

```bash
psql -U postgres
CREATE DATABASE contractiq;
CREATE USER contractiq_user WITH PASSWORD 'contractiq_local';
GRANT ALL PRIVILEGES ON DATABASE contractiq TO contractiq_user;
\q
```

### Step 2 — enable pgvector extension

```bash
psql -U postgres -d contractiq
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Step 3 — run migrations

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

### Step 4 — seed benchmark data (optional for MVP)

```bash
python scripts/seed_benchmarks.py
```

---

## DATABASE SCHEMA

### Table: users

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
clerk_id      VARCHAR(255) UNIQUE NOT NULL   -- Clerk user ID
email         VARCHAR(255) UNIQUE NOT NULL
name          VARCHAR(255)
company_id    UUID REFERENCES companies(id)
role          VARCHAR(50) DEFAULT 'member'   -- 'owner' | 'admin' | 'member'
created_at    TIMESTAMP DEFAULT NOW()
```

### Table: companies

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
name          VARCHAR(255) NOT NULL
industry      VARCHAR(100)
created_at    TIMESTAMP DEFAULT NOW()
```

### Table: contracts

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
company_id    UUID NOT NULL REFERENCES companies(id)
uploaded_by   UUID NOT NULL REFERENCES users(id)
filename      VARCHAR(500) NOT NULL
file_path     TEXT NOT NULL              -- local path or S3 key
file_size     INTEGER
page_count    INTEGER
status        VARCHAR(50) DEFAULT 'pending'
              -- 'pending' | 'processing' | 'completed' | 'failed'
risk_score    FLOAT                      -- 0.0 to 10.0
risk_level    VARCHAR(20)                -- 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
summary       TEXT
error_message TEXT                       -- populated if status = 'failed'
upload_date   TIMESTAMP DEFAULT NOW()
completed_at  TIMESTAMP
```

### Table: clauses

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
contract_id   UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE
clause_type   VARCHAR(100) NOT NULL
clause_text   TEXT NOT NULL
risk_level    VARCHAR(20)                -- 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
page_number   INTEGER
position_start INTEGER                  -- character offset in document
position_end  INTEGER
embedding     vector(1536)              -- pgvector for semantic search
created_at    TIMESTAMP DEFAULT NOW()
```

### Table: risks

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
contract_id   UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE
clause_id     UUID REFERENCES clauses(id)
risk_type     VARCHAR(100) NOT NULL
severity      VARCHAR(20) NOT NULL      -- 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
finding       TEXT NOT NULL
explanation   TEXT NOT NULL
recommendation TEXT NOT NULL
source_text   TEXT NOT NULL             -- exact paragraph from contract
confidence    FLOAT                     -- 0.0 to 1.0
created_at    TIMESTAMP DEFAULT NOW()
```

### Table: benchmarks

```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
clause_type   VARCHAR(100) NOT NULL
industry      VARCHAR(100)              -- NULL = applies to all industries
benchmark_text TEXT NOT NULL           -- what a "market standard" clause looks like
risk_indicators TEXT[]                 -- array of red flag phrases
created_at    TIMESTAMP DEFAULT NOW()
```

**Multi-tenancy rule (enforced in every query):**
Every database query on `contracts`, `clauses`, and `risks` MUST include
`WHERE company_id = :company_id`. No contract data is ever returned without
a verified company_id from the authenticated user's JWT. Violations are a
critical security bug.

---

## API ENDPOINTS

Base URL (local): `http://localhost:8000/api/v1`

All endpoints require `Authorization: Bearer <clerk_jwt>` header.

### Contracts

```
POST   /contracts/upload           Upload a contract file
                                   Body: multipart/form-data (file)
                                   Returns: { contract_id, status: "pending" }

GET    /contracts                  List all contracts for the company
                                   Returns: [{ id, filename, status, risk_score, upload_date }]

GET    /contracts/{id}             Get full contract detail
                                   Returns: contract + clauses + risks

GET    /contracts/{id}/status      Poll processing status
                                   Returns: { status, progress_percent, error_message }

DELETE /contracts/{id}             Delete a contract and all related data
```

### Dashboard

```
GET    /dashboard/stats            Aggregate stats for the company
                                   Returns: { total_contracts, risk_distribution,
                                             recent_uploads, avg_risk_score }
```

### Health

```
GET    /health                     Health check (no auth required)
                                   Returns: { status: "ok", db: "ok", redis: "ok" }
```

---

## ASYNC PROCESSING PIPELINE

Contract analysis is asynchronous. Never process synchronously — it will timeout.

```
1. POST /contracts/upload
   → Validate file (type, size, page count)
   → Save file to local uploads/ folder
   → Insert contract row with status = 'pending'
   → Push job to Redis queue
   → Return { contract_id, status: "pending" } immediately

2. Background worker picks up job from Redis
   → Update status = 'processing'
   → Parse PDF/DOCX → extract raw text + page numbers
   → Chunk text into segments of MAX_TOKENS_PER_CHUNK
   → For each chunk: call AI extraction pipeline
   → Aggregate results
   → Insert clauses + risks into database
   → Calculate overall risk_score
   → Update status = 'completed'
   → If any step fails: update status = 'failed', store error_message

3. Frontend polls GET /contracts/{id}/status every 3 seconds
   → Show progress indicator while status = 'processing'
   → Redirect to contract view when status = 'completed'
   → Show error state if status = 'failed'
```

---

## AI PIPELINE

### Model routing

```python
PRIMARY_MODEL   = "gpt-4o"           # used for all clause extraction
FALLBACK_MODEL  = "claude-sonnet-4-5"  # used if OpenAI fails or rate-limits

# Fallback trigger conditions:
# - OpenAI API returns 5xx error
# - OpenAI rate limit (429) after 2 retries
# - Response fails JSON validation after 2 retries
```

### Document chunking strategy

```
Max chunk size:  6,000 tokens
Chunk overlap:   200 tokens (preserves clause context across boundaries)
Split strategy:  By paragraph boundary, never mid-sentence
                 If a single paragraph exceeds 6,000 tokens, split at sentence boundary
```

### System prompt (clause extraction)

```
You are a contract intelligence analyst. Your job is to extract and analyse
legal clauses from contract documents.

Rules:
1. Extract ONLY clauses that appear in the provided text.
2. Never infer or fabricate clauses not present in the text.
3. Always include the exact source_text verbatim from the document.
4. Return ONLY valid JSON. No preamble, no explanation, no markdown.
5. If a clause type is not present in this chunk, omit it.
6. Confidence score: 0.9+ means the clause is unambiguous.
             0.7–0.9 means moderate confidence, manual review recommended.
             Below 0.7 means uncertain, flag for human review.

Clause types to detect:
liability, indemnification, termination, renewal, payment_terms,
data_privacy, confidentiality, intellectual_property, governing_law, exclusivity
```

### AI output format (every finding must match this schema exactly)

```json
{
  "clauses": [
    {
      "clause_type": "liability",
      "risk_level": "CRITICAL",
      "finding": "Unlimited liability clause detected",
      "explanation": "The agreement contains no cap on financial liability,
                      exposing the company to unlimited financial risk.",
      "recommendation": "Negotiate a liability cap equal to 12 months of
                         contract value or a fixed monetary ceiling.",
      "source_text": "exact verbatim paragraph from the contract here",
      "confidence": 0.95
    }
  ]
}
```

Never return free-form text. Always return structured JSON.
Validate every response against this schema before writing to the database.
If validation fails, retry once. If retry fails, log and skip the chunk.

---

## CLAUSE TYPES

Version 1 detects:

| Clause Type         | Risk Focus                                      |
|---------------------|--------------------------------------------------|
| liability           | Caps, uncapped exposure, mutual vs one-sided     |
| indemnification     | Scope, carve-outs, third-party coverage          |
| termination         | Notice period, termination for convenience       |
| renewal             | Auto-renewal, notice window to cancel            |
| payment_terms       | Payment timing, late fees, currency risk         |
| data_privacy        | GDPR/DPDP compliance, data handling obligations  |
| confidentiality     | Duration, scope, exclusions                      |
| intellectual_property | Ownership of IP created during engagement      |
| governing_law       | Jurisdiction, dispute resolution mechanism       |
| exclusivity         | Lock-in risk, exclusivity duration               |

---

## RISK SCORING

### Per-clause risk levels

```
LOW       Minor concern, standard language
MEDIUM    Non-standard, worth reviewing
HIGH      Significant risk, recommend negotiation
CRITICAL  Must address before signing
```

### Contract-level risk score (0.0 to 10.0)

```python
# Weighted scoring formula
weights = {
    "CRITICAL": 3.0,
    "HIGH":     2.0,
    "MEDIUM":   1.0,
    "LOW":      0.2
}

score = sum(weights[risk.severity] for risk in risks)
normalized = min(score / 10.0, 10.0)   # cap at 10.0

# Risk level thresholds
0.0 – 3.0  → LOW
3.1 – 5.0  → MEDIUM
5.1 – 7.5  → HIGH
7.6 – 10.0 → CRITICAL
```

---

## FILE PROCESSING RULES

```
Max file size:        25 MB
Max pages:            150 pages
Allowed extensions:   .pdf, .docx
Min file size:        1 KB (reject empty files)

Password-protected PDF:   Return error: "Password-protected files are not supported."
Scanned PDF (no text):    Return error: "This PDF appears to be a scanned image.
                           Please upload a text-based PDF."
Corrupt file:             Return error: "File could not be read. Please re-upload."
Unsupported language:     Process anyway, note low confidence scores in output.

Text extraction order (PDF):
  1. Try pdfplumber (best for complex layouts)
  2. Fall back to PyMuPDF if pdfplumber fails
  3. If both fail, mark contract as failed with error message

Text extraction (DOCX):
  Use python-docx. Extract paragraphs + tables.
```

---

## UI REQUIREMENTS

### Dashboard (`/dashboard`)

- Total contracts count
- Risk distribution chart (LOW / MEDIUM / HIGH / CRITICAL counts)
- Recent uploads list (last 5, with status badges)
- Average risk score across all contracts

### Contract List (`/contracts`)

- Table: filename, upload date, status badge, risk level badge, risk score
- Click row → go to contract detail
- Upload button → triggers file picker

### Contract Detail (`/contracts/[id]`)

- Contract metadata (filename, upload date, page count, overall risk score)
- Processing status indicator (if still pending/processing)
- Executive summary section
- Clause list (grouped by clause type)
- Each clause shows: risk level badge, finding, source text highlight
- Risk detail panel (click a risk → see explanation + recommendation)

### Status badges

```
pending     → grey   "Pending"
processing  → blue   "Analysing..."  (animated)
completed   → green  "Complete"
failed      → red    "Failed"
```

---

## RUNNING LOCALLY

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Start background worker (separate terminal)
python -m app.workers.analysis_worker
```

### Frontend

```bash
cd frontend
npm install
npm run dev                        # runs on http://localhost:3000
```

### Verify setup

```bash
# Backend health check
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","db":"ok","redis":"ok"}
```

---

## CODING STANDARDS

### Architecture pattern

```
API route (FastAPI router)
    ↓
Service layer          (business logic, AI calls, orchestration)
    ↓
Repository layer       (all database access — no raw SQL in services)
    ↓
SQLAlchemy models      (ORM definitions only)
```

Rules:
- No business logic in API route handlers
- No raw SQL outside repository layer
- No database calls in service layer (use repositories)
- All functions typed with Python type hints
- All async — use `async def` throughout
- Max function length: 50 lines (split if longer)
- No duplicate code — shared logic goes in `utils/` or base classes

### Required for every new module

- Type annotations on all function signatures
- Docstring on all public functions
- Unit test in `tests/` before marking a feature done
- Repository function, not inline query, for every DB operation

---

## PRODUCT PHILOSOPHY

ContractIQ is NOT:
- ChatGPT for contracts
- Contract storage software
- Another CLM

ContractIQ IS:
- Contract Intelligence
- Risk Identification
- Clause Benchmarking
- Executive Decision Support

Every feature should answer: **"What business risk exists inside this contract?"**

If a feature does not improve contract intelligence, do not build it.

---

## CURRENT TASK RULE

When generating code:

1. Follow the architecture above — no redesigning.
2. Only build the feature that was asked for.
3. Keep code production-ready and fully typed.
4. Local dev context: no S3, no SQS — use local file storage and Redis queue.
5. Always explain decisions before writing implementation code.
6. Every DB query must filter by `company_id`.
7. Every AI response must be validated against the JSON schema before storage.
8. Never hardcode API keys — always read from environment variables.
