/* ------------------------------------------------------------------ *
 * THE METHODOLOGY TAB'S LAYOUT INSTRUMENT.
 *
 * `node ui/measure_data.mjs <dir> [label]`, where <dir> holds an index.html
 * with data.js and banner/ beside it.
 *
 * WHY IT EXISTS AT ALL. `ui/measure_map.mjs` measures `#map`. Every layout
 * figure ever quoted about `#data` — including the 17,970 pixels that
 * `UI_METHODOLOGY_DESIGN_START.md` §2 is built on — came from a throwaway probe
 * written inside a block and never committed, which means no later thread could
 * reproduce the number it was being asked to improve. This block is a layout
 * block, and `UI_METHODOLOGY_RESULT.md` §7 is the reason this file is the first
 * commit in it: a layout block without an instrument is a matter of opinion.
 *
 * WHERE THIS RUNS. It needs Playwright and a headless Chromium and is NOT part
 * of `node ui/check_ui.mjs`. The harness is what stops a redesign breaking what
 * is already true; this is what tells you whether the page works, and the two
 * are deliberately different tools. Same division as measure_map.mjs, for the
 * same reason — FINDING 59's shape.
 *
 * WHAT ITS FIGURES ARE WORTH. Headless Chromium on Linux, where this page's
 * serif stack falls back to something the reader will not have. The figures are
 * therefore NOT comparable with a host browser's. They are comparable with each
 * other: the whole point is to be the SAME instrument at a block's open and at
 * its close, so measure your own baseline before scoring anything against a
 * number in a document.
 *
 * AND IT STILL HAS NO OPINION ABOUT WHETHER THE PAGE IS BETTER. The Methodology
 * block passed every figure it set itself and made the tab 13% longer on a
 * phone. Render it, look at it, and put it in front of a person before believing
 * anything printed below.
 *
 * Every figure is read out of the rendered page as an absolute document offset
 * or an element's own bounding box. NONE is computed from another — FINDING 76.
 * In particular the cards are not measured by subtracting one card's top from
 * the next: each reports its own height, and two cards that share a grid row
 * both report the row.
 *
 * THE CARDS ARE NOT NAMED IN THIS FILE. It enumerates whatever `.card` elements
 * the tab renders, in document order, and takes each label from the card's own
 * heading. A block that reorders, renames, splits or merges a card does not have
 * to edit this instrument, and — more to the point — cannot quietly drop one
 * past it.
 * ------------------------------------------------------------------ */
import { chromium } from "playwright";
import path from "node:path";

const dir = path.resolve(process.argv[2] || ".");
const label = process.argv[3] || path.basename(dir);
const url = "file://" + path.join(dir, "index.html");

const WIDTHS = [
  { name: "1600px", width: 1600, height: 900 },
  { name: " 390px", width: 390, height: 844 },
];

/* The content column, i.e. everything on the tab that is NOT the sticky Guide.
 *
 * SCOPING THE ROW COUNTS TO IT IS NOT TIDINESS, IT IS THE DIFFERENCE BETWEEN
 * 117 AND 167. Measured while this instrument was written: a document-wide
 * count of `[data-place]` / `[data-record]` / `[data-edge]` on `#data` reads
 * 65 / 53 / 49, and the extra 31 records and 19 edges are the PERSISTENT SITE
 * HEADER — the brand bar's map thumbnail and the script band, which are on
 * every tab and are not this tab's rows. The Guide adds one more the instant
 * anyone clicks a placement, so a naive count is not merely wrong, it is wrong
 * by a different amount depending on whether the page has been touched.
 *
 * `UI_METHODOLOGY_RESULT.md` §8 records that the last start document's own
 * figure for this was "roughly seventy" against an actual 117. This constant is
 * why the next one will not have to be corrected the same way.
 */
/* THE CONTENT COLUMN, AND IT CHANGED SHAPE ON 2026-09-21. The Guide left this
 * tab, so the column is no longer "the half of `.cols-panel` that is not the
 * rail" — it is the tab's own body. The old selector is kept as a fallback so
 * this instrument reports a number rather than timing out if it is ever pointed
 * at a build from before the change. */
const CONTENT = ".mth-body, .cols.cols-panel > div:not(.rail-right)";

const PROBE = () => {
  const CONTENT = document.querySelector(".mth-body") ? ".mth-body" : ".cols.cols-panel > div:not(.rail-right)";
  const y = sel => {
    const el = document.querySelector(sel);
    if (!el) return null;
    return Math.round(el.getBoundingClientRect().top + window.scrollY);
  };
  const h = sel => {
    const el = document.querySelector(sel);
    return el ? Math.round(el.getBoundingClientRect().height) : null;
  };
  const n = sel => document.querySelectorAll(sel).length;

  /* Each card's own box, and the heading it carries. `placard` records that the
     card is a cell of the two-column `.placards` grid rather than a block in the
     column — at desktop width such a card reports the height of the ROW it
     shares, which is a true statement about the page and a misleading one about
     the card, so it is flagged rather than silently reported. */
  const cards = [...document.querySelectorAll(`${CONTENT} .card`)].map(el => {
    const r = el.getBoundingClientRect();
    const head = el.querySelector("h3");
    return {
      title: head ? head.textContent.trim().replace(/\s+/g, " ") : "(no heading)",
      top: Math.round(r.top + window.scrollY),
      height: Math.round(r.height),
      placard: !!el.closest(".placards"),
    };
  });

  return {
    page:      Math.round(document.documentElement.scrollHeight),
    notice:    y(".hashnotice"),
    /* No Guide on this tab since 2026-09-21. Measured anyway, and expected to
       be null: an instrument that stops looking is an instrument that cannot
       see the panel come back. */
    guide:     y(".rail-right.panel"),
    guideH:    h(".rail-right.panel"),
    guideBody: h("#panel"),
    empty:     !!document.querySelector("#panel .empty"),
    sections:  n(`${CONTENT} section.mth`),
    secnavH:   h(".secnav"),
    evidence:  n(`${CONTENT} details.evidence`),
    placards:  y(".placards"),
    placardsH: h(".placards"),
    cards,
    place:     n(`${CONTENT} [data-place]`),
    record:    n(`${CONTENT} [data-record]`),
    edge:      n(`${CONTENT} [data-edge]`),
  };
};

/* Click the first row of each kind and ask two questions. One: does the address
   bar carry the selection, which is RULING 94 and guard 61 read from the
   outside. Two: HOW TALL IS THE GUIDE THE CLICK LANDS IN — since 2026-09-21 the
   click leaves this tab for ${TABS.map}, so what is measured is the panel the
   reader actually arrives at, and `view` records which tab that was. A click
   that opens nothing reports `clicked: false`, which is the inert-row failure
   this tab's own comment warned about. */
const CLICK_PROBE = kind => {
  const CONTENT = document.querySelector(".mth-body") ? ".mth-body" : ".cols.cols-panel > div:not(.rail-right)";
  const row = document.querySelector(`${CONTENT} [data-${kind}]`);
  if (!row) return { kind, clicked: false };
  row.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  const panel = document.querySelector(".rail-right.panel");
  if (!panel) return { kind, clicked: true, landed: false, hash: location.hash || "(none)" };
  const r = panel.getBoundingClientRect();
  const tab = document.querySelector('.tab[aria-selected="true"]');
  return {
    kind,
    clicked: true,
    landed: true,
    view: tab ? tab.textContent.trim() : "(unknown)",
    hash: location.hash || "(none)",
    guideH: Math.round(r.height),
    overflows: Math.max(0, Math.round(r.height) - window.innerHeight),
    filled: !document.querySelector("#panel .empty"),
    /* Top-level blocks, not rows of any named class. The panel's internals are
       `.sect`, `.chain`, `.rec` and more depending on the kind, and an
       instrument that named them would report 0 the day one is renamed —
       silently, and in the direction that flatters the block. */
    blocks: document.querySelectorAll("#panel > *").length,
  };
};

const browser = await chromium.launch();
const out = [];
for (const w of WIDTHS) {
  const page = await browser.newPage({ viewport: { width: w.width, height: w.height } });
  await page.goto(url + "#data", { waitUntil: "load" });
  await page.waitForSelector(".mth-body, .cols.cols-panel", { timeout: 30000 });
  await page.waitForTimeout(300);
  const m = await page.evaluate(PROBE);
  const clicks = [];
  for (const kind of ["place", "record", "edge"]) {
    /* Each kind gets a clean page: a click leaves the Guide filled and the hash
       set, and the next kind's figures would inherit both. */
    await page.goto(url + "#data", { waitUntil: "load" });
    await page.waitForSelector(".mth-body, .cols.cols-panel", { timeout: 30000 });
    await page.waitForTimeout(200);
    clicks.push(await page.evaluate(CLICK_PROBE, kind));
  }
  out.push({ width: w.name, viewportH: w.height, ...m, clicks });
  await page.close();
}
await browser.close();

const pad = (s, x) => String(s == null ? "—" : s).padStart(x);
const clip = (s, x) => (s.length > x ? s.slice(0, x - 1) + "…" : s).padEnd(x);

console.log(`\n=== METHODOLOGY TAB — ${label} ===`);
console.log("width     page  notice   guide  guideH  panelH   place/record/edge");
for (const r of out)
  console.log(`${r.width} ${pad(r.page, 8)} ${pad(r.notice, 7)} ${pad(r.guide, 7)} `
    + `${pad(r.guideH, 7)} ${pad(r.guideBody, 7)}   ${r.place}/${r.record}/${r.edge}`
    + `  (${r.place + r.record + r.edge} rows, ${r.sections} sections, ${r.evidence} evidence panels,`
    + ` secnav ${r.secnavH}px, guide ${r.guide === null ? "not on this tab" : (r.empty ? "empty" : "FILLED — why?")})`);

for (const r of out) {
  console.log(`\n--- the cards at ${r.width.trim()}, in document order — top / own height ---`);
  for (const [i, c] of r.cards.entries())
    console.log(` ${pad(i + 1, 2)}  ${clip(c.title, 54)} ${pad(c.top, 7)} ${pad(c.height, 7)}`
      + (c.placard ? "  [grid cell — shares its row]" : ""));
  console.log(`     .placards row itself                                   `
    + `${pad(r.placards, 7)} ${pad(r.placardsH, 7)}`);
  const last = r.cards[r.cards.length - 1];
  if (last)
    console.log(`     the last card starts at ${last.top}px, which is `
      + `${(last.top / r.viewportH).toFixed(1)} screens down a ${r.viewportH}px viewport.`);
}

console.log("\nclick the first row of each kind — does the address carry it, "
  + "and how tall does the Guide get?");
for (const r of out) {
  for (const c of r.clicks) {
    if (!c.clicked) { console.log(`${r.width}  ${c.kind.padEnd(6)} NO ROW OF THIS KIND ON THE TAB`); continue; }
    console.log(`${r.width}  ${c.kind.padEnd(6)} ${clip(c.hash, 46)} ${(c.view || "-").padEnd(14)} guide ${pad(c.guideH, 5)}px`
      + ` · ${c.blocks} block(s) · `
      + (c.overflows ? `${c.overflows}px TALLER THAN THE VIEWPORT` : "fits the viewport")
      + (c.filled ? "" : " · PANEL STILL EMPTY"));
  }
}
console.log("");
