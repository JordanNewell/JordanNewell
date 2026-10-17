#!/usr/bin/env python3
"""Generate the profile's ledger assets (SVG, text outlined to paths).

Palette + type: NEWELL Brand System tokens (brand-system/tokens.json) in a
dark "terminal ledger" remix of jordannewell.com's paper Ledger — OLED black
#0A0A0A cards, white ink, #1F1F1F hairlines, neon green #00FF41 rules and
tags. JetBrains Mono owns structure, Newsreader owns prose.

Text is converted to SVG paths so the assets render identically everywhere
GitHub can show them (no webfonts inside README images). Fonts are vendored
in tools/fonts (JetBrains Mono + Newsreader, both SIL OFL) so this also
runs in CI — see .github/workflows/refresh-ledger.yml, which re-renders
everything monthly so the masthead dateline stays current.

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


def hairline(y, x=0, w=W, color=BORDER):
    return f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="{color}"/>'


def masthead(f, today):
    body = []
    body.append(f["mono400"].draw("REGISTER OF PUBLIC WORK · UPDATED " + today,
                                  12.5, 0, 26, MUTED, tracking=1.6))
    d, w = f["mono700"].line("JORDAN NEWELL", 72, tracking=-1.4)
    body.append(f'<path transform="translate(0 118)" fill="{INK}" d="{d}"/>')
    body.append(f'<rect x="0" y="136" width="{W}" height="2" fill="{RULE}"/>')
    body.append(f["serif-i"].draw("Field notes from an operator shipping in public across sectors.",
                                  22, 0, 180, FG2))
    body.append(f["mono400"].draw("One thing gets the attention. Everything else runs quiet.",
                                  13.5, 0, 214, MUTED))
    return svg(W, 238, "".join(body))


def register_head(f):
    body = f["mono400"].draw("SHIPPED", 12.5, 0, 22, MUTED, tracking=1.6)
    body += f'<rect x="0" y="38" width="{W}" height="2" fill="{RULE}"/>'
    return svg(W, 40, body)


ROWS = [
    ("01", "curtis", "The agent for Obsidian — 53 providers, local-first, everything on the record.", "/agent", "https://github.com/JordanNewell/curtis"),
    ("02", "dot_curt", "A single-file conversation format machines can verify.", "/standard", "https://github.com/JordanNewell/dot_curt"),
    ("03", "curtis-ai-porter", "AI chat history in, .curt and markdown out — nothing leaves your machine.", "/portable", "https://github.com/JordanNewell/curtis-ai-porter"),
    ("04", "curtis-ai-audit", "Append-only receipts for everything your agent touches.", "/receipts", "https://github.com/JordanNewell/curtis-ai-audit"),
    ("05", "token-hunt", "Catch secrets at chat time, not commit time.", "/security", "https://github.com/JordanNewell/token-hunt"),
    ("06", "pat-scanner", "Thirteen credential classes blocked before they reach the transcript.", "/security", "https://github.com/JordanNewell/pat-scanner"),
    ("07", "curtis-compliance", "Fintech compliance checks with a hash-chained audit trail.", "/fintech", "https://github.com/JordanNewell/curtis-compliance"),
    ("08", "newell-typeface", "A geometric display face built from rails and 45-degree diagonals.", "/typeface", "https://github.com/JordanNewell/newell-typeface"),
]

ROW_H = 92


def row(f, idx, name, desc, tag):
    body = []
    body.append(f["mono400"].draw(idx, 12.5, 0, 38, MUTED, tracking=1.2))
    body.append(f["mono600"].draw(name, 17.5, 120, 38, INK))
    # tag right-aligned on the title line, green like the site's /tags
    body.append(f["mono400"].draw(tag, 12.5, W - 24, 37, GREEN, anchor="end"))
    body.append(f["serif"].draw(desc, 16, 120, 66, MUTED))
    body.append(hairline(ROW_H - 1))
    return svg(W, ROW_H, "".join(body))


def figures(f):
    items = [("53", "AI PROVIDERS WIRED"), ("17", "FLEET AGENTS"), ("13", "PAT CLASSES BLOCKED")]
    body = [hairline(0)]
    col_w = W / 3
    for i, (num, cap) in enumerate(items):
        x = i * col_w
        body.append(f["mono700"].draw(num, 48, x, 66, INK))
        body.append(f["mono400"].draw(cap, 11, x, 92, MUTED, tracking=1.5))
    body.append(hairline(118))
    return svg(W, 120, "".join(body))


def rule_svg():
    return svg(W, 2, f'<rect width="{W}" height="1" fill="{BORDER}"/>')


SW, SH = 1280, 640  # GitHub social preview card


def social(f, today):
    body = []
    m = 72  # page margin
    body.append(f["mono400"].draw("REGISTER OF PUBLIC WORK · " + today,
                                  15, m, 92, MUTED, tracking=2.0))
    d, _ = f["mono700"].line("JORDAN NEWELL", 128, tracking=-2.2)
    body.append(f'<path transform="translate({m} 268)" fill="{INK}" d="{d}"/>')
    body.append(f'<rect x="{m}" y="308" width="{SW - 2 * m}" height="3" fill="{RULE}"/>')
    body.append(f["serif-i"].draw("Field notes from an operator shipping in public across sectors.",
                                  30, m, 376, FG2))
    body.append(f["mono400"].draw("One thing gets the attention. Everything else runs quiet.",
                                  16, m, 418, MUTED))
    # figures strip pinned to the bottom
    body.append(hairline(SH - 150, x=m, w=SW - 2 * m))
    items = [("53", "AI PROVIDERS WIRED"), ("17", "FLEET AGENTS"), ("13", "PAT CLASSES BLOCKED")]
    col_w = (SW - 2 * m) / 3
    for i, (num, cap) in enumerate(items):
        x = m + i * col_w
        body.append(f["mono700"].draw(num, 44, x, SH - 88, INK))
        body.append(f["mono400"].draw(cap, 11.5, x, SH - 60, MUTED, tracking=1.5))
    return svg(SW, SH, "".join(body))


def main():
    import datetime
    f = load_faces()
    OUT.mkdir(exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")
    (OUT / "masthead.svg").write_text(masthead(f, today))
    (OUT / "register-head.svg").write_text(register_head(f))
    for i, (idx, name, desc, tag, _) in enumerate(ROWS, 1):
        (OUT / f"row-{i:02d}.svg").write_text(row(f, idx, name, desc, tag))
    (OUT / "figures.svg").write_text(figures(f))
    (OUT / "rule.svg").write_text(rule_svg())
    (OUT / "social.svg").write_text(social(f, today))
    # width report for overflow QC
    for idx, name, desc, tag, _ in ROWS:
        _, tw = f["mono600"].line(name, 17.5)
        _, dw = f["serif"].line(desc, 16)
        _, gw = f["mono400"].line(tag, 12.5)
        status = "OK " if 120 + max(tw, dw) < W - gw - 24 else "TIGHT"
        print(f"{status} {name:<20} desc {dw:5.0f}px  title {tw:5.0f}px  tag {gw:4.0f}px")
    print("assets ->", OUT)


if __name__ == "__main__":
    main()
