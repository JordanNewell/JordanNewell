#!/usr/bin/env python3
"""Generate the profile hero (terminal status line + NEWELL wordmark).

Wordmark is outlined from the Newell typeface v0.2+ (tools/fonts/Newell-Black.ttf,
SIL OFL). Two deviations from raw font metrics, both deliberate:

- Layout by ink edges with a constant 185u optical gap — v0.2 Black's advances
  are uneven (E–W/E–L ink gaps 290u vs N–E 179u), reading as "NE WELL".
- The E's bars and the L's bottom bar are overprinted green (OG treatment):
  the glyph is drawn a second time in brand green, clipped to each bar band
  past the stem edge. Rects can't do this — the bar terminals are 45° cut,
  so the green must follow the true outline.

Regenerate after any typeface release bump: python tools/hero.py
"""

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "hero.svg"
SOCIAL = REPO / "assets" / "social.svg"
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
GAP = 185          # uniform inter-letter ink gap (glyph units)
INK_TOP, INK_BOT = 810, -110  # v0.2 cap + overshoot extents
BAR_TIP_FROM = 310  # green starts at the stem's right edge (stem = 90..310u),
                    # so bars read fully green with white stems — the OG treatment


def face():
    f = TTFont(FONT)
    return f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm


def wordmark(gs, cmap, upem, band=(120, 76, 960, 170)):
    BAND_X, BAND_Y, BAND_W, BAND_H = band
    """Lay out NEWELL by ink edges; white glyphs + green bar overlays."""
    inks = {}
    for ch in WORDMARK:
        bp = BoundsPen(gs)
        gs[cmap[ord(ch)]].draw(bp)
        inks[ch] = bp.bounds
    ink_w = sum(inks[c][2] - inks[c][0] for c in WORDMARK)
    total = ink_w + GAP * (len(WORDMARK) - 1)
    s = min(BAND_W / total, BAND_H / (INK_TOP - INK_BOT))  # px per glyph unit
    baseline = BAND_Y + (BAND_H - (INK_TOP - INK_BOT) * s) / 2 + INK_TOP * s
    cursor = BAND_X + (BAND_W - total * s) / 2  # left ink edge, in px

    defs, body = [], []
    for i, ch in enumerate(WORDMARK):
        x0, _, x1, _ = inks[ch]
        ox = cursor - x0 * s  # glyph origin so ink starts at cursor
        pen = SVGPathPen(gs)
        tpen = TransformPen(pen, Transform(s, 0, 0, -s, ox, baseline))
        gs[cmap[ord(ch)]].draw(tpen)
        body.append(f'<path d="{pen.getCommands()}" fill="{INK}"/>')
        if ch in "EL":
            # green overlay: same glyph, clipped to the bar bands past the stem.
            # x runs to x1+50u so the 45° cut terminals stay green to their edge.
            bands = [(-110, 110)] if ch == "L" else [(-110, 110), (240, 460), (590, 810)]
            cid = f"bar-{i}"
            rects = "".join(
                f'<rect x="{ox + BAR_TIP_FROM * s:.2f}" y="{baseline - y1 * s:.2f}" '
                f'width="{(x1 + 50 - BAR_TIP_FROM) * s:.2f}" height="{(y1 - y0) * s:.2f}"/>'
                for y0, y1 in bands
            )
            defs.append(f'<clipPath id="{cid}">{rects}</clipPath>')
            body.append(f'<path d="{pen.getCommands()}" fill="{GREEN}" clip-path="url(#{cid})"/>')
        cursor += (x1 - x0) * s + GAP * s
    return "".join(defs), "".join(body)


def render(W, H, band, top_y, rule_y, bar_y, out_scale=1.0):
    gs, cmap, upem = face()
    defs, mark = wordmark(gs, cmap, upem, band)
    mono = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace"
    m = MARGIN if W == 1200 else 80
    ty = top_y
    body = []
    body.append(
        f'<text x="{m}" y="{ty}" font-family="{mono}" font-size="{16 * out_scale:.0f}" xml:space="preserve">'
        f'<tspan fill="{MUTED}">jordan@newell</tspan><tspan fill="{INK}">:</tspan>'
        f'<tspan fill="{ACCENT}">~</tspan><tspan fill="{INK}">$ </tspan>'
        f'<tspan fill="{GREEN}">status</tspan><tspan fill="{INK}"> {STATUS}</tspan></text>'
    )
    body.append(
        f'<text x="{W - m}" y="{ty}" font-family="{mono}" font-size="{12 * out_scale:.0f}" text-anchor="end">'
        f'<tspan fill="{GREEN}">● </tspan><tspan fill="{MUTED}">live</tspan></text>'
    )
    body.append(f'<line x1="{m}" y1="{rule_y}" x2="{W - m}" y2="{rule_y}" stroke="{BORDER}" stroke-width="1"/>')
    body.append(mark)
    body.append(
        f'<text x="{m}" y="{bar_y}" font-family="{mono}" font-size="{13 * out_scale:.0f}" xml:space="preserve">'
        f'<tspan fill="{GREEN}">[ ok ]</tspan><tspan fill="{MUTED}"> · </tspan>'
        f'<tspan fill="{INK}">fleet</tspan></text>'
    )
    body.append(
        f'<text x="{W - MARGIN}" y="276" font-family="{mono}" font-size="13" text-anchor="end" fill="{MUTED}">et</text>'
    )
    # explicit width/height: dimensionless SVGs render blank in the mobile
    # app's image pipeline (it won't size from viewBox alone)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-label="NEWELL">'
           f'<defs>{defs}</defs>'
           f'<rect width="{W}" height="{H}" fill="#0A0A0A"/>{"".join(body)}</svg>')
    return out


def main():
    OUT.write_text(render(1200, 300, (120, 76, 960, 170), 44, 64, 276), encoding="utf-8")
    print("hero ->", OUT)
    # social card: same design, 1280x640, scaled up ~1.6x
    sc = 1.6
    SOCIAL.write_text(render(1280, 640, (110, 210, 1060, 300), 88, 122, 588, sc), encoding="utf-8")
    print("social ->", SOCIAL)


if __name__ == "__main__":
    main()
