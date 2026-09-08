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
import { createHash } from "node:crypto";
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

/* FINDING 100, fixed here rather than in the design block that found it — a
   block quietly editing the guard file it is being judged by is worse than the
   defect, and this block is not judged by this line.

   The defect: this matched script tags ANYWHERE in the file, including inside
   HTML comments. A comment above the loading state described the tag it sits
   over, writing `<script src>` with no `=`; the lookahead excludes `src=` and
   not that, so the comment was counted as a second inline script and the
   capture ran from the middle of a comment to the first real `</script>`. The
   harness went red pointing at the page rather than at itself.

   The fix is to ignore matches that START INSIDE A COMMENT, rather than to
   strip comments out of `html` before matching: `scripts[0]` is what gets
   EXECUTED in the VM below, one of the page's own template strings contains an
   HTML comment, and a harness that runs a lightly-edited copy of the file is a
   harness asserting about something that does not ship. The comment ranges are
   computed once and the matches are filtered by index; every captured body is
   still byte-for-byte what is in the file. */
const commentRanges = [...html.matchAll(/<!--[\s\S]*?-->/g)]
  .map(m => [m.index, m.index + m[0].length]);
const inComment = i => commentRanges.some(([a, b]) => i >= a && i < b);
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .filter(m => !inComment(m.index))
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
    " buildMap, mapState, mapWindow, mapBase, viewHome, viewQuestions, viewPlaces, viewAbout," +
    " BANNER, BANNER_H, BANNER_NATIVE, bannerText, chainExample," +
    " railPartition, showableRuns, caseOf, REFUSAL_REASONS, refusalReason," +
    " SPAN_STATES, PROVENANCE, langName, placeLedger };",
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
        viewHome, viewQuestions, viewPlaces, viewAbout,
        BANNER, BANNER_H, BANNER_NATIVE, bannerText, chainExample,
        railPartition, showableRuns, caseOf, REFUSAL_REASONS, refusalReason,
        SPAN_STATES, PROVENANCE, langName, placeLedger } = sandbox.__api;

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
/* Every view the tab bar can reach is rendered here BY NAME. A view that is
   not in this list is a surface with no guard on it at all: the Home tab was
   added after this harness was written, and until it was named here a Home tab
   that threw would have shipped green. Add the next one the same day it
   exists. */
try { viewPlaces(); viewAbout(); note(true, "places and about views render"); }
catch (e) { note(false, `a view threw: ${e.message}`); }
try { viewHome(); note(true, "the home view renders"); }
catch (e) { note(false, `the home view threw: ${e.message}`); }

/* ---- 2c. the question rail is a PARTITION of the archive, and the two
   groups are what they claim to be. RULING 86.

   The rail lists 24 of 33 questions under seven regions, groups 7 more as
   refusals, and counts the rest in a line at its foot. That is three filters
   over one array, and three filters are how a question comes to be in none of
   them: the failure this guards against is not a wrong label, it is a question
   that silently stops being anywhere the day the archive grows a case the
   partition did not anticipate. So the assertion is set arithmetic — every
   archived question, exactly once — and not a count.

   The second check is the one that keeps the refusals group honest. "The corpus
   refuses this" is a CLAIM, and the evidence for it is that a person declared
   the case `correctly_refusable` in gold/ before the runs were made. A question
   that merely happens to have no showable run is a failure and belongs in the
   counted line, not under a heading that says the refusal was correct. ---- */
{
  const rail = railPartition();
  const listed = [
    ...rail.regions.flatMap(([, qs]) => qs),
    ...rail.refusals,
    ...rail.withheld,
  ];
  const seen = new Map();
  for (const q of listed) seen.set(q, (seen.get(q) || 0) + 1);
  const missing = QUESTIONS.filter(q => !seen.has(q));
  const twice = [...seen.keys()].filter(q => seen.get(q) > 1);
  const stray = [...seen.keys()].filter(q => !QUESTIONS.includes(q));
  note(
    missing.length === 0 && twice.length === 0 && stray.length === 0
      && listed.length === QUESTIONS.length,
    missing.length || twice.length || stray.length
      ? `the rail is not a partition of the archive — ${missing.length} question(s) in no group `
        + `(e.g. ${JSON.stringify(missing[0] || "")}), ${twice.length} in two, ${stray.length} in neither`
      : `every archived question is in the rail exactly once `
        + `(${rail.regions.reduce((n, [, qs]) => n + qs.length, 0)} under `
        + `${rail.regions.length} regions, ${rail.refusals.length} refusals, `
        + `${rail.withheld.length} withheld and counted)`,
  );

  const listedWithNothing = rail.regions
    .flatMap(([, qs]) => qs).filter(q => showableRuns(q).length === 0);
  const notDeclared = rail.refusals
    .filter(q => (caseOf.get(q) || {}).expected_behaviour !== "correctly_refusable");
  /* ---- 2c-iii. RULING 87: every refusal prints a REASON, and every claim
     that reason makes is re-derived here from the bundle.

     A sentence typed about the corpus is the prose form of a typed count, and
     the page's rule against those is the reason this guard exists rather than a
     comment asking the next person to be careful. Each sentence declares what
     it rests on — strings that appear in no field of a named record (or of any
     record), or a record that carries no translation and whose excerpt is a
     bracketed editorial pointer — and if the corpus stops making that true the
     line goes red instead of the page going quietly wrong.

     The Palmyrene case is the live one: `manifest.json` lists that record for a
     transcription pass, and its own gold note calls the case "a tripwire on
     that follow-up". The day the pass happens, this check is the tripwire. ---- */
  const reasonProblems = [];
  for (const q of rail.refusals) {
    const c = caseOf.get(q) || {};
    const r = refusalReason(q);
    if (!r) { reasonProblems.push(`${c.id || q}: no reason written`); continue; }
    if (!r.line || !r.line.trim()) { reasonProblems.push(`${c.id}: empty reason`); continue; }
    const h = r.holds || {};
    if (h.absent) {
      const recs = h.doc ? [[h.doc, D.corpus[h.doc]]] : Object.entries(D.corpus);
      if (h.doc && !D.corpus[h.doc]) { reasonProblems.push(`${c.id}: no record ${h.doc}`); continue; }
      for (const w of h.absent) {
        const found = recs.filter(([, rec]) =>
          Object.values((rec && rec.fields) || {})
            .some(v => String(v).toLowerCase().includes(w.toLowerCase())));
        if (found.length)
          reasonProblems.push(`${c.id}: "${w}" is NOT absent — it is in ${found[0][0]}`);
      }
    }
    if (h.pointerOnly) {
      const rec = D.corpus[h.doc];
      const f = (rec && rec.fields) || {};
      const excerpt = String(f.original_text_excerpt || "").trim();
      if (!rec) reasonProblems.push(`${c.id}: no record ${h.doc}`);
      else if (f.reference_translation)
        reasonProblems.push(`${c.id}: ${h.doc} now carries a reference_translation — `
          + `the record has gained reachable text and the sentence is stale`);
      else if (!excerpt.startsWith("["))
        reasonProblems.push(`${c.id}: ${h.doc}'s excerpt is no longer a bracketed pointer`);
    }
    if (!h.absent && !h.pointerOnly)
      reasonProblems.push(`${c.id}: reason makes no re-derivable claim`);
  }
  note(
    reasonProblems.length === 0,
    reasonProblems.length
      ? `a refusal's stated reason no longer holds — ${reasonProblems[0]}`
        + (reasonProblems.length > 1 ? ` (and ${reasonProblems.length - 1} more)` : "")
      : `every refusal states why, and every claim those reasons make still holds `
        + `against the corpus (${rail.refusals.length} reasons, `
        + `${Object.values(REFUSAL_REASONS).reduce((n, r) => n + ((r.holds.absent || []).length || 1), 0)} claims)`,
  );

  note(
    listedWithNothing.length === 0 && notDeclared.length === 0,
    listedWithNothing.length || notDeclared.length
      ? `the rail's two groups do not hold what they claim — ${listedWithNothing.length} region `
        + `question(s) with no showable run, ${notDeclared.length} refusal(s) gold does not `
        + `declare correctly_refusable (e.g. ${JSON.stringify(notDeclared[0] || listedWithNothing[0] || "")})`
      : `the region rail holds only questions with a showable run, and every refusal is `
        + `declared correctly_refusable in gold (${rail.refusals.length} checked)`,
  );
}

/* ---- 2d. the chain figure on Home ----
 *
 * The figure says, of a specific quotation, "these are the characters on
 * disk". That is the page's whole claim stated in one picture, and a picture
 * is the one thing on this page a reader cannot click to check. So it is
 * checked here: the example still exists, its span still resolves, and the
 * characters at the recorded offsets ARE the quoted characters.
 *
 * A figure illustrating click-through provenance with a quotation that no
 * longer resolves would be the most embarrassing defect this page could carry,
 * and nothing else in this harness looks at it — the example is chosen at
 * render time from whatever the archive holds, so it can change without anyone
 * editing a line.
 */
{
  const c = chainExample();
  if (!c) {
    note(false, "the chain figure has no example: no default run has a resolved quotation");
  } else {
    const problems = [];
    if (c.span.resolution?.state !== "resolved")
      problems.push(`the chosen span is ${c.span.resolution?.state}, not resolved`);
    if (c.onDisk !== c.span.quote)
      problems.push(`the characters at [${c.span.abs_start}:${c.span.abs_end}] are not the quoted ` +
                    `characters (${JSON.stringify(c.onDisk.slice(0, 40))} vs ` +
                    `${JSON.stringify(c.span.quote.slice(0, 40))})`);
    if (!c.rec.file) problems.push("the record names no file");
    note(problems.length === 0,
         `the chain figure draws a quotation that still resolves ` +
         `(${c.rec.file}:${c.span.source_field}[${c.span.abs_start}:${c.span.abs_end}])` +
         (problems.length ? ` — ${problems.join("; ")}` : ""));
  }
}

/* ---- 2c. the masthead script band ----
 *
 * The band shows source text as IMAGES, because live web type would give a
 * visitor without a Tamil, Devanagari, CJK or polytonic Greek font a row of
 * tofu boxes. An image is the one thing on this page a reader cannot check by
 * clicking, so it is checked here instead, on four counts:
 *
 *   - the page's declared list and ui/banner/manifest.json agree. They are two
 *     declarations of one curation decision, in two files, and nothing else
 *     would notice them drifting apart
 *   - the record each specimen names still exists
 *   - the declared start is still IN that record's field. If a record is
 *     re-curated and the substring goes, the page silently drops the specimen
 *     and this says so
 *   - the characters the page reads back for the alt text are the characters
 *     the generator baked into the image. An image whose alt text has drifted
 *     from the picture is a caption that lies, and it is exactly the class of
 *     defect FINDING 98 was: three renderings of one thing, disagreeing.
 */
{
  let manifest = null;
  try { manifest = JSON.parse(readFileSync(join(UI, "banner", "manifest.json"), "utf8")); }
  catch (e) { note(false, `ui/banner/manifest.json is unreadable: ${e.message}`); }

  if (manifest) {
    const byCode = new Map(manifest.specimens.map(sp => [sp.code, sp]));
    const problems = [];
    if (manifest.specimens.length !== BANNER.length)
      problems.push(`the page declares ${BANNER.length} specimen(s), the manifest ${manifest.specimens.length}`);
    for (const s of BANNER) {
      const m = byCode.get(s.code);
      if (!m) { problems.push(`${s.code}: declared on the page, absent from the manifest`); continue; }
      if (m.doc !== s.doc)     problems.push(`${s.code}: page says ${s.doc}, manifest says ${m.doc}`);
      if (m.from !== s.from)   problems.push(`${s.code}: the declared start differs between page and manifest`);
      if (m.w !== s.w)         problems.push(`${s.code}: declared width ${s.w} but the image was rendered ${m.w}`);
      if (!D.corpus[s.doc])    problems.push(`${s.code}: ${s.doc} is not in the corpus`);
      const text = bannerText(s);
      if (text == null)        problems.push(`${s.code}: the declared start "${s.from}" is no longer in ${s.doc}`);
      else if (text !== m.text) problems.push(`${s.code}: the page reads "${text}" where the image shows "${m.text}"`);
      try { statSync(join(UI, "banner", `${s.code}.png`)); }
      catch { problems.push(`${s.code}: ui/banner/${s.code}.png is missing`); }
    }
    note(problems.length === 0,
         `every masthead specimen (${BANNER.length}) has its record, its characters and its image` +
         (problems.length ? ` — ${problems.slice(0, 4).join("; ")}` : ""));

    const nat = BANNER.filter(s => BANNER_NATIVE.has(s.code)).length;
    note(BANNER.every(s => BANNER_NATIVE.has(s.code) === !!byCode.get(s.code)?.native),
         `native script and romanised transliteration are not confused (${nat} native of ${BANNER.length})`);
  }
}

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

/* ---- 2e. FINDING 98: every span state renders DELIBERATELY ----
 *
 * `whitespace_only` reached neither renderer. It fell through the class chain
 * to "" -- visually a clean citation -- and through the title chain to "this
 * quotation no longer resolves against the corpus", while its provenance panel
 * printed no box at all. Three answers on one citation and none of them
 * agreeing, and every check in this file passed over it, because all of them
 * assert a span is PRESENT and HIGHLIGHTED and it was.
 *
 * So this asserts what none of them did: that the state reaches the DOM AS
 * ITSELF. `data-span-state` exists for this and for nothing else -- the same
 * argument as `data-date-verdict` at A6, one layer over. The next state added
 * to `classify_span` and not to `SPAN_STATES` fails here instead of quietly
 * borrowing a neighbour's colour.
 */
{
  const seen = {}, mismatched = [], unknown = [];
  for (const run of D.runs) {
    const html = renderAnswerText(run);
    const spans = run.grounding?.quote_spans || [];
    for (const m of html.matchAll(/data-span-state="([^"]*)"/g))
      seen[m[1]] = (seen[m[1]] || 0) + 1;
    if (/class="q unknownstate"/.test(html)) unknown.push(run.run_key);
    // Every state in the data must be the state on the mark, span by span.
    for (let si = 0; si < spans.length; si++) {
      const want = spans[si].resolution?.state;
      if (!want) continue;
      const re = new RegExp(`<mark class="q[^"]*" data-span="${si}" data-span-state="([^"]*)"`);
      const got = (html.match(re) || [])[1];
      if (got !== undefined && got !== want)
        mismatched.push(`${run.run_key}#${si}: data says ${want}, mark says ${got}`);
    }
  }
  note(mismatched.length === 0,
       `every mark carries its own span's state (${JSON.stringify(seen)})` +
       (mismatched.length ? ` — ${mismatched.slice(0, 3).join("; ")}` : ""));
  note(unknown.length === 0,
       `no span falls through to the unknown-state rendering` +
       (unknown.length ? ` — ${unknown.length} run(s) do, e.g. ${unknown[0]}` : ""));

  // And the panel agrees with the mark. FINDING 98 was precisely the two
  // disagreeing, so asserting them separately would not have caught it.
  const panelMissing = [];
  for (const run of D.runs) {
    const spans = run.grounding?.quote_spans || [];
    for (let si = 0; si < spans.length; si++) {
      const want = spans[si].resolution?.state;
      if (!want) continue;
      const html = renderQuoteProvenance(run, si);
      if (!html.includes(`data-span-state="${want}"`)) panelMissing.push(`${run.run_key}#${si} (${want})`);
    }
  }
  note(panelMissing.length === 0,
       `every quotation panel names its own span's state (${panelMissing.length} do not)` +
       (panelMissing.length ? ` — e.g. ${panelMissing.slice(0, 3).join(", ")}` : ""));

  // Every state the data can produce must have a deliberate entry. A state
  // present in classify_span's output and absent from SPAN_STATES is FINDING
  // 98 again, and this is the check that would have caught it the first time.
  const dataStates = new Set();
  for (const run of D.runs)
    for (const s of run.grounding?.quote_spans || [])
      if (s.resolution) dataStates.add(s.resolution.state);
  const untabled = [...dataStates].filter(st => !(st in SPAN_STATES));
  note(untabled.length === 0,
       `SPAN_STATES covers every state in the archive (${[...dataStates].sort().join(", ")})` +
       (untabled.length ? ` — MISSING: ${untabled.join(", ")}` : ""));
}

/* ---- 2f. D1's SECOND AXIS reaches the screen, and stays a separate axis ----
 *
 * `build_ui_data.py` has written `resolution.provenance` onto every span since
 * D1 and, until this block, the page read none of it. A field that reaches the
 * bundle and not the panel is the A6 defect; a field that reaches the bundle,
 * is never read, and is nobody's job is the same defect with no owner.
 *
 * The second assertion is the one that matters. `unrecorded` means NOT
 * KNOWABLE, and `corpus_provenance`'s docstring is explicit that collapsing it
 * into `unchanged` reports a span as a real defect on no evidence. So this
 * checks that no span whose data says `unrecorded` is ever rendered as
 * anything else -- the failure would be invisible on screen and would quietly
 * turn eleven unknowns into eleven verdicts.
 */
/* RULING 88 MOVED THIS CHECK, AND MADE IT A STRONGER ONE.
 *
 * It used to call `renderQuoteProvenance` for all 1289 spans and assert that
 * each panel's HTML contained its own `data-provenance`. The quotation panel no
 * longer carries the second axis — a reader looking at a quotation was being
 * asked a question about the archive's bookkeeping, and "not knowable from the
 * archive" reads as doubt about the quotation rather than as what it means — so
 * the axis is rendered on the Data & Sources tab instead, cell by cell, beside
 * the first axis it has to be read against.
 *
 * The guard moved with it and asserts MORE than it did. The old one could only
 * say a state APPEARED somewhere in a panel. This one re-derives the whole
 * cross-tabulation from the archive and asserts every cell of it is on screen
 * with the right COUNT and both its states machine-readable — so collapsing
 * `unrecorded` into `unchanged` now fails on arithmetic, not on a missing
 * attribute, and a cell that quietly disappears fails too.
 */
{
  const cross = {}, tally = {};
  for (const run of D.runs)
    for (const s of run.grounding?.quote_spans || []) {
      const st = s.resolution?.state;
      const pv = s.resolution?.provenance?.state;
      if (!st || !pv) continue;
      cross[`${st} ${pv}`] = (cross[`${st} ${pv}`] || 0) + 1;
      tally[pv] = (tally[pv] || 0) + 1;
    }

  const aboutHtml = viewAbout();
  const cells = [...aboutHtml.matchAll(
    /data-span-state="([^"]+)"\s+data-provenance="([^"]+)"\s+data-cell-count="(\d+)"/g)]
    .map(m => [`${m[1]} ${m[2]}`, Number(m[3])]);
  const onScreen = Object.fromEntries(cells);

  const wrong = [];
  for (const [k, n] of Object.entries(cross)) {
    if (!(k in onScreen)) wrong.push(`${k}: ${n} spans, not on screen at all`);
    else if (onScreen[k] !== n) wrong.push(`${k}: archive says ${n}, screen says ${onScreen[k]}`);
  }
  for (const [k, n] of cells)
    if (!(k in cross)) wrong.push(`${k}: on screen (${n}) and not in the archive`);

  note(wrong.length === 0,
       `every cell of the two axes is on screen with its own count — ` +
       `${cells.length} cells, ${JSON.stringify(tally)}` +
       (wrong.length ? ` — WRONG: ${wrong.slice(0, 3).join("; ")}` : ""));

  /* The second assertion, unchanged in substance and now checkable by counting:
     the spans the archive calls `unrecorded` must be reported as `unrecorded`.
     Folding them into either neighbour moves the number, and the number is
     what is asserted. */
  const unrecOnScreen = cells.filter(([k]) => k.endsWith(" unrecorded"))
    .reduce((n, [, v]) => n + v, 0);
  note(unrecOnScreen === (tally.unrecorded || 0),
       `no 'unrecorded' span is reported as 'unchanged' or 'changed' ` +
       `(${unrecOnScreen} of ${tally.unrecorded || 0} still their own third answer)`);

  // Every provenance state must have a deliberate entry too, same argument.
  const untabled = Object.keys(tally).filter(p => !(p in PROVENANCE));
  note(untabled.length === 0,
       `PROVENANCE covers every provenance state in the archive` +
       (untabled.length ? ` — MISSING: ${untabled.join(", ")}` : ""));
}

/* ---- 2g. no count on this page is written down ----
 *
 * The page shipped `"All 24 records, by region"`, `"a corpus of 24 primary
 * sources"`, `"Five records ... have not been geographically placed at all"`
 * and `"two of the seven literary records"` while the corpus was 54, 54, zero
 * and neither. Every one was a literal typed once and true once.
 *
 * A guard against "a number appears in prose" would be unenforceable, so this
 * asserts the specific failure instead: no view may print a corpus-size or
 * record-count figure that disagrees with the bundle. The numbers it hunts for
 * are the ones that were actually wrong.
 */
{
  const html = viewPlaces() + viewAbout() + viewQuestions();
  const n = Object.keys(D.corpus).length;
  const stale = [];
  for (const [pattern, why] of [
    [/All (\d+) records, by region/, "the record-list heading"],
    [/corpus of (\d+) primary\s+sources/, "the About tab's opening sentence"],
  ]) {
    const m = html.match(pattern);
    if (m && Number(m[1]) !== n) stale.push(`${why}: says ${m[1]}, corpus is ${n}`);
  }
  // The two sentences that were not about the corpus size and were wrong anyway.
  if (/Five records \(the GeoNames backlog\)/.test(html) &&
      (P.unconsidered || []).length !== 5)
    stale.push(`the GeoNames-backlog sentence says five, unconsidered is ${(P.unconsidered||[]).length}`);
  if (/two of the seven literary records/.test(html))
    stale.push("the 'two of the seven literary records' sentence is a literal from 24 records");
  note(stale.length === 0,
       `no view prints a record count that disagrees with the bundle (${n} records)` +
       (stale.length ? ` — ${stale.join("; ")}` : ""));

  // Every language code in the corpus must have a name. `pal`, `san`, `ocm`,
  // `omy`, `non`, `arb`, `ko`, `vi` and `fr` rendered as raw ISO codes.
  const unnamed = [];
  for (const rec of Object.values(D.corpus))
    for (const c of rec.language_code || [])
      if (langName(c) === c) unnamed.push(c);
  note(unnamed.length === 0,
       `every language code in the corpus has a name on screen` +
       (unnamed.length ? ` — raw codes shown for: ${[...new Set(unnamed)].join(", ")}` : ""));
}

/* ---- 2h. DEBT ROW 7: the manifest describes the bundle beside it ----
 *
 * FINDING 74. `data.js` is one 9.5MB line, so `git diff --stat` calls every
 * rebuild `2 +-`. `data.manifest.json` is the reviewable diff -- and a
 * manifest nothing checks is a file that says whatever it last said, so every
 * figure in it is re-derived HERE from `data.js` rather than trusted.
 */
{
  let manifest = null;
  try { manifest = JSON.parse(readFileSync(join(UI, "data.manifest.json"), "utf8")); }
  catch (e) { note(false, `ui/data.manifest.json is missing or unparseable (${e.message}) — run: python ui/build_ui_data.py`); }

  if (manifest) {
    const actual = createHash("sha256").update(readFileSync(join(UI, "data.js"))).digest("hex");
    note(manifest.data_js?.sha256 === actual,
         `the manifest names the data.js sitting beside it` +
         (manifest.data_js?.sha256 === actual ? ""
           : ` — manifest says ${String(manifest.data_js?.sha256).slice(0,12)}…, file is ${actual.slice(0,12)}…`));

    const spans = D.runs.flatMap(r => (r.grounding?.quote_spans || []).filter(s => s.resolution));
    const tally = (xs, f) => { const t = {}; for (const x of xs) { const k = f(x); t[k] = (t[k]||0)+1; } return t; };
    const derived = {
      "corpus.records": [manifest.corpus?.records, Object.keys(D.corpus).length],
      "runs.count": [manifest.runs?.count, D.runs.length],
      "runs.with_corpus_version": [manifest.runs?.with_corpus_version,
                                    D.runs.filter(r => r.corpus_version).length],
      "spans.claimed": [manifest.spans?.claimed, spans.length],
      "places.groups": [manifest.places?.groups, (P.groups || []).length],
      "places.edges": [manifest.places?.edges, (P.edges || []).length],
    };
    const off = Object.entries(derived).filter(([, [m, d]]) => m !== d)
      .map(([k, [m, d]]) => `${k}: manifest ${m}, data.js ${d}`);
    const auditOff = JSON.stringify(manifest.spans?.audit) !==
      JSON.stringify(Object.fromEntries(Object.entries(tally(spans, s => s.resolution.state)).sort()));
    const provOff = JSON.stringify(manifest.spans?.corpus_provenance) !==
      JSON.stringify(Object.fromEntries(Object.entries(tally(spans, s => s.resolution.provenance.state)).sort()));
    if (auditOff) off.push("spans.audit disagrees with the spans in data.js");
    if (provOff) off.push("spans.corpus_provenance disagrees with the spans in data.js");
    note(off.length === 0,
         `every figure in the manifest is re-derivable from data.js (${Object.keys(derived).length + 2} checked)` +
         (off.length ? ` — ${off.join("; ")}` : ""));

    // The manifest must keep the two axes apart. Merging them in a summary is
    // how a decomposition quietly becomes a total.
    note(manifest.spans?.audit != null && manifest.spans?.corpus_provenance != null,
         "the manifest reports both verify axes, separately");
  }
}

/* ---- 2i. FINDING 99: nothing emits a tag with a newline inside it ----
 *
 * `renderAnswerText` turned every newline in the ASSEMBLED MARKUP into a
 * `<br>`, and the citation-marker button was written across two lines for
 * readability. So the newline inside its opening tag became a `<br>` and broke
 * the tag: browsers parsed `<button class="marker" data-marker="S1"<br` as the
 * element and rendered the rest of the attributes as visible text. All 1945
 * markers in the archive, on every run, for the whole life of the page.
 *
 * NOT ONE CHECK IN THIS FILE CAUGHT IT. The marker assertion below compares
 * markers in the answer PROSE against the grounding report's `unknown_markers`
 * — both of which were fine. Nothing rendered the markup and looked at it.
 * That is the second time (after the inside-out coastline at 2c) that looking
 * at the page was the only instrument that worked, so this asserts the
 * property instead: no tag this page emits contains a newline, and every
 * marker is a well-formed clickable element.
 */
{
  const brokenTag = [], notClickable = [];
  let markers = 0;
  for (const run of D.runs) {
    const html = renderAnswerText(run);
    // A `<` inside what should be a tag, or a tag containing a newline.
    if (/<[a-zA-Z][^>]*[\n<][^>]*>/.test(html)) brokenTag.push(run.run_key);
    const inProse = [...(run.answer || "").matchAll(/\[S\d+\]/g)].length;
    const rendered = (html.match(/<button class="marker" data-marker="[^"]+" title="[^"]*">/g) || []).length;
    markers += rendered;
    // Every marker the model wrote that is not inside a quotation should be a
    // button. Quotations swallow some, so `rendered` may be lower — but it may
    // never be zero while the prose has markers outside every quote range.
    if (inProse > 0 && rendered === 0 &&
        !(run.grounding?.quote_spans || []).some(s => (s.quote || "").includes("[S")))
      notClickable.push(run.run_key);
  }
  note(brokenTag.length === 0,
       `no rendered answer emits a tag with a newline or a stray '<' inside it (${markers} marker buttons)` +
       (brokenTag.length ? ` — malformed in ${brokenTag.length} run(s), e.g. ${brokenTag[0]}` : ""));
  note(notClickable.length === 0,
       `every answer whose prose carries a citation marker renders it as a button` +
       (notClickable.length ? ` — ${notClickable.length} do not, e.g. ${notClickable[0]}` : ""));
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
