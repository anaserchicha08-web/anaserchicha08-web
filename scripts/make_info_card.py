"""
make_info_card.py
Generates an animated neofetch-style terminal info card SVG.
Each line fades + slides in on a stagger, then freezes.
Output: info-card.svg  (root of the repo)
"""

from pathlib import Path

OUT_FILE = Path(__file__).parent.parent / "info-card.svg"

# ── Palette ───────────────────────────────────────────────────────────────
BG      = "#0d1117"
BORDER  = "#30363d"
GREEN   = "#39d353"
CYAN    = "#56d364"
YELLOW  = "#e3b341"
GRAY    = "#8b949e"
WHITE   = "#c9d1d9"
PINK    = "#f78166"
BLUE    = "#58a6ff"

FONT    = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
W       = 460
LINE_H  = 20
PAD_X   = 20
PAD_Y   = 18
TITLE_H = 32  # height of the title bar area

# ── Info lines  (key, value, key_color, val_color) ────────────────────────
INFO_LINES = [
    ("",          "anaserchicha08-web@github",   "",      GREEN),
    ("",          "─" * 30,                      "",      BORDER),
    ("Name",      "Anas Erchicha",               CYAN,    WHITE),
    ("Role",      "Developer & Lifelong Learner", CYAN,    WHITE),
    ("Location",  "Algeria 🇩🇿",                  CYAN,    WHITE),
    ("",          "",                            "",      ""),
    ("Stack",     "Node.js · JS · Python",        YELLOW,  WHITE),
    ("Learning",  "Networking · Cloud · DevOps",  YELLOW,  WHITE),
    ("",          "",                            "",      ""),
    ("Projects",  "Networking Docs Series",       PINK,    WHITE),
    ("GitHub",    "github.com/anaserchicha08-web",PINK,    BLUE),
    ("",          "",                            "",      ""),
    ("OS",        "Windows 11",                  GRAY,    WHITE),
    ("Editor",    "VS Code",                     GRAY,    WHITE),
    ("Shell",     "PowerShell / bash",            GRAY,    WHITE),
]

H = TITLE_H + PAD_Y + len(INFO_LINES) * LINE_H + PAD_Y + 4


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    parts: list[str] = []

    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                 f'role="img" aria-label="neofetch-style info card">')

    # Background
    parts.append(f'  <rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>')

    # Title bar
    parts.append(f'  <rect width="{W}" height="{TITLE_H}" rx="10" fill="#161b22"/>')
    parts.append(f'  <rect y="{TITLE_H - 1}" width="{W}" height="1" fill="{BORDER}"/>')
    # Traffic-light dots
    for xi, col in [(14, "#ff5f57"), (30, "#ffbd2e"), (46, "#28c840")]:
        parts.append(f'  <circle cx="{xi}" cy="{TITLE_H // 2}" r="5" fill="{col}"/>')
    # Window title
    parts.append(f'  <text x="{W // 2}" y="{TITLE_H // 2 + 4}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="11" fill="{GRAY}">anaserchicha08-web — neofetch</text>')

    # CSS animations
    parts.append("  <style>")
    parts.append(f"""    .line {{
      opacity: 0;
      animation: slideIn 0.4s ease forwards;
    }}
    @keyframes slideIn {{
      from {{ opacity: 0; transform: translateX(-8px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}""")
    parts.append("  </style>")

    # Info lines
    for i, (key, val, kc, vc) in enumerate(INFO_LINES):
        y = TITLE_H + PAD_Y + i * LINE_H + LINE_H // 2 + 4
        delay = round(i * 0.07, 2)
        gid = f"line{i}"

        parts.append(f'  <g class="line" id="{gid}" style="animation-delay:{delay}s">')

        if key:
            # key label + value
            key_w = 70
            parts.append(
                f'    <text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="12" fill="{kc}">'
                f'{escape(key)}:</text>'
            )
            parts.append(
                f'    <text x="{PAD_X + key_w}" y="{y}" font-family="{FONT}" font-size="12" fill="{vc}">'
                f'{escape(val)}</text>'
            )
        elif val:
            # full-width line (separator or username line)
            text_fill = vc if vc else WHITE
            parts.append(
                f'    <text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="12" fill="{text_fill}">'
                f'{escape(val)}</text>'
            )
        # empty lines → nothing rendered (just spacing)

        parts.append("  </g>")

    # Color palette row at the bottom
    pal_y = TITLE_H + PAD_Y + len(INFO_LINES) * LINE_H + 6
    colors_block = ["#ff5f57", "#ffbd2e", "#28c840", "#58a6ff", "#bd93f9", "#ff79c6", "#f8f8f2", "#6272a4"]
    for ci, col in enumerate(colors_block):
        cx = PAD_X + ci * 18
        parts.append(f'  <rect x="{cx}" y="{pal_y}" width="14" height="14" rx="3" fill="{col}"/>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = build_svg()
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"[OK] Wrote {OUT_FILE}  ({W}x{H}px)")


if __name__ == "__main__":
    main()
