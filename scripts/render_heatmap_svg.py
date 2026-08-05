"""
render_heatmap_svg.py
Reads data/contributions.json and renders an animated contribution
heatmap SVG (53 weeks × 7 days) that reveals itself diagonally on load
then freezes — no looping glow.
Output: contrib-heatmap.svg  (root of the repo)
"""

import json
import math
from pathlib import Path
from datetime import datetime, date, timedelta

DATA_FILE = Path(__file__).parent.parent / "data" / "contributions.json"
OUT_FILE  = Path(__file__).parent.parent / "contrib-heatmap.svg"

# GitHub-ish green palette  none → level-5 neon top
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG      = "#0d1117"
TEXT_FG = "#8b949e"
LABEL   = "#c9d1d9"

CELL    = 11   # px per square
GAP     = 3    # gap between squares
RADIUS  = 2    # border-radius

WEEKS   = 53
DAYS    = 7

LEFT_PAD   = 30   # room for day labels (Mon/Wed/Fri)
TOP_PAD    = 28   # room for month labels
BOT_PAD    = 52   # legend + stats footer
CANVAS_W   = LEFT_PAD + WEEKS * (CELL + GAP) + 16
CANVAS_H   = TOP_PAD  + DAYS  * (CELL + GAP) + BOT_PAD


def level_from_count(count: int, max_count: int) -> int:
    if count == 0:
        return 0
    if max_count == 0:
        return 1
    frac = count / max_count
    if frac < 0.15:
        return 1
    if frac < 0.35:
        return 2
    if frac < 0.60:
        return 3
    if frac < 0.85:
        return 4
    return 5


def build_week_grid(days_data: list[dict]) -> list[list[dict | None]]:
    """Return a list of 53 columns, each a list of 7 day-dicts (or None for padding)."""
    # Index by date string
    by_date = {d["date"]: d for d in days_data}

    # Find the last day in the data (or today)
    if days_data:
        last_date = datetime.strptime(days_data[-1]["date"], "%Y-%m-%d").date()
    else:
        last_date = date.today()

    # Walk back to make last_date the last Sunday (or keep as-is and pad forward)
    # GitHub always ends the graph on the current date's week's Saturday
    end_date = last_date
    # Advance to the next Saturday
    while end_date.weekday() != 5:  # 5 = Saturday
        end_date += timedelta(days=1)

    start_date = end_date - timedelta(weeks=WEEKS) + timedelta(days=1)

    weeks: list[list[dict | None]] = []
    cur = start_date
    while cur <= end_date:
        week: list[dict | None] = []
        for _ in range(DAYS):
            key = cur.isoformat()
            week.append(by_date.get(key, {"date": key, "count": 0, "level": 0}))
            cur += timedelta(days=1)
        weeks.append(week)

    return weeks[:WEEKS]  # trim in case of rounding


def month_labels(weeks):
    """Return list of (col_index, month_abbr) for the first week of each month."""
    labels = []
    prev_month = None
    for wi, week in enumerate(weeks):
        # find first non-None day
        for day in week:
            if day is not None:
                m = day["date"][5:7]
                if m != prev_month:
                    labels.append((wi, datetime.strptime(day["date"], "%Y-%m-%d").strftime("%b")))
                    prev_month = m
                break
    return labels


def render(weeks, stats, max_count):
    parts = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="{CANVAS_W}" height="{CANVAS_H}"
  viewBox="0 0 {CANVAS_W} {CANVAS_H}"
  role="img" aria-label="Contribution heatmap">""")

    # ── Background ─────────────────────────────────────────────────────────
    parts.append(f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" rx="10" fill="{BG}"/>')

    # ── CSS animations ──────────────────────────────────────────────────────
    parts.append("  <style>")
    parts.append("    .cell { opacity: 0; animation: fadeIn 0.25s ease forwards; }")

    # Diagonal stagger: each diagonal d = week + day has the same delay
    # Max diagonals = WEEKS + DAYS - 2
    max_diag = WEEKS + DAYS - 2
    for d in range(max_diag + 1):
        delay = round(d * 0.022, 3)
        parts.append(f"    .d{d} {{ animation-delay: {delay}s; }}")

    parts.append("""    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to   { opacity: 1; transform: translateY(0); }
    }""")
    parts.append("  </style>")

    # ── Month labels ────────────────────────────────────────────────────────
    for wi, abbr in month_labels(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        parts.append(f'  <text x="{x}" y="{TOP_PAD - 6}" font-family="ui-monospace,monospace" '
                     f'font-size="9" fill="{TEXT_FG}">{abbr}</text>')

    # ── Day labels (Mon / Wed / Fri) ────────────────────────────────────────
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for di, lbl in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP_PAD + di * (CELL + GAP) + CELL - 2
        parts.append(f'  <text x="0" y="{y}" font-family="ui-monospace,monospace" '
                     f'font-size="9" fill="{TEXT_FG}">{lbl}</text>')

    # ── Cells ───────────────────────────────────────────────────────────────
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day is None:
                continue
            count  = day["count"]
            level  = day.get("level") or level_from_count(count, max_count)
            color  = PALETTE[min(level, len(PALETTE) - 1)]
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD  + di * (CELL + GAP)
            diag = wi + di
            tooltip = f"{count} contribution{'s' if count != 1 else ''} on {day['date']}"
            parts.append(
                f'  <rect class="cell d{diag}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="{RADIUS}" fill="{color}" data-date="{day["date"]}" data-count="{count}">'
                f'<title>{tooltip}</title></rect>'
            )

    # ── Legend ──────────────────────────────────────────────────────────────
    legend_y = TOP_PAD + DAYS * (CELL + GAP) + 10
    parts.append(f'  <text x="{LEFT_PAD}" y="{legend_y + CELL - 2}" '
                 f'font-family="ui-monospace,monospace" font-size="9" fill="{TEXT_FG}">Less</text>')
    for li, color in enumerate(PALETTE):
        lx = LEFT_PAD + 32 + li * (CELL + GAP)
        parts.append(f'  <rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" '
                     f'rx="{RADIUS}" fill="{color}"/>')
    more_x = LEFT_PAD + 32 + len(PALETTE) * (CELL + GAP) + 4
    parts.append(f'  <text x="{more_x}" y="{legend_y + CELL - 2}" '
                 f'font-family="ui-monospace,monospace" font-size="9" fill="{TEXT_FG}">More</text>')

    # ── Stats footer ────────────────────────────────────────────────────────
    footer_y = legend_y + 22
    total   = stats.get("total", 0)
    cur_str = stats.get("current_streak", 0)
    lng_str = stats.get("longest_streak", 0)
    best    = stats.get("best_day", {})
    best_c  = best.get("count", 0)
    best_d  = best.get("date", "")

    footer_text = (
        f"{total:,} contributions in the last year  •  "
        f"Current streak: {cur_str}d  •  "
        f"Longest: {lng_str}d  •  "
        f"Best day: {best_d} ({best_c})"
    )
    parts.append(f'  <text x="{CANVAS_W // 2}" y="{footer_y}" text-anchor="middle" '
                 f'font-family="ui-monospace,monospace" font-size="9" fill="{TEXT_FG}">'
                 f'{footer_text}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if not DATA_FILE.exists():
        print(f"❌  {DATA_FILE} not found. Run fetch_contributions.py first.")
        return

    payload   = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    days_data = payload.get("days", [])
    stats     = payload.get("stats", {})

    if not days_data:
        print("⚠️  No day data in contributions.json — generating empty grid.")

    max_count = max((d["count"] for d in days_data), default=0)
    weeks     = build_week_grid(days_data)
    svg       = render(weeks, stats, max_count)

    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"[OK] Wrote {OUT_FILE}  ({CANVAS_W}x{CANVAS_H}px)")


if __name__ == "__main__":
    main()
