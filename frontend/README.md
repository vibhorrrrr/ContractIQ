# ContractIQ — Frontend

Next.js 15 (App Router) client for the ContractIQ platform. Handles authentication, contract uploads, risk visualisation, and the analytics dashboard.

## Tech Stack

- **Framework** — Next.js 15 (App Router, Server Components)
- **Language** — TypeScript
- **Auth** — [Clerk](https://clerk.com) (JWT-based, middleware-protected routes)
- **Styling** — Tailwind CSS
- **HTTP** — Fetch-based API client (`lib/api.ts`)

## Directory Layout

```
app/
├── (auth)/                 # Public auth routes (Clerk)
│   ├── sign-in/            # /sign-in
│   └── sign-up/            # /sign-up
├── (app)/                  # Authenticated app shell
│   ├── layout.tsx          # Sidebar + header layout
│   ├── dashboard/          # /dashboard — stats, risk chart, recent uploads
│   └── contracts/          # /contracts — list, upload, [id] detail
├── layout.tsx              # Root layout (ClerkProvider, fonts, global CSS)
├── page.tsx                # Landing page (public)
└── globals.css             # Global styles + Tailwind directives
lib/
├── api.ts                  # Typed API client (auto-attaches Clerk JWT)
└── utils.ts                # Shared helpers
middleware.ts               # Clerk route protection
```

## Key Pages

| Route | Description |
|---|---|
| `/` | Public landing page with feature overview and CTA |
| `/sign-in` | Clerk sign-in |
| `/sign-up` | Clerk sign-up |
| `/dashboard` | Company-wide stats — total contracts, risk distribution, recent uploads |
| `/contracts` | Contract list with upload dialog (PDF / DOCX, max 25 MB) |
| `/contracts/[id]` | Contract detail — extracted clauses, risk findings, executive summary |

## Getting Started

```bash
# Install dependencies
npm install

# Copy env template and fill in your keys
cp .env.example .env.local

# Start dev server
npm run dev
```

App runs at **http://localhost:3000**.

## Environment Variables

See [`.env.example`](.env.example) for the full list.

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY` | Clerk secret key (server-side) |
| `NEXT_PUBLIC_API_URL` | Backend API base URL (default: `http://localhost:8000`) |

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
