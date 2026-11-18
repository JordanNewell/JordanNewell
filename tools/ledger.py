#!/usr/bin/env python3
"""Generate the profile's social-preview card + /tag labels (SVG, text outlined to paths).

Palette + type: NEWELL Brand System tokens (brand-system/tokens.json) in a
dark "terminal ledger" remix of jordannewell.com's paper Ledger — OLED black
#0A0A0A canvas, white ink, neon green #00FF41 rule. JetBrains Mono owns
structure, Newsreader owns prose.

Text is converted to SVG paths so the assets render identically everywhere
GitHub can show them (no webfonts inside README images). Fonts are vendored
in tools/fonts (JetBrains Mono + Newsreader, both SIL OFL) so this also
runs in CI — see .github/workflows/refresh-ledger.yml, which re-renders
both assets monthly.

assets/social-preview.png is the GitHub social-share card; it is a rendered
raster of assets/social.svg and needs a headless browser (see workflow).

Usage: python tools/ledger.py  (run from repo root)
"""

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets"

# Fonts are vendored in tools/fonts (copied from jordannewell.com's
# fontsource packages — JetBrains Mono + Newsreader, both OFL) so this
# runs in CI. Local site checkout used as fallback during development.
FONTS = REPO / "tools" / "fonts"
if not FONTS.exists():
    FONTS = Path(r"E:/dev/projects/jordannewell.com/node_modules") / "@fontsource"

# NEWELL Brand System tokens (brand-system/tokens.json) — dark "terminal
# ledger" remix of The Ledger. Backgrounds go OLED black, ink goes white,
# structural rules go neon green (green stays accent-only).
PAPER = "#0A0A0A"   # card background
INK = "#FFFFFF"     # primary type
FG2 = "#A0A0A0"     # secondary type (muted token)
MUTED = "#A0A0A0"
BORDER = "#1F1F1F"  # hairlines between rows
RULE = "#00FF41"    # structural rules (green accent)
GREEN = "#00FF41"   # /tags

W = 1012  # GitHub README content column


class Face:
    """A font face laid out by advance widths (mono needs no kerning; the
    serif lines are short enough that missing GPOS kerning doesn't show)."""

    def __init__(self, path: str, axes: dict | None = None):
        f = TTFont(path)
        if axes and "fvar" in f:
            have = {a.axisTag for a in f["fvar"].axes}
            axes = {k: v for k, v in axes.items() if k in have}
            if axes:
                instantiateVariableFont(f, axes, inplace=True)
        self.font = f
        self.upem = f["head"].unitsPerEm
        self.glyphs = f.getGlyphSet()
        self.cmap = f.getBestCmap()
        self.hmtx = f["hmtx"]

    def line(self, text: str, size: float, tracking: float = 0.0):
        """Return (svg_path_d, width_px) for text on a baseline at y=0,
        y-up flipped (SVG user space)."""
        scale = size / self.upem
        x = 0.0
        parts = []
        for ch in text:
            gname = self.cmap.get(ord(ch), ".notdef")
            pen = SVGPathPen(self.glyphs)
            tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, x, 0))
            self.glyphs[gname].draw(tpen)
            d = pen.getCommands()
            if d:
                parts.append(d)
            x += self.hmtx[gname][0] * scale + tracking
        if text:
            x -= tracking  # no trailing tracking
        return " ".join(parts), x

    def draw(self, text: str, size: float, x: float, y: float,
             fill: str, tracking: float = 0.0, anchor: str = "start") -> str:
        d, w = self.line(text, size, tracking)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        if not d:
            return ""
        return f'<path transform="translate({x:.2f} {y:.2f})" fill="{fill}" d="{d}"/>'


def load_faces():
    if FONTS.name == "fonts":  # vendored layout
        jb = FONTS
        nr = FONTS
    else:  # site node_modules layout
        jb = FONTS / "jetbrains-mono" / "files"
        nr = FONTS.parent / "@fontsource-variable" / "newsreader" / "files"
    return {
        "mono400": Face(jb / "jetbrains-mono-latin-400-normal.woff2"),
        "mono600": Face(jb / "jetbrains-mono-latin-600-normal.woff2"),
        "mono700": Face(jb / "jetbrains-mono-latin-700-normal.woff2"),
        "serif": Face(nr / "newsreader-latin-wght-normal.woff2", axes={"wght": 400, "opsz": 16}),
        "serif-i": Face(nr / "newsreader-latin-standard-italic.woff2", axes={"wght": 400, "opsz": 16}),
    }


def svg(w, h, body, bg=PAPER):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


def label(f, text):
    """/tag section label: green slash, muted lowercase mono, transparent
    background so it sits on GitHub's theme (site's /tag language)."""
    size, tracking, lh = 13, 1.0, 16
    slash_d, slash_w = f["mono400"].line("/", size, tracking)
    rest_d, rest_w = f["mono400"].line(text[1:], size, tracking)
    body = (f'<path transform="translate(0 {lh - 4})" fill="{GREEN}" d="{slash_d}"/>'
            f'<path transform="translate({slash_w:.2f} {lh - 4})" fill="{MUTED}" d="{rest_d}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {slash_w + rest_w:.0f} {lh}" '
            f'width="{slash_w + rest_w:.0f}" height="{lh}">{body}</svg>')


SW, SH = 1280, 640  # GitHub social preview card


def social(f):
    body = []
    m = 72  # page margin
    d, _ = f["mono700"].line("JORDAN NEWELL", 128, tracking=-2.2)
    body.append(f'<path transform="translate({m} 300)" fill="{INK}" d="{d}"/>')
    body.append(f'<rect x="{m}" y="340" width="{SW - 2 * m}" height="3" fill="{RULE}"/>')
    return svg(SW, SH, "".join(body))


def main():
    f = load_faces()
    OUT.mkdir(exist_ok=True)
    (OUT / "social.svg").write_text(social(f))
    for name in ("shipped", "elsewhere"):
        (OUT / f"label-{name}.svg").write_text(label(f, "/" + name))
    print("assets ->", OUT)


if __name__ == "__main__":
    main()
