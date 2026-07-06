# Consulting Dashboard

Admin dashboard for the Entrepreneur Readiness Assessment Tool by Manisha Mozumder Business Consulting Services.

## Features

- **Password-protected admin login**
- **Analytics overview**: Total assessments, average scores, maturity distribution, dimension averages
- **Interactive charts**: Radar chart for dimensions, doughnut for maturity levels, trend line, stage breakdown
- **Submissions table**: Search, view details, delete individual entries
- **Detail view**: Full breakdown of each assessment including dimension scores, patterns, reflections, and consulting recommendations
- **Reset button**: Clear all submission data

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Postgres in production (via `DATABASE_URL`), SQLite fallback for local dev
- **Frontend**: Vanilla HTML/CSS/JS with Chart.js
- **Deployment**: Render (Docker)

## Data persistence

Set the `DATABASE_URL` environment variable to a Postgres connection string
(e.g. a free permanent database from [Neon](https://neon.tech)) so submissions
persist across restarts and redeploys. This is required on hosts with an
ephemeral filesystem such as Render's free tier — without it, submissions are
stored in a local SQLite file that gets wiped whenever the instance spins down.

When `DATABASE_URL` is unset, the app falls back to SQLite at `DB_DIR/submissions.db`.

## Local Development

```bash
pip install -r requirements.txt
# SQLite (local):
DB_DIR=./data ADMIN_PASSWORD=mozumder123 uvicorn main:app --reload --port 8000
# or against Postgres:
DATABASE_URL=postgresql://user:pass@host/db ADMIN_PASSWORD=mozumder123 uvicorn main:app --reload --port 8000
```

Then visit http://localhost:8000/admin

## API Endpoints

- `POST /api/submit` - Submit assessment results
- `POST /api/login` - Authenticate with password
- `GET /api/submissions?password=...` - Get all submissions
- `GET /api/analytics?password=...` - Get analytics data
- `DELETE /api/reset` - Reset all data (requires password in body)
- `DELETE /api/submissions/{id}` - Delete a single submission
- `GET /admin` - Admin dashboard UI
