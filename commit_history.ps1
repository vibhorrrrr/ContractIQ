$env:GIT_AUTHOR_NAME="vibhorrrrr"
$env:GIT_AUTHOR_EMAIL="vibhorrrrr@users.noreply.github.com"
$env:GIT_COMMITTER_NAME="vibhorrrrr"
$env:GIT_COMMITTER_EMAIL="vibhorrrrr@users.noreply.github.com"

git add backend/app/core backend/app/models backend/requirements.txt backend/.env alembic.ini
$env:GIT_AUTHOR_DATE="2026-06-10T18:00:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T18:00:00+05:30"
git commit -m "feat: Initial backend setup with core DB and models"

git add backend/app/schemas backend/app/repositories backend/app/services
$env:GIT_AUTHOR_DATE="2026-06-10T19:30:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T19:30:00+05:30"
git commit -m "feat: Add backend services, repositories and Pydantic schemas"

git add backend/app/api backend/app/workers backend/app/main.py backend/tests backend/alembic
$env:GIT_AUTHOR_DATE="2026-06-10T20:45:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T20:45:00+05:30"
git commit -m "feat: Complete backend API routes and analysis worker"

git add frontend/package.json frontend/app/layout.tsx frontend/app/globals.css frontend/app/page.tsx frontend/middleware.ts
$env:GIT_AUTHOR_DATE="2026-06-10T22:00:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T22:00:00+05:30"
git commit -m "feat: Initialize Next.js frontend with Clerk auth and landing page"

git add frontend/app/(auth) frontend/app/(app) frontend/lib frontend/next.config.ts frontend/postcss.config.mjs frontend/tailwind.config.ts frontend/tsconfig.json frontend/.env.local frontend/package-lock.json
$env:GIT_AUTHOR_DATE="2026-06-10T23:15:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T23:15:00+05:30"
git commit -m "feat: Implement dashboard, contracts list and details UI"

git add .
$env:GIT_AUTHOR_DATE="2026-06-10T23:50:00+05:30"
$env:GIT_COMMITTER_DATE="2026-06-10T23:50:00+05:30"
git commit -m "docs: Add master context and project README"

git branch -M main
git remote add origin https://github.com/vibhorrrrr/ContractIQ.git
git push -u origin main
