"""Scrape the public contribution calendar (no token) into data/contributions.json."""
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "SuhaasS")
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(username):
    response = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "profile-readme-heatmap"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    counts = {}
    for tip in soup.select("tool-tip[for]"):
        match = re.match(r"\s*(\d[\d,]*) contribution", tip.get_text())
        counts[tip["for"]] = int(match.group(1).replace(",", "")) if match else 0

    days = [
        {
            "date": cell["data-date"],
            "level": int(cell["data-level"]),
            "count": counts.get(cell["id"], 0),
        }
        for cell in soup.select("td.ContributionCalendar-day[data-date]")
    ]
    if not days:
        raise RuntimeError("no contribution cells found; GitHub markup may have changed")
    return sorted(days, key=lambda d: d["date"])


def streaks(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)

    # Today may not have activity yet; don't let that zero the current streak.
    tail = days[:-1] if days[-1]["count"] == 0 else days
    current = 0
    for day in reversed(tail):
        if not day["count"]:
            break
        current += 1
    return current, longest


def main():
    days = fetch_days(USERNAME)
    today = date.today().isoformat()
    days = [d for d in days if d["date"] <= today]
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])

    monthly = {}
    for day in days:
        monthly[day["date"][:7]] = monthly.get(day["date"][:7], 0) + day["count"]

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "username": USERNAME,
                "total": sum(d["count"] for d in days),
                "current_streak": current,
                "longest_streak": longest,
                "best_day": {"date": best["date"], "count": best["count"]},
                "active_days": sum(1 for d in days if d["count"]),
                "monthly": monthly,
                "days": days,
            },
            indent=1,
        )
        + "\n"
    )
    print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions -> {OUT}")


if __name__ == "__main__":
    main()
