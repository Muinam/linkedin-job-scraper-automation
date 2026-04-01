import asyncio
import random
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from scraper.browser import get_browser

load_dotenv()

DELAY_MIN = float(os.getenv("SCRAPE_DELAY_MIN", 2))
DELAY_MAX = float(os.getenv("SCRAPE_DELAY_MAX", 5))
MAX_PAGES = int(os.getenv("MAX_PAGES", 20))

def is_recent(posted):
    if not posted:
        return False
    posted = posted.lower().strip()
    if "just now" in posted: return True
    if "minute"   in posted: return True
    if "hour"     in posted: return True
    if "1 day"    in posted: return True
    if "2 days"   in posted: return True
    return False

def detect_level(title):
    if not title:
        return "Unknown"
    t = title.lower()
    if any(w in t for w in ["intern", "internship", "trainee"]):
        return "Intern"
    if any(w in t for w in ["junior", "entry", "associate", "graduate", "fresh"]):
        return "Entry Level"
    if any(w in t for w in ["senior", "sr.", "lead", "principal", "staff", "head"]):
        return "Senior"
    if any(w in t for w in ["manager", "director", "vp ", "chief", "cto", "consultant"]):
        return "Consultant/Manager"
    return "Mid Level"

async def scrape_jobs(keyword="AI Engineer", location="Pakistan"):
    print(f"Starting scrape: {keyword} | {location}")
    p, browser, context = await get_browser()
    page = await context.new_page()
    all_jobs = []

    try:
        for page_num in range(0, MAX_PAGES * 25, 25):
            url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={keyword.replace(' ', '%20')}"
                f"&location={location.replace(' ', '%20')}"
                f"&sortBy=DD"
                f"&start={page_num}"
            )
            print(f"  Scraping page {page_num // 25 + 1}...")

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            cards = soup.find_all("div", class_="base-card")

            if not cards:
                print(f"  No more cards — stopping.")
                break

            old_count = 0
            for card in cards:
                title_el   = card.find("h3", class_="base-search-card__title")
                company_el = card.find("h4", class_="base-search-card__subtitle")
                loc_el     = card.find("span", class_="job-search-card__location")
                link_el    = card.find("a", class_="base-card__full-link")
                time_el    = card.find("time")

                posted = time_el.get_text(strip=True) if time_el else None
                title  = title_el.get_text(strip=True) if title_el else None

                # Date attribute bhi lo
                posted_date = time_el.get("datetime", "") if time_el else ""

                if not is_recent(posted):
                    old_count += 1
                    continue

                all_jobs.append({
                    "title":       title,
                    "company":     company_el.get_text(strip=True) if company_el else None,
                    "location":    loc_el.get_text(strip=True)     if loc_el     else None,
                    "link":        link_el["href"]                  if link_el    else None,
                    "posted":      posted,
                    "posted_date": posted_date,
                    "level":       detect_level(title),
                })

            print(f"  Recent: {len(all_jobs)} | Old skipped: {old_count}")
            if old_count >= 20:
                print("  Purani jobs aa rahi hain — band karte hain.")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()
        await p.stop()

    return all_jobs