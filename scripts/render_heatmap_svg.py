"""Dibuja data/contributions.json como un heatmap SVG animado (53 semanas x 7 dias).

Uso:  python scripts/render_heatmap_svg.py
Salida: contrib-heatmap.svg
"""
import datetime as dt
import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 12, 3
PITCH = CELL + GAP
W = 860
LEFT, TOP = 40, 40
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    if not DATA.exists():
        raise SystemExit(f"Falta {DATA}. Ejecuta antes fetch_contributions.py")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    max_count = max((d["count"] for d in days), default=0) or 1
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # domingo = 0

    cells, month_labels, last_month = [], [], None
    n_weeks = 0
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        idx = (date - first).days + offset
        wk, row = idx // 7, idx % 7
        n_weeks = max(n_weeks, wk + 1)
        level = d["level"]
        if level >= 4 and d["count"] >= 0.75 * max_count:
            level = 5  # extremo neon
        x, y = LEFT + wk * PITCH, TOP + row * PITCH
        delay = (wk + row) * 0.018
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{d["count"]} contributions on {d["date"]}</title></rect>')
        if row == 0 or wk == 0:
            if date.month != last_month and (wk == 0 and row == 0 or row == 0):
                if not month_labels or x - month_labels[-1][0] >= 3 * PITCH:
                    month_labels.append((x, MONTHS[date.month - 1]))
                last_month = date.month

    grid_bottom = TOP + 7 * PITCH
    height = grid_bottom + 52
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" '
        f'font-family="{FONT}">',
        "<style>"
        ".c{opacity:0;transform-box:fill-box;animation:pop .45s ease-out forwards}"
        "@keyframes pop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        ".f{opacity:0;animation:fade .6s ease-out 1.3s forwards}"
        "@keyframes fade{to{opacity:1}}"
        "</style>",
        f'<rect width="{W}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>',
    ]
    for x, name in month_labels:
        parts.append(f'<text x="{x}" y="{TOP - 10}" font-size="10" fill="#8b949e">{name}</text>')
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{LEFT - 8}" y="{TOP + r * PITCH + 10}" font-size="10" '
                     f'text-anchor="end" fill="#8b949e">{name}</text>')
    parts += cells

    fy = grid_bottom + 28
    summary = (f'{data["total"]:,} contributions in the last year'
               f' | streak {data["current_streak"]}d | longest {data["longest_streak"]}d')
    parts.append(f'<text class="f" x="{LEFT}" y="{fy}" font-size="12" fill="#c9d1d9">{summary}</text>')

    lx = W - 28 - (len(PALETTE) * 17 + 70)
    legend = f'<text x="{lx}" y="{fy}" font-size="10" fill="#8b949e">Less</text>'
    for i, c in enumerate(PALETTE):
        legend += f'<rect x="{lx + 30 + i * 17}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
    legend += f'<text x="{lx + 36 + len(PALETTE) * 17}" y="{fy}" font-size="10" fill="#8b949e">More</text>'
    parts.append(f'<g class="f">{legend}</g>')
    parts.append("</svg>")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Listo: {OUT} ({n_weeks} semanas)")


if __name__ == "__main__":
    main()