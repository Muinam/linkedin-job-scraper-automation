# LinkedIn Job Scraper — Automated Pipeline

> Scrape 1000+ fresh LinkedIn jobs daily, filter by experience level, auto-export to Google Sheets, and receive beautiful email alerts. All automated. Zero manual effort.

---

## What This Does

Every time you run this system, it:

1. Opens LinkedIn Jobs in a stealth browser
2. Scrapes all jobs posted in the **last 48 hours**
3. Detects experience level from job titles automatically
4. Removes duplicates using MD5 hashing
5. Saves everything to PostgreSQL database
6. Updates Google Sheets with color-coded levels
7. Sends HTML email alerts with Apply links to multiple recipients
8. Provides one-click CSV download from the web interface

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Browser Automation | Python + Playwright (stealth mode) |
| HTML Parsing | BeautifulSoup4 + lxml |
| API Backend | FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| Database | PostgreSQL |
| Sheets Export | Google Sheets API (gspread) |
| Email Alerts | Gmail SMTP |
| Scheduler | Make.com |
| Frontend | Vanilla HTML/CSS/JS |
---


![Project Image](Linkein-scaper)


## Project Structure
```

linkedin-scraper/
│
├── scraper/
│   ├── __init__.py
│   ├── browser.py          # Playwright stealth browser setup
│   └── linkedin_jobs.py    # Scraping + filtering logic
│
├── templates/
│   └── index.html          # Web frontend
│
├── api.py                  # FastAPI endpoints
├── tasks.py                # Celery task definitions
├── database.py             # PostgreSQL operations
├── notifier.py             # Gmail email alerts
├── export_sheets.py        # Google Sheets export
├── run.py                  # One-command startup script
├── .env                    # Environment variables (secrets)
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Features

### Smart Filtering

- Only scrapes jobs posted in the **last 48 hours** using LinkedIn's `sortBy=DD` parameter
- Stops automatically when old posts appear — saves 70% unnecessary requests
- Auto-clears old data on every fresh run — zero data mixing

### Experience Level Detection

Automatically detects from job title — no LinkedIn API needed:

| Level | Keywords Detected |
|-------|------------------|
| Intern | intern, internship, trainee |
| Entry Level | junior, entry, associate, graduate, fresh |
| Mid Level | everything else |
| Senior | senior, sr., lead, principal, staff, head |
| Consultant | manager, director, vp, chief, consultant |

### Deduplication

Every job gets an MD5 hash of `title + company + link`. Same job posted twice? Stored once. Always.

### Parallel Processing

Celery + Redis runs multiple keywords simultaneously — 8x faster than sequential scraping.

---

## Setup Guide

### Prerequisites

- Python 3.10+
- PostgreSQL 17
- Redis
- Google Cloud account (for Sheets)
- Gmail account with App Password
- Make.com account (for scheduling)

---

### Step 1 — Clone and Setup Environment

```bash
git clone https://github.com/yourusername/linkedin-job-scraper.git
cd linkedin-job-scraper

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 2 — Install Dependencies

```bash
pip install playwright beautifulsoup4 lxml psycopg2-binary celery redis fastapi uvicorn python-dotenv requests gspread google-auth slack-sdk

playwright install chromium
```

### Step 3 — PostgreSQL Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE linkedin_jobs;"
```

### Step 4 — Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account** → download JSON key
5. Rename the file to `google_credentials.json` and place in project root
6. Create a Google Sheet named `LinkedIn Jobs`
7. Share the sheet with the service account email (Editor access)

### Step 5 — Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate password for `Mail`
5. Copy the 16-character password

### Step 6 — Environment Variables

Create `.env` file in project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=linkedin_jobs
DB_USER=postgres
DB_PASS=yourpassword

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD=your16digitapppassword
EMAIL_RECEIVER=yourgmail@gmail.com

# Google Sheets
SHEET_NAME=LinkedIn Jobs

# Scraper Settings
SCRAPE_DELAY_MIN=2
SCRAPE_DELAY_MAX=5
MAX_PAGES=20
```

---

### Step 7 — Run the Project

```bash
python run.py
```

This starts:

- Celery worker (background task processor)
- FastAPI server (API + frontend)

Open browser:

```
http://127.0.0.1:8000
```

---

## Using the Web Interface

1. Enter job **keywords** (one per line).

   AI Engineer
   Machine Learning Engineer
   Data Scientist

2. Select **experience levels** (optional — leave blank for all)
   - Intern
   - Entry Level
   - Mid Level
   - Senior
   - Consultant

3. Set **location** (default: Pakistan)

4. Enter **email addresses** (one per line — multiple supported)

    ```
   ali@gmail.com
   sara@company.com
   ```

5. Click **Scraping Shuru Karo**

6. After completion — click **CSV Download Karo**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web frontend |
| POST | `/scrape` | Trigger scraping task |
| GET | `/jobs` | Get all jobs (JSON) |
| GET | `/download-csv` | Download jobs as CSV |
| GET | `/health` | Health check |

### POST /scrape — Request Body

```json
{
  "keywords": ["AI Engineer", "Data Scientist"],
  "location": "Pakistan",
  "emails": ["you@gmail.com"],
  "levels": ["Entry Level", "Mid Level"]
}
```

---

## Make.com Automation (Daily Schedule)

To run automatically every day:

1. Install [ngrok](https://ngrok.com) and expose your local server:

   ```bash
   ngrok http 8000
   ```

2. In Make.com, create a scenario:

   ```
   Schedule (Daily 9:00 AM)
        ↓
   HTTP POST → https://your-ngrok-url.ngrok-free.app/scrape
   Body: {"keywords": ["AI Engineer"], "location": "Pakistan", "emails": ["you@gmail.com"]}
   ```

---

## Email Alert Format

Each email contains:

- Job title
- Company name
- Location
- Experience level badge (color-coded)
- Posted date
- Direct Apply link

| Badge Color | Level |
|-------------|-------|
| Purple | Intern |
| Blue | Entry Level |
| Green | Mid Level |
| Orange | Senior |
| Red | Consultant/Manager |

---

## Google Sheets Output

Columns exported:

| ID | Title | Company | Location | Link | Posted | Posted Date | Level | Keyword | Scraped At |
|----|-------|---------|----------|------|--------|-------------|-------|---------|------------|

Level column is **color-coded** automatically:

- Purple → Intern
- Blue → Entry Level
- Green → Mid Level
- Orange → Senior
- Red → Consultant

---

## Performance

| Metric | Value |
|--------|-------|
| Jobs per keyword | ~1,000–1,400 |
| Scrape time (1 keyword) | ~2.5 minutes |
| Parallel keywords | 8 simultaneously |
| Deduplication | MD5 hash-based |
| Data freshness | Last 48 hours only |

---

## Anti-Detection Features

- Headless Chromium with stealth mode
- `navigator.webdriver` property hidden
- Randomized user agents (Chrome, Safari, Firefox)
- Human-like random delays between requests
- Scroll simulation on each page
- Asia/Karachi timezone set on browser context

---

## Common Issues

**`psql` not found on Windows**

```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
```

**Celery not connecting to Redis**

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

**Google Sheets permission error**

- Make sure you shared the sheet with the service account email
- Check the email in `google_credentials.json` → `client_email` field

**Email not sending**

- Verify App Password is correct (16 chars, no spaces)
- Make sure 2-Step Verification is enabled on Gmail

---

## Roadmap

- [ ] LinkedIn login for more job data
- [ ] Salary range extraction
- [ ] Slack notification support
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] Job matching score based on user profile
- [ ] Dashboard with charts and analytics

---

## Important Note

This project is built for **educational and personal productivity purposes**. LinkedIn's Terms of Service restricts automated scraping. Use responsibly — respect rate limits and do not use for commercial data resale.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Built with Python, patience, and too much coffee.

If this helped you — give it a star and share it.

**LinkedIn:** 'www.linkedin.com/in/inam-ur-rehman-61ba85291'
