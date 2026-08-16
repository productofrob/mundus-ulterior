/*
 * Part 9 smoke test: run the page's own rendering functions over every archived
 * run, headlessly.
 *
 *     node ui/check_ui.mjs
 *
 * Deliberately small. The Part 9 brief warned that four parts running ended
 * with a larger offline suite than deliverable, so this checks three things and
 * stops: that the page's script parses, that rendering every run throws
 * nothing, and that the claims the UI makes on screen are true of the data.
 *
 * The interesting one is the third. A provenance viewer that renders smoothly
 * while quietly dropping a citation is worse than one that crashes, so the
 * check asserts that every quotation the answer text contains is actually
 * highlighted, and that every citation marker resolves to a source card.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const UI = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(UI);
const fail = [];
const note = (ok, msg) => { console.log(`  ${ok ? "ok  " : "FAIL"}  ${msg}`);
                            if (!ok) fail.push(msg); };

/* ---- 0. the bundle is not older than the evidence ----
 *
 * Added 2026-08-12, Phase 2 Block 0. This file reported "all checks passed"
 * over 61 runs and 139 spans while the archive held 77 and 168: data.js was
 * built at 09:02 and the exit-gate session ran at 13:36. Every assertion below
 * was true of the bundle and none of them was true of the project.
 *
 * A checker that validates whatever it is handed will certify a stale artefact
 * without complaint. README.md already carried the instruction — "run the
 * builder after any corpus edit" — and an instruction is not a guard.
 *
 * This runs FIRST and hard-fails, because every count printed after it is
 * meaningless if the bundle is behind.
 */
{
  const bundleAge = statSync(join(UI, "data.js")).mtimeMs;
  const newer = [];
  for (const dir of ["eval/answer_runs", "data/seed_corpus"]) {
    const walk = (d) => {
      for (const entry of readdirSync(d, { withFileTypes: true })) {
        const p = join(d, entry.name);
        if (entry.isDirectory()) walk(p);
        else if (entry.name.endsWith(".json") &&
                 statSync(p).mtimeMs > bundleAge) newer.push(p);
      }
    };
    try { walk(join(ROOT, dir)); } catch { /* directory absent is not this check's business */ }
  }
  note(
    newer.length === 0,
    newer.length === 0
      ? "ui/data.js is at least as new as every archived run and seed record"
      : `ui/data.js is STALE — ${newer.length} file(s) changed after it was ` +
        `built (e.g. ${newer.slice(0, 3).map(p => p.replace(ROOT + "/", "")).join(", ")}). ` +
        `Run: python ui/build_ui_data.py`,
  );
  if (newer.length) {
    console.log("\nStopping: every count below would describe a bundle that is behind the evidence.");
    process.exit(1);
  }
}

/* ---- 1. the page parses, and its data loads ---- */
const html = readFileSync(join(UI, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map(m => m[1]);
note(scripts.length === 1, `index.html has exactly one inline script (found ${scripts.length})`);

const dataJs = readFileSync(join(UI, "data.js"), "utf8");

// A DOM thin enough to let the page's top-level code run to completion.
const el = () => ({ innerHTML: "", scrollTop: 0, dataset: {},
                    setAttribute() {}, closest: () => null });
const sandbox = {
  console,
  window: {},
  document: {
    getElementById: el, querySelectorAll: () => [], addEventListener() {},
    createElement: el,
  },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

try {
  vm.runInContext(dataJs, sandbox, { filename: "data.js" });
  note(true, "data.js parses");
} catch (e) { note(false, `data.js failed to parse: ${e.message}`); }

try {
  vm.runInContext(
    scripts[0] +
    "\n;globalThis.__api = { D, P, byQuestion, QUESTIONS, state, renderAnswerText," +
    " renderQuoteProvenance, renderPassageProvenance, renderRecordProvenance," +
    " renderPlaceProvenance, renderGroupProvenance, renderEdgeProvenance," +
    " buildMap, mapState, mapWindow, mapBase, viewQuestions, viewPlaces, viewAbout };",
    sandbox, { filename: "index.html<script>" });
  note(true, "the page's script parses and runs to completion");
} catch (e) {
  note(false, `the page's script threw: ${e.message}`);
  console.log(e.stack);
  process.exit(1);
}

const { D, P, byQuestion, QUESTIONS, state, renderAnswerText,
        renderQuoteProvenance, renderPassageProvenance,
        renderRecordProvenance, renderPlaceProvenance, renderGroupProvenance,
        renderEdgeProvenance, buildMap, mapState, mapWindow, mapBase,
        viewQuestions, viewPlaces, viewAbout } = sandbox.__api;

/* ---- 2. every run renders without throwing ---- */
let rendered = 0, panels = 0;
for (const q of QUESTIONS) {
  state.question = q;
  const runs = byQuestion.get(q);
  for (let i = 0; i < runs.length; i++) {
    state.runIndex = i;
    try {
      renderAnswerText(runs[i]);
      viewQuestions();
      rendered++;
    } catch (e) { fail.push(`render ${q} run ${i}: ${e.message}`); }

    for (let si = 0; si < (runs[i].grounding?.quote_spans || []).length; si++) {
      try { renderQuoteProvenance(runs[i], si); panels++; }
      catch (e) { fail.push(`quote panel ${q}#${i}/${si}: ${e.message}`); }
    }
    for (const p of runs[i].passages || []) {
      try { renderPassageProvenance(runs[i], p.marker); panels++; }
      catch (e) { fail.push(`passage panel ${q}#${i}/${p.marker}: ${e.message}`); }
    }
  }
}
note(rendered === D.runs.length, `rendered all ${D.runs.length} runs (${rendered})`);
note(true, `built ${panels} provenance panels without throwing`);

for (const docId of Object.keys(D.corpus)) {
  try { renderRecordProvenance(docId); }
  catch (e) { fail.push(`record panel ${docId}: ${e.message}`); }
}
note(true, `built a record panel for all ${Object.keys(D.corpus).length} seed records`);
try { viewPlaces(); viewAbout(); note(true, "places and about views render"); }
catch (e) { note(false, `a view threw: ${e.message}`); }

/* ---- 2b. Phase 2, A5: every placement is reachable, plotted or not ----
 *
 * The whole design argument for A5's gap lists is that "not drawable" and
 * "silently missing" must never be the same thing. That is not verifiable by
 * reading the HTML a human would scroll past — it has to be checked against
 * the data. `renderRecordProvenance` was extended to list every place a
 * record carries, so every placement in `D.places.docs`, gap or not, must
 * appear there as a `data-place` target; there is no other path a person
 * could use to reach it if this failed silently.
 */
{
  let placements = 0, missingFromRecord = 0, thrown = 0;
  for (const [docId, entries] of Object.entries(P.docs || {})) {
    let html;
    try { html = renderRecordProvenance(docId); }
    catch (e) { thrown++; continue; }
    for (const e of entries) {
      placements++;
      if (!html.includes(`data-place="${e.key}"`)) missingFromRecord++;
      try { renderPlaceProvenance(e.key); }
      catch (err) { fail.push(`place panel ${e.key}: ${err.message}`); }
    }
  }
  note(thrown === 0, `every placed document's record panel renders (${thrown} threw)`);
  note(missingFromRecord === 0,
       `every placement is listed on its own record's panel (${placements} checked, ` +
       `${missingFromRecord} missing)`);
}

// Every pin/extent the data says is drawable must actually appear in the
// SVG the map builds — a group present in D.places.groups but absent from
// buildMap()'s output is a point the page claims to plot and does not.
{
  const svg = buildMap();
  const missingGroups = (P.groups || []).filter(g => !svg.includes(`data-group="${g.cache_key}"`));
  note(missingGroups.length === 0,
       `every cached point/extent (${(P.groups||[]).length}) is drawn on the map` +
       (missingGroups.length ? ` — missing: ${missingGroups.slice(0,5).map(g=>g.cache_key).join(", ")}` : ""));

  const drawableEdges = (P.edges || []).map((e, i) => [e, i]).filter(([e]) => e.drawable);
  const missingEdges = drawableEdges.filter(([, i]) => !svg.includes(`data-edge="${i}"`));
  note(missingEdges.length === 0,
       `every drawable edge (${drawableEdges.length}) is drawn on the map` +
       (missingEdges.length ? ` — missing index ${missingEdges.slice(0,5).map(([,i])=>i).join(", ")}` : ""));

  for (const g of P.groups || []) {
    try { renderGroupProvenance(g.cache_key); }
    catch (err) { fail.push(`group panel ${g.cache_key}: ${err.message}`); }
  }
  for (let i = 0; i < (P.edges || []).length; i++) {
    try { renderEdgeProvenance(i); }
    catch (err) { fail.push(`edge panel ${i}: ${err.message}`); }
  }
  note(true, `built ${(P.groups||[]).length} group panel(s) and ${(P.edges||[]).length} edge panel(s) without throwing`);
}

/* ---- 2b2. the date verdicts reach the screen ----
 *
 * A6 computed `hole` and `unknown` in `ingest/gazetteer.py --check` and the
 * bundle did not carry them, so for one release the page could not show that a
 * point's dates fail to corroborate the record citing it. Carrying them in
 * `data.js` fixes half of that; this asserts the other half, because a verdict
 * that reaches the bundle and not the panel is the same defect one layer down.
 *
 * Asserted on `data-date-verdict`, an attribute the renderer emits for exactly
 * this purpose, rather than on the prose around it — the sentence will be
 * reworded and the claim will not.
 */
{
  const tally = {};
  const unsurfaced = [];
  for (const [docId, entries] of Object.entries(P.docs || {})) {
    for (const e of entries) {
      const v = e.resolved?.date_verdict ?? "(not resolved)";
      tally[v] = (tally[v] || 0) + 1;
      if (v !== "hole" && v !== "unknown") continue;
      let html = "";
      try { html = renderPlaceProvenance(e.key); } catch { /* panel failure is 2b's business */ }
      if (!html.includes(`data-date-verdict="${v}"`)) unsurfaced.push(`${e.key} (${v})`);
    }
  }
  note(unsurfaced.length === 0,
       `every 'hole'/'unknown' date verdict is surfaced on its placement panel ` +
       `— ${JSON.stringify(tally)}` +
       (unsurfaced.length ? ` — NOT shown: ${unsurfaced.slice(0, 5).join(", ")}` : ""));

  // The verdict must be present, not merely absent-and-forgiven: an entry that
  // resolved and carries no verdict at all means the builder skipped the audit.
  const missing = Object.values(P.docs || {}).flat()
    .filter(e => e.resolved && e.resolved.date_verdict == null);
  note(missing.length === 0,
       `every resolved placement carries a date verdict (${missing.length} missing)` +
       (missing.length ? ` — e.g. ${missing.slice(0, 3).map(e => e.key).join(", ")}` : ""));
}

/* ---- 2c. the coastline is the right way round ----
 *
 * This check exists because of a specific failure. The first coastline
 * snapshot emitted undifferentiated boundary rings; drawn as one filled SVG
 * path, the Mediterranean and Black Sea came out as water and the Indian
 * Ocean and Atlantic came out as LAND. Every check in this file passed —
 * they assert that each cached point and edge is PRESENT in the SVG, and all
 * of them were, on top of an inside-out world. It was caught by rendering the
 * map to an image and looking at it.
 *
 * So this asserts a property instead: known-land points are inside the filled
 * region and known-sea points are outside it, evaluated with the same
 * even-odd rule the SVG's `fill-rule="evenodd"` uses over the same rings.
 * Getting the winding backwards now fails here rather than looking plausible.
 */
if (D.coastline && D.coastline.polygons) {
  const rings = D.coastline.polygons.flat();

  // Even-odd across EVERY ring, matching the single <path fill-rule="evenodd">
  // the map builds by concatenating all rings of all polygons.
  const isFilled = (lon, lat) => {
    let inside = false;
    for (const ring of rings) {
      for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        const [xi, yi] = ring[i], [xj, yj] = ring[j];
        if ((yi > lat) !== (yj > lat) &&
            lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
      }
    }
    return inside;
  };

  const controls = [
    ["Aksum, Ethiopia", 38.72, 14.13, true],
    ["central Sahara", 15.0, 25.0, true],
    ["central Arabia", 45.0, 24.0, true],
    ["Deccan, India", 77.0, 18.0, true],
    ["mid Mediterranean", 18.0, 34.5, false],
    ["mid Black Sea", 34.0, 43.0, false],
    ["mid Arabian Sea", 65.0, 15.0, false],
    ["mid Bay of Bengal", 88.0, 15.0, false],
    ["mid Red Sea", 38.5, 20.0, false],
  ];
  const wrong = controls.filter(([, lon, lat, land]) => isFilled(lon, lat) !== land);
  note(wrong.length === 0,
       `coastline renders land as land and sea as sea (${controls.length} control points)` +
       (wrong.length
         ? ` — WRONG: ${wrong.map(([n, , , land]) => `${n} should be ${land ? "land" : "sea"}`).join("; ")}`
         : ""));

  // The legend prints these; a snapshot that cannot say where it came from or
  // when cannot be attributed on screen.
  const missingProv = ["source", "terms", "retrieved", "scale"]
    .filter(k => !D.coastline[k]);
  note(missingProv.length === 0,
       `the coastline snapshot carries its provenance` +
       (missingProv.length ? ` — missing ${missingProv.join(", ")}` : ""));
} else {
  note(true, "no coastline snapshot bundled — map degrades to a graticule (not a failure)");
}

/* ---- 2d. the map survives being zoomed ----
 *
 * Every other check in this file calls `buildMap()` at the default view, and
 * the coastline culling bug this guards was invisible there. The first version
 * skipped a landmass unless one of its VERTICES fell inside the window —
 * correct at full extent, and wrong the moment you zoom inside a continent,
 * where every vertex of Africa is off-screen while Africa covers the whole
 * view. The map would lose its land exactly when land was all there was.
 *
 * Also asserts the thing pan/zoom must never do: change the shape of the
 * world. The window is derived so that lon-span : lat-span always matches
 * W : H, because the projection is already equirectangular and a second,
 * accidental stretch on top of it would be untraceable.
 */
{
  const saved = { zoom: mapState.zoom, cx: mapState.cx, cy: mapState.cy };
  const views = [
    ["mid-ocean, x8",        65.0, 15.0,  8],
    ["inside the Sahara, x40", 20.0, 25.0, 40],
    ["Malabar cluster, x14",  76.0, 10.6, 14],
    ["Red Sea, x9",           39.0, 15.5,  9],
  ];
  const noLand = [], skewed = [];
  for (const [name, cx, cy, z] of views) {
    mapState.cx = cx; mapState.cy = cy; mapState.zoom = z;
    const svg = buildMap();
    if (!svg.includes('class="land"')) noLand.push(name);
    const w = mapWindow();
    const err = Math.abs(((w.lonMax - w.lonMin) / (w.latMax - w.latMin)) / (w.W / w.H) - 1);
    if (err > 1e-9) skewed.push(`${name} (${err.toExponential(1)})`);
  }
  note(noLand.length === 0,
       `the coastline still draws when zoomed in (${views.length} views)` +
       (noLand.length ? ` — land vanished at: ${noLand.join(", ")}` : ""));
  note(skewed.length === 0,
       `zooming never distorts the projection's aspect ratio` +
       (skewed.length ? ` — skewed at: ${skewed.join(", ")}` : ""));

  // Reset must land exactly back on the default view, not merely near it.
  mapState.zoom = 1; mapState.cx = null; mapState.cy = null;
  const home = mapWindow(), base = mapBase();
  note(Math.abs((home.lonMin + home.lonMax) / 2 - base.cx) < 1e-9 &&
       Math.abs((home.lonMax - home.lonMin) - base.spanLon) < 1e-9,
       "reset returns exactly to the full extent");

  Object.assign(mapState, saved);
}

// Every document with a place or a `no_places_reason` is reachable from the
// Places tab's record grid — the entry point every panel above assumes.
{
  const allIds = new Set(Object.keys(D.corpus));
  const placesHtml = viewPlaces();
  const missing = [...allIds].filter(id => !placesHtml.includes(`data-record="${id}"`));
  note(missing.length === 0,
       `all ${allIds.size} records are clickable from the Places tab` +
       (missing.length ? ` — missing: ${missing.slice(0,5).join(", ")}` : ""));
}

/* ---- 3. the UI's on-screen claims are true of the data ---- */

// Every quotation present in the answer prose must end up highlighted. A quote
// silently not rendered is exactly the failure this page exists to rule out.
let expected = 0, highlighted = 0, unhighlighted = [];
for (const run of D.runs) {
  const html = renderAnswerText(run);
  const marks = (html.match(/<mark class="q/g) || []).length;
  const inProse = (run.grounding?.quote_spans || [])
    .filter(s => (s.quote || "").trim().length >= 3 &&
                 (run.answer || "").includes(s.quote.trim()));
  expected += inProse.length;
  highlighted += marks;
  if (marks < inProse.length) unhighlighted.push(`${run.run_key}: ${inProse.length - marks}`);
}
note(unhighlighted.length === 0,
     `every quotation appearing in an answer is highlighted (${highlighted}/${expected})`
     + (unhighlighted.length ? ` — missed in ${unhighlighted.slice(0,3).join(", ")}` : ""));

// Every [Sn] marker the model wrote must correspond to a source that was
// actually supplied. `unknown_markers` is the grounding report's own name for a
// breach of this, so the two must agree.
let danglers = 0, reported = 0;
for (const run of D.runs) {
  const have = new Set((run.passages || []).map(p => p.marker));
  const used = new Set([...(run.answer || "").matchAll(/\[S\d+\]/g)].map(m => m[0].slice(1, -1)));
  for (const m of used) if (!have.has(m)) danglers++;
  reported += (run.grounding?.unknown_markers || []).length;
}
note(danglers === reported,
     `citation markers all resolve to a source card (${danglers} dangling, ` +
     `grounding reports ${reported})`);

// Every span classified `resolved` must genuinely hold its quote, checked here
// against data.js rather than trusting the Python that wrote it.
let checked = 0, bad = 0;
for (const run of D.runs) {
  for (const s of run.grounding?.quote_spans || []) {
    const r = s.resolution;
    if (!r || r.state !== "resolved") continue;
    const text = D.corpus[s.doc_id]?.fields?.[s.source_field];
    const found = text?.slice(s.abs_start, s.abs_end) ?? "";
    const quote = (s.quote || "").trim();
    checked++;
    if (!(found && (found.includes(quote) || quote.includes(found)))) bad++;
  }
}
note(bad === 0, `all ${checked} 'resolved' spans hold their quoted characters (${bad} bad)`);

// The audit counts shown on the About tab must match the spans in the bundle.
// `case_folded` joined this list at C1a (2026-08-14). It was written as a fixed
// object rather than accumulated from the data, so an unlisted state would have
// incremented `undefined` and every comparison against NaN would have been
// false — the audit would have failed with a message that named the count and
// not the missing state. It is accumulated now, and the assertion is over the
// union of both sides' keys, so the next state to be added fails loudly here
// only if the two sides actually disagree.
const tally = { resolved: 0, case_folded: 0, case_only: 0, moved: 0, absent: 0 };
for (const run of D.runs)
  for (const s of run.grounding?.quote_spans || [])
    if (s.resolution) tally[s.resolution.state] = (tally[s.resolution.state] || 0) + 1;
const audit = D.span_audit || {};
const states = [...new Set([...Object.keys(tally), ...Object.keys(audit)])];
note(states.every(k => (tally[k] || 0) === (audit[k] || 0)),
     `the headline audit matches the spans: ${JSON.stringify(tally)}`);

console.log();
if (fail.length) {
  console.log(`${fail.length} check(s) failed:`);
  for (const f of fail) console.log("  - " + f);
  process.exit(1);
}
console.log("all checks passed");
