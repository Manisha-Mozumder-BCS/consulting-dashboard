import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Consulting Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = Path(os.environ.get("DB_DIR", "/data"))
DB_PATH = DB_DIR / "submissions.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "mozumder123")


def init_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at REAL NOT NULL,
                name TEXT NOT NULL,
                business TEXT DEFAULT '',
                stage TEXT DEFAULT '',
                region TEXT DEFAULT '',
                overall_score REAL DEFAULT 0,
                maturity_label TEXT DEFAULT '',
                dimension_scores TEXT DEFAULT '[]',
                patterns TEXT DEFAULT '[]',
                strengths TEXT DEFAULT '[]',
                gaps TEXT DEFAULT '[]',
                action_steps TEXT DEFAULT '[]',
                reflections TEXT DEFAULT '[]',
                coachability_insight TEXT DEFAULT '',
                consulting_headline TEXT DEFAULT '',
                consulting_body TEXT DEFAULT '',
                environment_label TEXT DEFAULT '',
                environment_conditions TEXT DEFAULT '[]',
                raw_answers TEXT DEFAULT '[]'
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/api/submit")
async def submit_assessment(request: Request):
    data = await request.json()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO submissions (
                created_at, name, business, stage, region,
                overall_score, maturity_label, dimension_scores,
                patterns, strengths, gaps, action_steps,
                reflections, coachability_insight,
                consulting_headline, consulting_body,
                environment_label, environment_conditions, raw_answers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            data.get("name", ""),
            data.get("business", ""),
            data.get("stage", ""),
            data.get("region", ""),
            data.get("overall_score", 0),
            data.get("maturity_label", ""),
            json.dumps(data.get("dimension_scores", [])),
            json.dumps(data.get("patterns", [])),
            json.dumps(data.get("strengths", [])),
            json.dumps(data.get("gaps", [])),
            json.dumps(data.get("action_steps", [])),
            json.dumps(data.get("reflections", [])),
            data.get("coachability_insight", ""),
            data.get("consulting_headline", ""),
            data.get("consulting_body", ""),
            data.get("environment_label", ""),
            json.dumps(data.get("environment_conditions", [])),
            json.dumps(data.get("raw_answers", [])),
        ))
        conn.commit()
    return {"status": "ok"}


@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    if data.get("password") == ADMIN_PASSWORD:
        return {"status": "ok", "token": "authenticated"}
    return JSONResponse(status_code=401, content={"error": "Invalid password"})


@app.get("/api/submissions")
async def get_submissions(password: str = ""):
    if password != ADMIN_PASSWORD:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM submissions ORDER BY created_at DESC").fetchall()
    results = []
    for row in rows:
        r = dict(row)
        for field in ["dimension_scores", "patterns", "strengths", "gaps",
                       "action_steps", "reflections", "environment_conditions", "raw_answers"]:
            try:
                r[field] = json.loads(r[field])
            except (json.JSONDecodeError, TypeError):
                pass
        results.append(r)
    return results


@app.get("/api/analytics")
async def get_analytics(password: str = ""):
    if password != ADMIN_PASSWORD:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM submissions ORDER BY created_at DESC").fetchall()

    if not rows:
        return {
            "total": 0, "avg_score": 0, "maturity_distribution": {},
            "stage_distribution": {}, "region_distribution": {},
            "dimension_averages": {}, "score_over_time": [],
            "recent_submissions": []
        }

    total = len(rows)
    scores = [r["overall_score"] for r in rows]
    avg_score = sum(scores) / total if total else 0

    maturity_dist = {}
    stage_dist = {}
    region_dist = {}
    dim_totals = {}
    dim_counts = {}
    score_over_time = []

    for row in rows:
        mat = row["maturity_label"] or "Unknown"
        maturity_dist[mat] = maturity_dist.get(mat, 0) + 1
        st = row["stage"] or "Unknown"
        stage_dist[st] = stage_dist.get(st, 0) + 1
        reg = row["region"] or "Unknown"
        region_dist[reg] = region_dist.get(reg, 0) + 1

        try:
            dims = json.loads(row["dimension_scores"])
            for d in dims:
                key = d.get("label", d.get("key", ""))
                if key:
                    dim_totals[key] = dim_totals.get(key, 0) + d.get("score", 0)
                    dim_counts[key] = dim_counts.get(key, 0) + 1
        except (json.JSONDecodeError, TypeError):
            pass

        score_over_time.append({
            "date": row["created_at"],
            "score": row["overall_score"],
            "name": row["name"]
        })

    dim_averages = {k: round(dim_totals[k] / dim_counts[k], 2) for k in dim_totals}

    return {
        "total": total,
        "avg_score": round(avg_score, 2),
        "maturity_distribution": maturity_dist,
        "stage_distribution": stage_dist,
        "region_distribution": region_dist,
        "dimension_averages": dim_averages,
        "score_over_time": score_over_time,
    }


@app.delete("/api/reset")
async def reset_data(request: Request):
    data = await request.json()
    if data.get("password") != ADMIN_PASSWORD:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    with get_db() as conn:
        conn.execute("DELETE FROM submissions")
        conn.commit()
    return {"status": "ok", "message": "All data has been reset"}


@app.delete("/api/submissions/{submission_id}")
async def delete_submission(submission_id: int, request: Request):
    data = await request.json()
    if data.get("password") != ADMIN_PASSWORD:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    with get_db() as conn:
        conn.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
        conn.commit()
    return {"status": "ok"}


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    html_path = Path(__file__).parent / "static" / "admin.html"
    return html_path.read_text()


@app.get("/", response_class=HTMLResponse)
async def root():
    return '<meta http-equiv="refresh" content="0;url=/admin">'
