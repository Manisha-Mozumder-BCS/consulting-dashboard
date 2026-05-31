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
- **Database**: SQLite with persistent volume
- **Frontend**: Vanilla HTML/CSS/JS with Chart.js
- **Deployment**: Fly.io

## Local Development

```bash
pip install fastapi uvicorn
DB_DIR=./data ADMIN_PASSWORD=mozumder123 uvicorn app:app --reload --port 8000
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
