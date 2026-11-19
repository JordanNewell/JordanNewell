#!/usr/bin/env python3
"""Generate the profile hero (terminal status line + NEWELL wordmark).

Wordmark is outlined from the Newell typeface v0.2+ (tools/fonts/Newell-Black.ttf,
SIL OFL) with proper advances — the v0.1-era banner had the W's ink leaning
into the E's space (fixed in the v0.2 regrid). Regenerate after any typeface
release bump: python tools/hero.py
"""

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "hero.svg"
FONT = REPO / "tools" / "fonts" / "Newell-Black.ttf"

W, H = 1200, 300
MARGIN = 40
INK = "#FFFFFF"
MUTED = "#A0A0A0"
ACCENT = "#1AFF72"
GREEN = "#00FF41"
BORDER = "#1F1F1F"

STATUS = "--role=engineer"
WORDMARK = "NEWELL"
BAND_X, BAND_Y, BAND_W, BAND_H = 120, 76, 960, 170  # wordmark fit box


def face():
    f = TTFont(FONT)
    return f, f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm


def wordmark_paths(gs, cmap, hmtx, upem, size):
    """Outlined NEWELL, laid out by INK edges with a constant optical gap.

    v0.2 Black's advances are uneven (N–E ink gap 179u vs 290u around W/L),
    which reads as "NE WELL" — so instead of advances we place each glyph's
    ink edge at cursor + GAP. Green bar offsets are relative to glyph origin,
    which we derive per glyph from its ink left edge."""
    from fontTools.pens.boundsPen import BoundsPen
    scale = size / upem
    GAP = 185  # uniform inter-letter ink gap (glyph units)
    inks = {}
    for ch in WORDMARK:
        bp = BoundsPen(gs)
        gs[cmap[ord(ch)]].draw(bp)
        inks[ch] = bp.bounds  # (x0, y0, x1, y1) — rectilinear glyphs, exact
    ink_w = sum(inks[c][2] - inks[c][0] for c in WORDMARK)
    total = ink_w + GAP * (len(WORDMARK) - 1)
    ink_top, ink_bot = 810, -110  # v0.2 cap + overshoot extents
    s = min(BAND_W / total, BAND_H / ((ink_top - ink_bot) * scale)) * scale
    baseline = BAND_Y + (BAND_H - (ink_top - ink_bot) * s) / 2 + ink_top * s
    x = BAND_X + (BAND_W - total * s) / 2  # cursor = left ink edge
    parts = []
    for ch in WORDMARK:
        x0, _, x1, _ = inks[ch]
        ox = x - x0 * s  # glyph origin so ink starts at cursor
        pen = SVGPathPen(gs)
        tpen = TransformPen(pen, Transform(s, 0, 0, -s, ox, baseline))
        gs[cmap[ord(ch)]].draw(tpen)
        parts.append(f'<path d="{pen.getCommands()}" fill="{INK}"/>')
        if ch == "E":
            # OG treatment: the E's three bars as green blocks
            # v0.2 Black bar geometry: x 90..475, bars y -110..110 / 240..460 / 590..810
            bx = ox + 200 * s
            bw = 275 * s
            for y0, y1 in ((-110, 110), (240, 460), (590, 810)):
                ry = baseline - y1 * s
                parts.append(f'<rect x="{bx:.2f}" y="{ry:.2f}" width="{bw:.2f}" '
                             f'height="{(y1 - y0) * s:.2f}" fill="{GREEN}"/>')
        if ch == "L":
            # L bottom bar green, matching the E treatment (bar = y -110..110)
            bx = ox + 200 * s
            parts.append(f'<rect x="{bx:.2f}" y="{baseline - 110 * s:.2f}" width="{275 * s:.2f}" '
                         f'height="{220 * s:.2f}" fill="{GREEN}"/>')
        x += (x1 - x0) * s + GAP * s
    return "".join(parts)


def main():
    f, gs, cmap, hmtx, upem = face()
    body = []
    # terminal status line
    body.append(
        f'<text x="{MARGIN}" y="44" font-family="\'JetBrains Mono\',\'Fira Code\',\'Cascadia Code\',ui-monospace,monospace" font-size="16" xml:space="preserve">'
        f'<tspan fill="{MUTED}">jordan@newell</tspan><tspan fill="{INK}">:</tspan>'
        f'<tspan fill="{ACCENT}">~</tspan><tspan fill="{INK}">$ </tspan>'
        f'<tspan fill="{GREEN}">status</tspan><tspan fill="{INK}"> {STATUS}</tspan></text>'
    )
    body.append(
        f'<text x="{W - MARGIN}" y="44" font-family="\'JetBrains Mono\',\'Fira Code\',\'Cascadia Code\',ui-monospace,monospace" font-size="12" text-anchor="end">'
        f'<tspan fill="{GREEN}">● </tspan><tspan fill="{MUTED}">live</tspan></text>'
    )
    body.append(f'<line x1="{MARGIN}" y1="64" x2="{W - MARGIN}" y2="64" stroke="{BORDER}" stroke-width="1"/>')
    body.append(wordmark_paths(gs, cmap, hmtx, upem, 1000))
    # status bar — real facts only (the v0.1 bar carried fabricated
    # commits/uptime numbers; those don't go back on)
    mono = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace"
    body.append(
        f'<text x="{MARGIN}" y="276" font-family="{mono}" font-size="13" xml:space="preserve">'
        f'<tspan fill="{GREEN}">[ ok ]</tspan><tspan fill="{MUTED}"> · </tspan>'
        f'<tspan fill="{INK}">fleet</tspan></text>'
    )
    body.append(
        f'<text x="{W - MARGIN}" y="276" font-family="{mono}" font-size="13" text-anchor="end" fill="{MUTED}">new york · et</text>'
    )
    OUT.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="NEWELL">'
        f'<rect width="{W}" height="{H}" fill="#0A0A0A"/>{"".join(body)}</svg>',
        encoding="utf-8",
    )
    print("hero ->", OUT)


if __name__ == "__main__":
    main()
