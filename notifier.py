import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import time

load_dotenv()

SENDER   = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("EMAIL_RECEIVER")

LEVEL_COLORS = {
    "Intern":             "#9c27b0",
    "Entry Level":        "#2196f3",
    "Mid Level":          "#4caf50",
    "Senior":             "#ff9800",
    "Consultant/Manager": "#f44336",
    "Unknown":            "#888888",
}

def send_email(subject, html_body, recipient=None):
    to = recipient if recipient else RECEIVER
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html"))
    time.sleep(3)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, to, msg.as_string())
    print(f"Email sent to {to}")

def send_job_alert(keyword, jobs, recipient=None):
    rows = ""
    for job in jobs[:30]:
        level = job.get("level", "Unknown")
        color = LEVEL_COLORS.get(level, "#888")
        posted      = job.get("posted", "")
        posted_date = job.get("posted_date", "")
        date_str    = f"{posted_date} ({posted})" if posted_date else posted

        rows += f"""
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #eee">
            {job.get('title','')}
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;color:#555">
            {job.get('company','')}
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;color:#555">
            {job.get('location','')}
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;text-align:center">
            <span style="background:{color};color:white;padding:3px 10px;border-radius:20px;font-size:11px;white-space:nowrap">
              {level}
            </span>
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;color:#888;font-size:12px;white-space:nowrap">
            {date_str}
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;text-align:center">
            <a href="{job.get('link','')}" style="background:#0077b5;color:white;padding:4px 12px;border-radius:6px;text-decoration:none;font-size:12px">
              Apply
            </a>
          </td>
        </tr>
        """

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:900px;margin:auto">
      <div style="background:#0077b5;padding:20px 24px;border-radius:10px 10px 0 0">
        <h2 style="color:white;margin:0">LinkedIn Job Alert</h2>
        <p style="color:#cce5f3;margin:4px 0 0">{len(jobs)} naye jobs — <b>{keyword}</b></p>
      </div>
      <div style="padding:16px;background:#f9f9f9">
        <p style="font-size:12px;color:#888;margin:0">
          Level key:
          <span style="background:#9c27b0;color:white;padding:2px 8px;border-radius:10px;font-size:11px">Intern</span>
          <span style="background:#2196f3;color:white;padding:2px 8px;border-radius:10px;font-size:11px">Entry</span>
          <span style="background:#4caf50;color:white;padding:2px 8px;border-radius:10px;font-size:11px">Mid</span>
          <span style="background:#ff9800;color:white;padding:2px 8px;border-radius:10px;font-size:11px">Senior</span>
          <span style="background:#f44336;color:white;padding:2px 8px;border-radius:10px;font-size:11px">Consultant</span>
        </p>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Arial;font-size:13px">
        <tr style="background:#e3f2fd">
          <th style="padding:10px 8px;text-align:left">Title</th>
          <th style="padding:10px 8px;text-align:left">Company</th>
          <th style="padding:10px 8px;text-align:left">Location</th>
          <th style="padding:10px 8px">Level</th>
          <th style="padding:10px 8px">Posted</th>
          <th style="padding:10px 8px">Link</th>
        </tr>
        {rows}
      </table>
      <div style="padding:16px;background:#f9f9f9;border-radius:0 0 10px 10px">
        <p style="font-size:11px;color:#aaa;margin:0">
          Top 30 jobs shown. Baqi Google Sheets mein hain.
        </p>
      </div>
    </body></html>
    """
    send_email(f"LinkedIn: {len(jobs)} jobs — {keyword}", html, recipient)