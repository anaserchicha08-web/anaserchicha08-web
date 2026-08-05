"""
fetch_contributions.py
Scrapes the public GitHub contribution calendar for anaserchicha08-web.
No API token needed — GitHub serves this as public HTML.
Writes data/contributions.json with raw day data + derived stats.
"""

import json
import os
import re
import sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# Force UTF-8 output on Windows to avoid cp1252 errors
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

USERNAME = "anaserchicha08-web"
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_FILE = DATA_DIR / "contributions.json"


def fetch_days() -> list[dict]:
    """Return a list of {date, count, level} dicts sorted oldest-first."""
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # GitHub renders contribution cells as <td> or <rect> with data-date / data-level
    days: list[dict] = []

    # Try <td data-date data-level> (current GitHub HTML)
    cells = soup.find_all("td", attrs={"data-date": True})
    if not cells:
        # Fallback: <rect data-date data-level>  (older format)
        cells = soup.find_all("rect", attrs={"data-date": True})

    for cell in cells:
        d = cell.get("data-date", "")
        level = int(cell.get("data-level", 0))
        # Try to read the tooltip count if present
        count_text = cell.get("data-count", "")
        if count_text:
            count = int(count_text)
        else:
            # Fallback: parse tooltip text like "3 contributions on July 4, 2025"
            label = cell.get("aria-label", "")
            m = re.search(r"(\d+)\s+contribution", label)
            count = int(m.group(1)) if m else 0

        if d:
            days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    """Derive streak, best day, total, and monthly breakdown."""
    total = sum(d["count"] for d in days)

    # Longest streak
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    # Current streak (count backwards from today)
    current_streak = 0
    today_str = date.today().isoformat()
    for d in reversed(days):
        if d["date"] > today_str:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best = max(days, key=lambda x: x["count"], default={"date": "", "count": 0})

    # Monthly totals for last 12 months
    monthly: dict[str, int] = {}
    for d in days:
        ym = d["date"][:7]  # "YYYY-MM"
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total": total,
        "longest_streak": longest,
        "current_streak": current_streak,
        "best_day": best,
        "monthly_totals": monthly,
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching contributions for @{USERNAME} …")
    days = fetch_days()

    if not days:
        print("[WARN] No contribution data found. The profile may be private or the page structure changed.")
        # Write empty placeholder so downstream scripts don't crash
        OUT_FILE.write_text(json.dumps({"days": [], "stats": {}, "generated_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")
        return

    stats = compute_stats(days)
    payload = {
        "username": USERNAME,
        "days": days,
        "stats": stats,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    OUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Wrote {len(days)} days -> {OUT_FILE}")
    print(f"     Total: {stats['total']:,}  |  Current streak: {stats['current_streak']}d  |  Longest: {stats['longest_streak']}d")
    print(f"     Best day: {stats['best_day']['date']} ({stats['best_day']['count']} contributions)")


if __name__ == "__main__":
    main()
