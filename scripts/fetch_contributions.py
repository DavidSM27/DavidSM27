"""Descarga tu calendario de contribuciones (sin token) y calcula estadisticas.

Uso:  python scripts/fetch_contributions.py [usuario]
Salida: data/contributions.json
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DEFAULT_USER = "DavidSM27"
OUT = Path("data/contributions.json")


def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days, guessed = [], False
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        level = int(td.get("data-level", "0"))
        m = re.match(r"(\d[\d,]*)\s+contribution", tips.get(td.get("id"), ""))
        if m:
            count = int(m.group(1).replace(",", ""))
        else:
            count, guessed = (level if level else 0), guessed or level > 0
        days.append({"date": date, "count": count, "level": level})
    days.sort(key=lambda d: d["date"])
    if guessed:
        print("Aviso: no se encontraron los conteos exactos; se estimaron a partir del nivel.")
    return days


def stats(days):
    by_date = {d["date"]: d["count"] for d in days}
    total = sum(by_date.values())

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    current = 0
    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:
        i -= 1  # hoy aun puede no tener contribuciones
    while i >= 0 and days[i]["count"] > 0:
        current += 1
        i -= 1

    best = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

    return {"total": total, "current_streak": current, "longest_streak": longest,
            "best_day": {"date": best["date"], "count": best["count"]}, "months": months}


def main():
    user = (sys.argv[1] if len(sys.argv) > 1
            else os.environ.get("GITHUB_REPOSITORY_OWNER") or DEFAULT_USER)
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if not days:
        raise SystemExit("No se encontraron dias. Revisa el usuario o si GitHub cambio el HTML.")
    data = {"user": user, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "days": days, **stats(days)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"Listo: {OUT} ({len(days)} dias, {data['total']:,} contribuciones)")


if __name__ == "__main__":
    main()