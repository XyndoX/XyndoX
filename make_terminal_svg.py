"""Render assets/terminal.svg: an animated terminal window with an ASCII wordmark.

The wordmark is rasterised from a real font with Pillow and mapped to block
characters, so it is pixel-accurate (an LLM drawing ASCII art by hand is not).
Run: python3 make_terminal_svg.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORD = "XYNDOX"
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ROWS = 7  # height of the wordmark in text rows

BG, PANEL, INK, MUTED, ORANGE, VIOLET = "#0F1115", "#1B1D22", "#ECEAE3", "#8E939C", "#D97757", "#A78BFA"


def ascii_wordmark(word: str, rows: int) -> list[str]:
    # Draw large, then sample a grid: one text row = 2 pixel rows (half blocks).
    font = ImageFont.truetype(FONT, 200)
    l, t, r, b = font.getbbox(word)
    img = Image.new("L", (r - l + 20, b - t + 20), 0)
    ImageDraw.Draw(img).text((10 - l, 10 - t), word, font=font, fill=255)
    h = rows * 2
    w = round(img.width * h / img.height * 1.1)  # monospace cells are ~2x taller than wide
    small = img.resize((w, h), Image.LANCZOS).point(lambda p: 255 if p > 110 else 0)
    px = small.load()
    out = []
    for y in range(0, h, 2):
        line = ""
        for x in range(w):
            top, bot = px[x, y] > 0, px[x, y + 1] > 0
            line += "█" if top and bot else "▀" if top else "▄" if bot else " "
        out.append(line.rstrip())
    return out


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    art = ascii_wordmark(WORD, ROWS)
    LH, X = 20, 28
    W = max(860, round(2 * X + 9.03 * max(map(len, art))))
    lines = []  # (y, svg tspan content, delay seconds)
    y = 70
    lines.append((y, f'<tspan fill="{ORANGE}">chris@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan>cat banner.txt', 0.2)); y += LH + 6
    for i, row in enumerate(art):
        lines.append((y, f'<tspan fill="{ORANGE}">{esc(row)}</tspan>', 0.6 + i * 0.07)); y += 17.6
    y += 14
    lines.append((y, f'<tspan fill="{ORANGE}">chris@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan>whoami', 1.6)); y += LH + 4
    lines.append((y, "Christian Reinhardt", 2.0)); y += LH
    lines.append((y, f'<tspan fill="{MUTED}">agentic coding · cloud infrastructure · M.Sc. CS (Applied AI) @ TH Rosenheim</tspan>', 2.2)); y += LH + 14
    lines.append((y, f'<tspan fill="{ORANGE}">chris@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{VIOLET}">building --with agents</tspan>', 2.7))
    cursor_y = y
    H = round(y + 34)

    body = "\n".join(
        f'  <text x="{X}" y="{ly}" class="l" style="animation-delay:{d:.2f}s">{c}</text>' for ly, c, d in lines
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: XYNDOX, Christian Reinhardt, agentic coding and cloud infrastructure">
  <style>
    .l {{ font: 15px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; fill: {INK}; white-space: pre; animation: in .35s ease-out backwards; }}
    @keyframes in {{ from {{ opacity: 0; }} }}
    .c {{ animation: blink 1s step-end infinite; animation-delay: 3s; opacity: 0; }}
    @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .l, .c {{ animation: none; opacity: 1; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect width="{W}" height="36" rx="12" fill="{PANEL}"/><rect y="24" width="{W}" height="12" fill="{PANEL}"/>
  <circle cx="22" cy="18" r="6" fill="#FF5F57"/><circle cx="42" cy="18" r="6" fill="#FEBC2E"/><circle cx="62" cy="18" r="6" fill="#28C840"/>
  <text x="{W/2}" y="23" text-anchor="middle" style="font: 13px ui-monospace, Menlo, monospace; fill: {MUTED}">chris@github: ~</text>
{body}
  <rect class="c" x="{X + 9.03 * len("chris@github ~ $ building --with agents") + 4}" y="{cursor_y - 14}" width="9" height="18" fill="{INK}"/>
</svg>
'''


if __name__ == "__main__":
    art = ascii_wordmark(WORD, ROWS)
    assert len(art) == ROWS and max(map(len, art)) > 20, "wordmark rendering failed"
    out = Path(__file__).parent / "assets" / "terminal.svg"
    out.write_text(build(), encoding="utf-8")
    print("\n".join(art))
    print(f"wrote {out}")
