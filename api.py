import os
import csv
import io
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI()

class ScrapeRequest(BaseModel):
    keywords: List[str]
    location: str = "Pakistan"
    emails: List[str]
    levels: Optional[List[str]] = []

@app.on_event("startup")
async def startup():
    from database import create_table
    create_table()

@app.get("/", response_class=HTMLResponse)
async def frontend():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/scrape")
async def trigger_scrape(req: ScrapeRequest):
    from tasks import scrape_and_notify
    task = scrape_and_notify.delay(
        req.keywords, req.location, req.emails, req.levels
    )
    return {"status": "started", "task_id": task.id}

@app.get("/download-csv")
async def download_csv():
    from database import get_all_jobs
    from datetime import datetime

    jobs = get_all_jobs()

    def is_recent(posted):
        if not posted: 
            return False
        p = str(posted).lower()
        return any(x in p for x in ["just now", "minute", "hour", "1 day", "2 days"])

    recent = [j for j in jobs if is_recent(str(j[5]))]

    output = io.StringIO()
    writer = csv.writer(output)

    # Correct Headers
    writer.writerow([
        "ID", "Title", "Company", "Location", "Link",
        "Posted", "Posted Date", "Level", "Keyword", "Scraped At"
    ])

    for job in recent:
        writer.writerow([
            job[0],                    # ID
            job[1],                    # Title
            job[2],                    # Company
            job[3],                    # Location
            job[4],                    # Link
            job[5],                    # Posted
            job[6],                    # Posted Date
            job[7] if len(job) > 7 else "",   # Level
            job[8] if len(job) > 8 else "",   # Keyword
            job[10].strftime("%Y-%m-%d %H:%M:%S") if len(job) > 10 and hasattr(job[10], 'strftime') else str(job[10]) if len(job) > 10 else ""
        ])

    output.seek(0)
    filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/health")
async def health():
    return {"status": "ok"}