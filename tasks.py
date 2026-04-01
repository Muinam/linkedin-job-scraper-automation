import asyncio
import os
import time
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery("linkedin", broker=os.getenv("REDIS_URL"))

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_and_notify(self, keywords, location, emails, levels=None):
    from scraper.linkedin_jobs import scrape_jobs
    from database import save_jobs, clear_all_jobs
    from export_sheets import export_to_sheets, clear_sheet
    from notifier import send_job_alert

    all_results = {}

    try:
        # === PURANA DATA CLEAR ===
        print("Purana data clear kar raha hoon...")
        clear_all_jobs()
        clear_sheet()
        print("Clear ho gaya!")

        # === SCRAPING ===
        for keyword in keywords:
            print(f"Scraping: {keyword}")
            jobs = asyncio.run(scrape_jobs(keyword, location))

            if levels and len(levels) > 0:
                jobs = [j for j in jobs if j.get("level") in levels]
                print(f"After level filter: {len(jobs)} jobs")

            save_jobs(jobs, keyword=keyword)
            all_results[keyword] = jobs
            print(f"Done: {len(jobs)} jobs for {keyword}")

        # === GOOGLE SHEETS ===
        print("Google Sheets update ho rahi hai...")
        export_to_sheets()

        # === EMAILS with delay (second email ke liye important) ===
        print(f"{len(emails)} emails pe bhej raha hoon...")
        for email in emails:
            print(f"Sending to → {email}")
            for keyword, jobs in all_results.items():
                if jobs:
                    send_job_alert(keyword, jobs, recipient=email)
                    time.sleep(8)          # Gmail ko rest do
            time.sleep(5)

        total = sum(len(j) for j in all_results.values())
        print(f"Sab done! Total: {total} jobs | {len(emails)} emails bheje gaye")
        return f"Done: {total} jobs"

    except Exception as exc:
        print(f"Error: {exc}")
        raise self.retry(exc=exc)