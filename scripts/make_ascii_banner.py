"""
make_ascii_banner.py
Generates an animated ASCII-art text banner spelling out "anaserchicha08"
in large block letters that types itself in left-to-right using SMIL animation.
No external images or libraries needed.
Output: ascii-banner.svg  (root of the repo)
"""

from pathlib import Path

OUT_FILE = Path(__file__).parent.parent / "ascii-banner.svg"

BG      = "#0d1117"
BORDER  = "#30363d"
GREEN   = "#39d353"
GRAY    = "#8b949e"
WHITE   = "#c9d1d9"
FONT    = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
TITLE_H = 32

# ASCII block art for "ANAS" + newline-art "ERCHICHA08"
# Using a compact 5-row block font
ASCII_ART = r"""
 █████╗ ███╗   ██╗ █████╗ ███████╗
██╔══██╗████╗  ██║██╔══██╗██╔════╝
███████║██╔██╗ ██║███████║███████╗
██╔══██║██║╚██╗██║██╔══██║╚════██║
██║  ██║██║ ╚████║██║  ██║███████║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝

███████╗██████╗  ██████╗██╗  ██╗██╗ ██████╗██╗  ██╗ █████╗  ██████╗  █████╗ 
██╔════╝██╔══██╗██╔════╝██║  ██║██║██╔════╝██║  ██║██╔══██╗██╔═████╗██╔══██╗
█████╗  ██████╔╝██║     ███████║██║██║     ███████║███████║██║██╔██║╚█████╔╝
██╔══╝  ██╔══██╗██║     ██╔══██║██║██║     ██╔══██║██╔══██║████╔╝██║██╔══██╗
███████╗██║  ██║╚██████╗██║  ██║██║╚██████╗██║  ██║██║  ██║╚██████╔╝╚█████╔╝
╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚════╝ 
""".strip("\n")

LINES = ASCII_ART.split("\n")
FONT_SIZE = 11
LINE_H = 15
PAD_X = 16
PAD_Y = TITLE_H + 16

# Estimate width from longest line
MAX_LINE = max(len(l) for l in LINES) if LINES else 60
W = max(700, PAD_X * 2 + int(MAX_LINE * FONT_SIZE * 0.60))
H = PAD_Y + len(LINES) * LINE_H + 20


def build_svg() -> str:
    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                 f'role="img" aria-label="ASCII art banner: anaserchicha08">')

    # Background
    parts.append(f'  <rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>')

    # Title bar
    parts.append(f'  <rect width="{W}" height="{TITLE_H}" rx="10" fill="#161b22"/>')
    parts.append(f'  <rect y="{TITLE_H - 1}" width="{W}" height="1" fill="{BORDER}"/>')
    for xi, col in [(14, "#ff5f57"), (30, "#ffbd2e"), (46, "#28c840")]:
        parts.append(f'  <circle cx="{xi}" cy="{TITLE_H // 2}" r="5" fill="{col}"/>')
    parts.append(f'  <text x="{W // 2}" y="{TITLE_H // 2 + 4}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="11" fill="{GRAY}">bash — 80×24</text>')

    # Prompt line before the banner
    prompt_y = TITLE_H + 14
    parts.append(f'  <text x="{PAD_X}" y="{prompt_y}" font-family="{FONT}" font-size="11">')
    parts.append(f'    <tspan fill="{GREEN}">anaserchicha08@github</tspan>')
    parts.append(f'    <tspan fill="{WHITE}">:~$ </tspan>')
    parts.append(f'    <tspan fill="{WHITE}">figlet anaserchicha08</tspan>')
    parts.append(f'  </text>')

    # CSS for the typing reveal + blinking cursor
    parts.append("  <style>")
    parts.append(f"""    .banner-line {{
      opacity: 0;
      animation: typeLine 0.18s steps(1) forwards;
    }}
    @keyframes typeLine {{
      from {{ opacity: 0; }}
      to   {{ opacity: 1; }}
    }}
    .cursor {{
      animation: blink 0.8s step-start 0s 6 forwards;
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50%       {{ opacity: 0; }}
    }}""")
    parts.append("  </style>")

    # Render each line with staggered delay
    total_delay = 0.0
    for i, line in enumerate(LINES):
        y = PAD_Y + i * LINE_H
        delay = round(i * 0.12, 2)
        total_delay = delay + 0.18
        # Alternate green shades for visual interest
        fill = GREEN if (i % 7 < 3) else "#56d364" if (i % 7 < 6) else "#69f0a0"
        parts.append(
            f'  <text class="banner-line" x="{PAD_X}" y="{y + LINE_H - 3}" '
            f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{fill}" '
            f'style="animation-delay:{delay}s" xml:space="preserve">'
            f'{line}</text>'
        )

    # Blinking cursor after last line
    cursor_y = PAD_Y + len(LINES) * LINE_H + LINE_H - 3
    cursor_delay = round(total_delay, 2)
    parts.append(
        f'  <text class="cursor" x="{PAD_X}" y="{cursor_y}" '
        f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{GREEN}" '
        f'style="animation-delay:{cursor_delay}s">█</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = build_svg()
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"[OK] Wrote {OUT_FILE}  ({W}x{H}px)")


if __name__ == "__main__":
    main()
