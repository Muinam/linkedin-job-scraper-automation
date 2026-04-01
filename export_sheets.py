import gspread
from google.oauth2.service_account import Credentials
from database import get_all_jobs
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def serialize(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value if value else ""

def is_recent(posted):
    if not posted: return False
    p = str(posted).lower()
    return any(x in p for x in ["just now","minute","hour","1 day","2 days"])

def clear_sheet():
    creds  = Credentials.from_service_account_file("google_credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet  = client.open(os.getenv("SHEET_NAME")).sheet1
    sheet.clear()
    print("Google Sheet cleared!")

def export_to_sheets():
    creds  = Credentials.from_service_account_file("google_credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet  = client.open(os.getenv("SHEET_NAME")).sheet1

    all_jobs    = get_all_jobs()
    recent_jobs = [j for j in all_jobs if is_recent(str(j[5]))]

    print(f"Total jobs: {len(all_jobs)} | Recent: {len(recent_jobs)}")

    clear_sheet()

    # Correct Headers
    sheet.append_row([
        "ID", "Title", "Company", "Location", "Link",
        "Posted", "Posted Date", "Level", "Keyword", "Scraped At"
    ])

    rows = []
    for job in recent_jobs:
        rows.append([
            serialize(job[0]),   # ID
            serialize(job[1]),   # Title
            serialize(job[2]),   # Company
            serialize(job[3]),   # Location
            serialize(job[4]),   # Link
            serialize(job[5]),   # Posted
            serialize(job[6]),   # Posted Date
            serialize(job[7]),   # Level
            serialize(job[8]),   # Keyword
            serialize(job[10])   # Scraped At
        ])

    if rows:
        sheet.append_rows(rows)

    print(f"✅ Exported {len(rows)} jobs to Google Sheets successfully!")
    return len(rows)

if __name__ == "__main__":
    export_to_sheets()