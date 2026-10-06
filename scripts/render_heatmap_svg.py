"""Render data/contributions.json as an animated 53-week heatmap SVG."""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 44, 58
WIDTH = 860
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def main():
    data = json.loads(DATA.read_text())
    days = data["days"]
    best = data["best_day"]["count"]

    first = date.fromisoformat(days[0]["date"])
    origin = first - timedelta(days=(first.weekday() + 1) % 7)  # Sunday of first week

    cells, month_labels, seen_months = [], [], set()
    weeks = 0
    for day in days:
        current = date.fromisoformat(day["date"])
        week = (current - origin).days // 7
        row = (current.weekday() + 1) % 7
        weeks = max(weeks, week + 1)
        # GitHub tops out at level 4; promote the single best day to a neon level 5.
        level = 5 if best and day["count"] == best else day["level"]
        x, y = LEFT + week * STEP, TOP + row * STEP
        delay = (week + row) * 0.022
        label = "contribution" if day["count"] == 1 else "contributions"
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{day["count"]} {label} on {day["date"]}</title></rect>'
        )
        key = (current.year, current.month)
        if key not in seen_months and current.day <= 7 and week < 52:
            seen_months.add(key)
            month_labels.append(
                f'<text class="dim" x="{LEFT + week * STEP}" y="{TOP - 10}">{current.strftime("%b")}</text>'
            )

    grid_bottom = TOP + 7 * STEP - GAP
    height = grid_bottom + 62
    grid_right = LEFT + weeks * STEP - GAP

    day_labels = "".join(
        f'<text class="dim" x="{LEFT - 10}" y="{TOP + row * STEP + 10}" text-anchor="end">{name}</text>'
        for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    legend_y = grid_bottom + 18
    legend_x = grid_right - (len(PALETTE) * STEP + 44)
    legend = f'<text class="dim" x="{legend_x - 8}" y="{legend_y + 10}" text-anchor="end">Less</text>'
    legend += "".join(
        f'<rect x="{legend_x + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>'
        for i, color in enumerate(PALETTE)
    )
    legend += f'<text class="dim" x="{legend_x + len(PALETTE) * STEP + 5}" y="{legend_y + 10}">More</text>'

    stats = (
        f'<tspan class="hi">{data["total"]:,}</tspan> contributions in the last year'
        f'  ·  streak <tspan class="hi">{data["current_streak"]}d</tspan>'
        f'  ·  longest <tspan class="hi">{data["longest_streak"]}d</tspan>'
        f'  ·  best day <tspan class="hi">{best}</tspan>'
    )
    end = (weeks + 7) * 0.022 + 0.3

    OUT.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="{data['total']} contributions in the last year">
<style>
text {{ font-family: {FONT}; font-size: 11px; fill: #c9d1d9; }}
.dim {{ fill: #7d8590; }}
.hi {{ fill: #39d353; font-weight: 600; }}
.title {{ font-size: 12px; fill: #7d8590; }}
.c {{ opacity: 0; animation: drop .45s cubic-bezier(.2,.8,.2,1) both; }}
.fade {{ opacity: 0; animation: fade .6s ease-out {end:.2f}s both; }}
@keyframes drop {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@media (prefers-reduced-motion: reduce) {{ .c, .fade {{ animation: none; opacity: 1; }} }}
</style>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="17" r="5" fill="#ff5f56"/><circle cx="34" cy="17" r="5" fill="#ffbd2e"/><circle cx="50" cy="17" r="5" fill="#27c93f"/>
<text class="title" x="{WIDTH / 2}" y="21" text-anchor="middle">contributions.sh — {data['username']}</text>
{''.join(month_labels)}
{day_labels}
{''.join(cells)}
<g class="fade">
{legend}
<text x="{LEFT}" y="{legend_y + 10}" xml:space="preserve">{stats}</text>
</g>
</svg>
"""
    )
    print(f"{len(cells)} cells -> {OUT}")


if __name__ == "__main__":
    main()
