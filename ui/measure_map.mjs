/* ------------------------------------------------------------------ *
 * THE MAP TAB'S LAYOUT INSTRUMENT.
 *
 * `node ui/measure_map.mjs <dir> [label]`, where <dir> holds an index.html
 * with data.js beside it.
 *
 * WHERE THIS RUNS. It needs Playwright and a headless Chromium and is NOT part
 * of `node ui/check_ui.mjs`. The harness is what stops a redesign breaking what
 * is already true; this is what tells you whether the page works, and the two
 * are deliberately different tools. FINDING 59's shape: recorded here rather
 * than half-wired into the gate.
 *
 * WHAT ITS FIGURES ARE WORTH. Headless Chromium on Linux, where this page's
 * serif stack falls back to something the reader will not have. The figures are
 * therefore NOT comparable with a host browser's, and not with
 * UI_QUESTIONS_START.md section 3A's, which were taken on a different
 * instrument. They are comparable with each other: the whole point is to be the
 * SAME instrument at a block's open and at its close, so measure your own
 * baseline before scoring anything against a number in a document.
 *
 * Every figure is read out of the rendered page as an absolute document offset.
 * None is computed from another — FINDING 76.
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

const PROBE = () => {
  const y = sel => {
    const el = document.querySelector(sel);
    if (!el) return null;
    return Math.round(el.getBoundingClientRect().top + window.scrollY);
  };
  const h = sel => {
    const el = document.querySelector(sel);
    return el ? Math.round(el.getBoundingClientRect().height) : null;
  };
  return {
    page:       Math.round(document.documentElement.scrollHeight),
    notice:     y(".notice"),
    map:        y(".maparea"),
    mapH:       h(".maparea"),
    svgH:       h(".mapsvg"),
    // `.panel.guide` on this tab since the Guide became a band above the
    // map; still `.rail-right.panel` on the Questions tab.
    panel:      y(".panel"),
    regiongrid: y(".regiongrid"),
    pins:       document.querySelectorAll(".mapsvg .pin").length,
    extents:    document.querySelectorAll(".mapsvg .extent").length,
  };
};

/* The defect section 3A names, made into a number: click a marker, then ask
   where the thing that answers you is relative to what the visitor can see.
   `hl` is read too — FINDING 106 is that nothing ever applies it. */
const CLICK_PROBE = () => {
  const pin = document.querySelector(".mapsvg .pin");
  if (!pin) return { clicked: false };
  pin.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  const r = document.querySelector(".panel").getBoundingClientRect();
  return {
    clicked: true,
    panelTop: Math.round(r.top),
    below: Math.max(0, Math.round(r.top) - window.innerHeight),
    filled: !document.querySelector("#panel .empty"),
    marked: document.querySelectorAll(".mapsvg .hl").length,
  };
};

const browser = await chromium.launch();
const out = [];
for (const w of WIDTHS) {
  const page = await browser.newPage({ viewport: { width: w.width, height: w.height } });
  await page.goto(url + "#map", { waitUntil: "load" });
  await page.waitForSelector(".mapsvg", { timeout: 30000 });
  await page.waitForTimeout(300);
  const m = await page.evaluate(PROBE);
  const c = await page.evaluate(CLICK_PROBE);
  out.push({ width: w.name, viewportH: w.height, ...m, ...c });
  await page.close();
}
await browser.close();

const pad = (s, n) => String(s == null ? "—" : s).padStart(n);
console.log(`\n=== MAP TAB — ${label} ===`);
console.log("width     page  notice     map    mapH    svgH   panel    grid   pins/ext");
for (const r of out)
  console.log(`${r.width} ${pad(r.page, 8)} ${pad(r.notice, 7)} ${pad(r.map, 7)} `
    + `${pad(r.mapH, 7)} ${pad(r.svgH, 7)} ${pad(r.panel, 7)} ${pad(r.regiongrid, 7)}   ${r.pins}/${r.extents}`);
console.log("\nclick the first marker — where is the panel that answers you?");
for (const r of out)
  console.log(`${r.width}  panel ${pad(r.panelTop, 7)}px down a ${r.viewportH}px viewport · `
    + (r.below ? `${r.below}px BELOW THE FOLD` : "IN VIEW")
    + ` · panel ${r.filled ? "filled" : "STILL EMPTY"}`
    + ` · ${r.marked} thing(s) marked on the map`);
console.log("");
