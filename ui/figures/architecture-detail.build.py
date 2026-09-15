#!/usr/bin/env python3
"""Generator for the detailed architecture figure (Methodology section 10).

Every coordinate below is computed, not typed, because the first figure in this
pair needed two rounds of hand-fixing for collisions that arithmetic would have
prevented.

THREE ROUTING CONSTRAINTS the layout is built around, each one a collision the
first draft of this file actually had:
  1. The gateway band's right edge stops short of the viewBox so the return
     channel from `Stored answers` can run down the right margin OUTSIDE it.
  2. The publish row is inset from the left margin so the feed from
     `Source records` can run down the left margin outside it AND clear the
     zone eyebrow, which is 370-odd pixels of uppercase text at x=16.
  3. The two long connectors run at different heights (y=340 return, left
     margin feed) so they never cross each other or the down-arrows into the
     gateway.
"""
import html
import pathlib

W = 1240
# Emitted next to this script, wherever it sits, so regenerating works from a
# clone without editing a path first.
OUT = str(pathlib.Path(__file__).resolve().parent / "architecture-detail.html")

parts = []
def add(s): parts.append("  " + s)

def box(x, y, w, h, cls="af-box"):
    add(f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/></g>')

def txt(x, y, cls, s):
    add(f'<text x="{x}" y="{y}" class="{cls}">{html.escape(s)}</text>')

def line(x1, y1, x2, y2):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="af-line" marker-end="url(#ad-arrow)"/>')

def path(d):
    add(f'<path d="{d}" class="af-line" marker-end="url(#ad-arrow)"/>')

def eyebrow(x, y, s):
    txt(x, y, "af-eyebrow", s)

def titled(cx, top, title, subs, gap=20, lead=15):
    txt(cx, top, "af-title", title)
    for i, s in enumerate(subs):
        txt(cx, top + gap + i * lead, "af-sub", s)

# ---------------------------------------------------------------- zone 1
# Six boxes across the full width. The build pipeline, left to right.
Z1_Y, Z1_H, BW, GAP = 36, 92, 182, 24
X0 = 16
pipeline = [
    ("Source records", ["one file per source:", "text, translation,", "citations, reuse terms"]),
    ("Passages",       ["split at the source's own", "boundaries; character", "positions recorded"]),
    ("Embeddings",     ["each passage as 1,024", "numbers standing for", "its meaning"]),
    ("PostgreSQL 16",  ["with pgvector.", "vector(1024), searched", "by cosine distance"]),
    ("Retrieval and answer", ["nearest passages found,", "answer written with a", "citation on every claim"]),
    ("Stored answers", ["every run kept, whether", "it passed its checks", "or failed them"]),
]
xs = [X0 + i * (BW + GAP) for i in range(6)]
assert xs[-1] + BW <= W - 12, xs[-1] + BW

eyebrow(X0, 22, "Build pipeline — Python, run once, before the site is published")
for x, (title, subs) in zip(xs, pipeline):
    box(x, Z1_Y, BW, Z1_H)
    titled(x + BW // 2, Z1_Y + 24, title, subs)
for x in xs[:-1]:
    line(x + BW + 4, Z1_Y + 46, x + BW + GAP - 10, Z1_Y + 46)

CX = {name: x + BW // 2 for x, (name, _) in zip(xs, pipeline)}
BOT = Z1_Y + Z1_H          # 128

# ---------------------------------------------------------------- zone 2
# The gateway band. Its right edge is deliberately short of the pipeline's so
# the return channel has somewhere to run; see constraint 1 in the docstring.
GX, GY, GH = 428, 196, 116
GW = 752                          # 428..1180, leaving 1180..1240 as channel
CHIPS = [
    ("voyage-3.5",       "embeddings, 1,024-d"),
    ("rerank-2.5",       "re-scoring results"),
    ("claude-haiku-4-5", "answers, translation"),
    ("claude-sonnet-5",  "second tier, on request"),
]
box(GX, GY, GW, GH, "af-box af-box-live")
txt(GX + GW // 2, GY + 26, "af-title", "Every model call goes through one gateway (LiteLLM)")

PAD, CGAP, CH = 14, 10, 60
CW = (GW - 2 * PAD - 3 * CGAP) // 4
cy = GY + 40
for i, (mono, sub) in enumerate(CHIPS):
    cx = GX + PAD + i * (CW + CGAP)
    add(f'<rect x="{cx}" y="{cy}" width="{CW}" height="{CH}" rx="2" class="af-chip"/>')
    txt(cx + CW // 2, cy + 22, "af-mono", mono)
    txt(cx + CW // 2, cy + 40, "af-sub", sub)
assert GX + PAD + 3 * (CW + CGAP) + CW <= GX + GW - PAD + 1

line(CX["Embeddings"], BOT + 4, CX["Embeddings"], GY - 8)
txt(CX["Embeddings"] + 10, 174, "af-note af-start", "embed each passage")
line(CX["Retrieval and answer"], BOT + 4, CX["Retrieval and answer"], GY - 8)
txt(CX["Retrieval and answer"] - 10, 174, "af-note af-end", "write the answer")

# ---------------------------------------------------------------- zone 3
# Publish chain, inset from the left margin; see constraint 2.
PX0, PW, PY, PH, PGAP = 68, 260, 388, 88, 56
publish = [
    ("build_ui_data.py",  ["joins stored answers to", "source records"]),
    ("data.js + manifest", ["one generated bundle,", "never hand-edited"]),
    ("index.html",        ["one hand-written file;", "no framework or build step"]),
]
pxs = [PX0 + i * (PW + PGAP) for i in range(3)]
eyebrow(PX0, PY - 14, "Published site — static files, no server, no database")
for x, (title, subs) in zip(pxs, publish):
    box(x, PY, PW, PH)
    titled(x + PW // 2, PY + 26, title, subs, gap=22, lead=15)
for x in pxs[:-1]:
    line(x + PW + 4, PY + 44, x + PW + PGAP - 8, PY + 44)

PCX = {name: x + PW // 2 for x, (name, _) in zip(pxs, publish)}

# BOTH feeds into build_ui_data.py arrive along the LEFT MARGIN, in two lanes,
# and enter the box through its left edge at different heights.
#
# The obvious routing — bring the right-hand feed straight down into the top of
# the box — was drawn, rendered, and caught by the collision check: the descent
# ran through the zone eyebrow, which is ~370px of uppercase text starting at
# the box's own left edge, so NO descent x inside that box is clear. Entering
# through the left edge is the fix, and putting both feeds there is what keeps
# them from crossing: lane A never travels right of LANE_A, and the long
# horizontal run never travels left of LANE_B.
LANE_A, LANE_B = 24, 44
ENTRY_A, ENTRY_B = PY + 30, PY + 58
RUN = 340

path(f"M {LANE_A} {BOT + 4} L {LANE_A} {ENTRY_A} L {PX0 - 8} {ENTRY_A}")
txt(LANE_A + 10, 250, "af-note af-start", "text, translations, citations")

assert 1210 > GX + GW, "return channel would cross the gateway band"
assert GY + GH < RUN < PY - 14 - 12, "return run would cross a band or a label"
assert LANE_B > LANE_A, "the two feeds would cross in the margin"
path(f"M 1210 {BOT + 4} L 1210 {RUN} L {LANE_B} {RUN} "
     f"L {LANE_B} {ENTRY_B} L {PX0 - 8} {ENTRY_B}")
txt(1200, RUN - 8, "af-note af-end", "stored answers and their citations")

# ---------------------------------------------------------------- zone 4
KY = 560
KX, KW, KH = 16, W - 32, 104
checks = [
    ("The page's own code is executed",
     ["every stored answer rendered, and what",
      "appears compared with the data it describes"]),
    ("Defects introduced deliberately",
     ["the check meant to catch each one is",
      "confirmed to fail before it is trusted"]),
    ("Layout measured in a headless browser",
     ["Playwright with Chromium; one script runs",
      "every suite and prints the results"]),
]
eyebrow(KX, KY - 14, "Checks — run against the reference copy, not the published one")
box(KX, KY, KW, KH)
KPAD, KGAP = 14, 10
KCW = (KW - 2 * KPAD - 2 * KGAP) // 3
for i, (head, subs) in enumerate(checks):
    cx = KX + KPAD + i * (KCW + KGAP)
    add(f'<rect x="{cx}" y="{KY + KPAD}" width="{KCW}" height="{KH - 2 * KPAD}" rx="2" class="af-chip"/>')
    txt(cx + KCW // 2, KY + KPAD + 26, "af-chip-title", head)
    for j, s in enumerate(subs):
        txt(cx + KCW // 2, KY + KPAD + 46 + j * 15, "af-sub", s)

# The descent leaves data.js off-centre, near the box's right end, for the same
# reason the return feed leaves Stored answers off-centre: the zone eyebrow
# beneath it is 490px of uppercase text and a centred descent cleared its last
# word by eight pixels. Measured, not guessed — the collision check passes at
# both positions and only the render shows how tight the first one looked.
DESCENT = pxs[1] + PW - 24
line(DESCENT, PY + PH + 4, DESCENT, KY - 8)
txt(DESCENT + 10, 502, "af-note af-start", "the same bundle the site loads")

H = KY + KH + 16

ALT = ("Detailed architecture. A Python build pipeline turns source records into passages, "
       "embeddings and a searchable database, retrieves passages and writes answers, and "
       "stores every run. All model calls pass through a single gateway serving two Voyage "
       "models and two Anthropic models. A generator joins stored answers to source records "
       "into one data bundle, which a single hand-written HTML file loads with no server. "
       "Checks execute the page's own code, introduce defects deliberately, and measure "
       "layout in a headless browser.")

HEAD = '''<!-- =====================================================================
     THE DETAILED ARCHITECTURE FIGURE — Methodology section 10.

     The companion to the figure in section 1. That one makes one argument and
     omits everything that does not serve it. This one is the inventory: what
     the thing is actually built out of, named in the terms section 10 uses.

     GENERATED, NOT HAND-DRAWN. Every coordinate comes from
     scratchpad/mkarch2.py, which carries the routing constraints as asserts.
     Editing the numbers here by hand will hold until the next regeneration and
     no longer.

     NO NEW COLOURS, NO SCRIPT, NO IMAGE, NO EXTERNAL REFERENCE. Same token set
     as the first figure, so a palette change — including the dark scheme —
     reaches it without an edit here.

     ITS OWN MARKER ID. `ad-arrow`, not `af-arrow`: both figures can appear on
     one page and an SVG marker resolves by id across the whole document.

     THE SCROLL WRAPPER IS LOAD-BEARING and its min-width is larger than the
     first figure's, because the viewBox is wider and the type would otherwise
     land under 9px on a phone.
     ===================================================================== -->

<!-- ---------- 1. CSS: add to the stylesheet in ui/index.html, after the
                    .archfig rules the first figure introduced ---------- -->
<style>
  .archfig-detail svg      { min-width: 1100px; }

  .archfig .af-chip        { fill: var(--paper); stroke: var(--line); stroke-width: 1; }
  .archfig .af-mono        { font-family: var(--font-mono); font-size: var(--t-s, 13px);
                             fill: var(--ink); text-anchor: middle; }
  .archfig .af-chip-title  { font-family: var(--font-sans); font-size: var(--t-xs, 11.5px);
                             font-weight: 600; fill: var(--ink); text-anchor: middle; }
</style>

<!-- ---------- 2. MARKUP ---------- -->
'''

svg = [f'<figure class="archfig archfig-detail">', '<div class="af-scroll">',
       f'<svg viewBox="0 0 {W} {H}" role="img"', f'     aria-label="{html.escape(ALT)}">',
       '  <defs>',
       '    <marker id="ad-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"',
       '            orient="auto-start-reverse">',
       '      <path d="M0,0 L10,5 L0,10 z" fill="var(--ink-faint, #8a857c)"/>',
       '    </marker>',
       '  </defs>']
svg += parts
svg += ['</svg>', '</div>',
        '<figcaption>Every model call passes through one gateway. The published site is two',
        'static files — a generated data bundle and one hand-written page — with no server',
        'and no database behind it.</figcaption>',
        '</figure>', '']

open(OUT, "w", encoding="utf-8", newline="\n").write(HEAD + "\n".join(svg))
print(f"wrote {OUT}  viewBox 0 0 {W} {H}  chip {CW}  kchip {KCW}")
