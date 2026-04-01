import psycopg2
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

def create_table():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          SERIAL PRIMARY KEY,
            title       TEXT,
            company     TEXT,
            location    TEXT,
            link        TEXT,
            posted      TEXT,
            posted_date TEXT,
            level       TEXT,
            keyword     TEXT,
            hash        TEXT UNIQUE,
            scraped_at  TIMESTAMP DEFAULT NOW()
        )
    """)
    # Purani table mein columns add karo agar nahi hain
    cur.execute("""
        ALTER TABLE jobs
        ADD COLUMN IF NOT EXISTS posted_date TEXT,
        ADD COLUMN IF NOT EXISTS level TEXT
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Table ready!")

def save_jobs(jobs, keyword=""):
    conn = get_connection()
    cur  = conn.cursor()
    saved = skipped = 0

    for job in jobs:
        job_hash = hashlib.md5(
            f"{job.get('title')}{job.get('company')}{job.get('link')}".encode()
        ).hexdigest()

        try:
            cur.execute("""
                INSERT INTO jobs
                    (title, company, location, link, posted, posted_date, level, keyword, hash)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (hash) DO NOTHING
            """, (
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("link"),
                job.get("posted"),
                job.get("posted_date"),
                job.get("level"),
                keyword,
                job_hash
            ))
            if cur.rowcount > 0:
                saved += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Saved: {saved} | Skipped: {skipped}")

def get_all_jobs():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY scraped_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def clear_all_jobs():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("TRUNCATE TABLE jobs RESTART IDENTITY;")
    conn.commit()
    cur.close()
    conn.close()
    print("Database cleared!")