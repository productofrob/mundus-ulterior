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
    " buildMap, mapState, mapWindow, mapBase, MARK, MAP_LABEL_PX," +
    " viewHome, viewQuestions, viewPlaces, viewAbout," +
    " BANNER, BANNER_H, BANNER_NATIVE, bannerText, chainExample," +
    " railPartition, showableRuns, caseOf, REFUSAL_REASONS, refusalReason, PUBLIC_NOTES, TABS," +
    " pushSelection, stepSelection, clearTrail, canStep, panelNav, placeNotice," +
    " SPAN_STATES, PROVENANCE, PANEL_EMPTY, SELECT_ATTR, renderPanel, langName, placeLedger,"
    + " regionBands, bandLedger, bandBox, BAND, renderRegionProvenance, layoutBands,"
    + " REGION_ANCHOR, mapLegend };",
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
        renderEdgeProvenance, buildMap, mapState, mapWindow, mapBase, MARK, MAP_LABEL_PX,
        viewHome, viewQuestions, viewPlaces, viewAbout,
        BANNER, BANNER_H, BANNER_NATIVE, bannerText, chainExample,
        railPartition, showableRuns, caseOf, REFUSAL_REASONS, refusalReason, PUBLIC_NOTES, TABS,
        pushSelection, stepSelection, clearTrail, canStep, panelNav, placeNotice,
        SPAN_STATES, PROVENANCE, PANEL_EMPTY, SELECT_ATTR, renderPanel,
        langName, placeLedger,
        regionBands, bandLedger, bandBox, BAND, renderRegionProvenance,
        layoutBands, REGION_ANCHOR, mapLegend } = sandbox.__api;

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

  /* AND EVERY ONE OF THEM IS BIG ENOUGH TO CLICK.
     An SVG stroke is hit-tested at the width it is drawn, and an edge is drawn
     at 1.4 viewBox units — thinner than a cursor hotspot. Every edge on this map
     was clickable in principle and unhittable in practice from A5 until Rob
     reported that mousing over one did not select it, and NO CHECK HERE COULD
     SEE IT: this guard asserted the edge was in the markup, and it was.

     So the claim is widened rather than a second guard added beside it. An edge
     is drawn AND it presents a target: a `.hit` line in the same group, reading
     `--edge-hit` from the stylesheet, several times the visible stroke. The
     failure this catches is silent and looks fine in the source — drop the hit
     line, or let the token drift down to the drawn width, and the map looks
     identical and stops responding. */
  const drawableEdges = (P.edges || []).map((e, i) => [e, i]).filter(([e]) => e.drawable);
  const edgeProblems = [];
  for (const [, i] of drawableEdges) {
    if (!svg.includes(`data-edge="${i}"`)) { edgeProblems.push(`edge ${i} is not drawn`); continue; }
    const at = svg.indexOf(`data-edge="${i}"`);
    const chunk = svg.slice(at, at + 400);
    if (!/class="hit"/.test(chunk)) edgeProblems.push(`edge ${i} has no hit line`);
  }
  const hitDecl = html.match(/--edge-hit:\s*([\d.]+)/);
  const hitRule = html.match(/\.mapsvg \.edge \.hit \{[\s\S]*?\}/);
  const lnRule  = html.match(/\.mapsvg \.edge \.ln \{[\s\S]*?\}/);
  if (!hitDecl) edgeProblems.push("the stylesheet declares no --edge-hit");
  if (!hitRule) edgeProblems.push("no `.mapsvg .edge .hit` rule found");
  else if (!hitRule[0].includes("var(--edge-hit)"))
    edgeProblems.push("`.mapsvg .edge .hit` does not take its width from var(--edge-hit)");
  else if (!/pointer-events:\s*stroke/.test(hitRule[0]))
    edgeProblems.push("`.mapsvg .edge .hit` does not take pointer events on its stroke");
  const drawn = lnRule && lnRule[0].match(/stroke-width:\s*([\d.]+)/);
  if (!drawn) edgeProblems.push("`.mapsvg .edge .ln` declares no stroke-width");
  else if (hitDecl && Number(hitDecl[1]) < Number(drawn[1]) * 4)
    edgeProblems.push(`--edge-hit is ${hitDecl[1]} against a drawn ${drawn[1]} — not a target`);
  if (lnRule && !/pointer-events:\s*none/.test(lnRule[0]))
    edgeProblems.push("`.mapsvg .edge .ln` still takes pointer events, so the hit line is not the target");
  /* AND A TARGET IS NOT ENOUGH, because six of these edges have no length to
     give one. Coloe → Adulis is 3.9 viewBox units between dots of radius 8 and
     10.5: the line is underneath its own endpoints, and no hit width reaches
     something that is covered. Two more are identical Ganges → Muziris edges
     from different records drawn on top of each other.
     So the claim this guard really wants to make is REACHABILITY, not hit
     width: every drawable edge is listed on the panel of BOTH points it joins,
     and a point is always a pin and always clickable. That is checkable here,
     where a pixel is not. */
  for (const [e, i] of drawableEdges) {
    for (const key of [e.from_key, e.to_key]) {
      const pl = (Object.values(P.docs || {}).flat()).find(x => x.key === key);
      if (!pl || !pl.cache_key) { edgeProblems.push(`edge ${i}: endpoint ${key} has no group`); continue; }
      if (!renderGroupProvenance(pl.cache_key).includes(`data-edge="${i}"`))
        edgeProblems.push(`edge ${i} is not listed on the panel for ${pl.cache_key}`);
    }
  }
  note(edgeProblems.length === 0,
       `every drawable edge (${drawableEdges.length}) is drawn, presents a `
       + `${hitDecl ? hitDecl[1] : "?"}-unit target against a ${drawn ? drawn[1] : "?"}-unit line, `
       + `and is listed on the panel of both points it joins`
       + (edgeProblems.length ? ` — ${edgeProblems.slice(0, 4).join("; ")}` : ""));

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

/* ---- GUARD 48. The Map tab's panel is rendered BESIDE the map, not below the
   whole tab. UI_QUESTIONS_START.md section 3A.

   The defect this exists to stop coming back was measured, not felt: the panel
   sat in the tab's bottom `.cols`, and clicking a marker filled it 7,306 pixels
   below the fold at 1600px and 16,464 below it on a phone.

   WHY THIS IS ASSERTABLE AT ALL, given FINDING 102 ruled that scroll position
   after a click is not the harness's business and no guard was added for it.
   The distinction is that this is not a fact about layout: it is a fact about
   the ORDER of three landmarks in markup the harness already has in a string.
   The CSS turns that order into a column, and the CSS is not what this checks —
   which is why the note below says what it says. A block that keeps the order
   and breaks the stylesheet passes this and fails ui/measure_map.mjs, and both
   of those are correct.

   A RELATION, NOT A PRESENCE. FINDING 105's lesson from the other side: the
   guard it replaced could say a `data-provenance` attribute APPEARED and could
   not see that its value was mangled. Three indexes and two comparisons cannot
   be satisfied by a landmark merely existing. ---- */
{
  const html = viewPlaces();
  const at = needle => html.indexOf(needle);
  const map   = at(`class="maparea"`);
  const guide = at(`id="panel"`);
  const grid  = at(`class="regiongrid"`);
  const found = map >= 0 && guide >= 0 && grid >= 0;
  /* RE-POINTED TWICE NOW, AND RELAXED NEITHER TIME. It read map < panel < grid
     while the Guide was the right-hand column; guide < map < grid while the
     Guide was a band above a full-width map; and map < guide < grid again now
     the columns are back. Three arrangements, one claim, unchanged in all of
     them: THE BOX THAT ANSWERS A CLICK IS ADJACENT TO THE MAP AND IS NEVER AT
     THE FOOT OF THE TAB. Which side it is adjacent on is a design decision;
     being adjacent at all is what section 3A ruled.

     Both re-pointings were seen RED for free, because the restructure landed
     before the guard was touched each time — `288 < 87 < 71231` going one way
     and `35180 < 73 < 71067` coming back. A guard that goes red on a change it
     is supposed to notice, before anybody edits it, is the cheapest evidence
     there is that it was watching. */
  note(found && map < guide && guide < grid,
       `the ${TABS.map} tab renders the map, then the Guide, then the record grid` +
       (found ? ` (${map} < ${guide} < ${grid})`
              : ` — a landmark is missing: map ${map}, guide ${guide}, grid ${grid}`));
}

/* ---- GUARD 49. Every tab that renders a panel has its own empty state, and
   the kinds it advertises are the kinds it can actually select. RULING 90.

   ONE STRING SERVED TWO TABS. The Questions block trimmed it for the Questions
   tab — correctly, for that tab — and the clause naming *a point, a shaded
   region or a line* went with it, leaving the Map tab telling a visitor to
   click things it does not have. Nothing caught that, because every guard on
   this page asserted the panel RENDERED, and it did.

   So this is not a proof-read. It is the SPAN_STATES / PROVENANCE shape: a
   table, and a guard that re-derives the table from the archive — here, from
   the view's own rendered markup. Three claims, and each one is a different
   way for the same defect to come back:

     1  a view that renders a panel and declares no empty state
     2  a view whose declared kinds are not the kinds its markup can select —
        either it advertises a click it cannot answer, or it has GAINED a
        clickable kind and still describes the old set
     3  two views printing the same sentence, which is the original defect
        exactly

   Rendered with `selection` null and `intro` true, because that is the state
   the sentence describes: a visitor who has just arrived and clicked nothing.
   ---- */
{
  /* BY NAME, and the same reason as the render check above: a view missing from
     this list is a view whose empty state nobody checks. Add the fifth the day
     it exists. */
  const VIEWS = [["questions", viewQuestions], ["map", viewPlaces],
                 ["home", viewHome], ["data", viewAbout]];
  const saved = { view: state.view, selection: state.selection, intro: state.intro };
  const problems = [];
  const withPanel = [];
  const seen = new Map();

  for (const [name, fn] of VIEWS) {
    state.view = name; state.selection = null; state.intro = true;
    let html;
    try { html = fn(); }
    catch (e) { problems.push(`${name} threw: ${e.message}`); continue; }
    if (!html.includes(`id="panel"`)) continue;
    withPanel.push(name);

    const entry = PANEL_EMPTY[name];
    if (!entry) { problems.push(`${name} renders a panel and declares no empty state`); continue; }

    // 1. the view prints its OWN declared sentence, verbatim.
    if (!html.includes(entry.html))
      problems.push(`${name}'s panel does not hold the sentence PANEL_EMPTY declares for it`);

    // 3. and nobody else's.
    const prior = seen.get(entry.html);
    if (prior) problems.push(`${name} and ${prior} print the same empty state`);
    seen.set(entry.html, name);

    // 2. declared kinds === kinds this view's markup can actually select.
    const declared = [...entry.selects].sort();
    const present = Object.entries(SELECT_ATTR)
      .filter(([, attr]) => html.includes(`${attr}="`))
      .map(([kind]) => kind).sort();
    const missing = declared.filter(k => !present.includes(k));
    const extra   = present.filter(k => !declared.includes(k));
    if (missing.length)
      problems.push(`${name} advertises ${missing.join(", ")} and its markup emits no such thing`);
    if (extra.length)
      problems.push(`${name} can select ${extra.join(", ")} and its empty state does not say so`);
  }

  Object.assign(state, saved);
  const undeclared = Object.keys(PANEL_EMPTY).filter(v => !withPanel.includes(v));
  if (undeclared.length)
    problems.push(`PANEL_EMPTY declares ${undeclared.join(", ")}, which render no panel`);

  note(problems.length === 0,
       `every tab with a panel has its own empty state, naming what that tab can select` +
       ` (${withPanel.map(v => `${v}: ${PANEL_EMPTY[v] ? PANEL_EMPTY[v].selects.length : 0}`).join(", ")})` +
       (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 50. The map's label size is declared twice and the two agree.

   A place label is the one piece of type on this page that is ALSO A GEOMETRY.
   The browser draws it from `--map-label` in the stylesheet; `buildMap` decides
   which labels fit by solving collisions in viewBox units, using metrics
   derived from `MAP_LABEL_PX` in the script. No expression can be shared
   between a CSS custom property and a script constant, so the size is declared
   in both places — the BANNER pattern, where the specimen list is declared in
   this file and in ui/build_banner.mjs and a check asserts they agree.

   THE FAILURE THIS CATCHES IS SILENT AND LOOKS FINE IN THE SOURCE. Raise the
   CSS value alone and every label is drawn larger than the size the collider
   cleared room for, so names overlap their neighbours and each other — and the
   diff that caused it is one plausible-looking number. Nothing else on the page
   would go red, because every other guard here asserts a label EXISTS.

   WHAT IT DOES NOT COVER, said plainly: this harness has no layout engine, so
   it cannot check that the browser's rendered glyphs match `charW`. It checks
   that the two declarations agree and that the collider's metrics are still
   proportional to the declared size. ui/measure_map.mjs is what reads the type
   the browser actually drew. ---- */
{
  const problems = [];
  const decl = html.match(/--map-label:\s*([\d.]+)px/);
  if (!decl) problems.push("the stylesheet declares no --map-label");
  else if (Number(decl[1]) !== MAP_LABEL_PX)
    problems.push(`the stylesheet says --map-label: ${decl[1]}px and the script says ${MAP_LABEL_PX}`);

  // ...and the rule that draws a label actually reads that token. A token with
  // the right value that nothing uses is FINDING 105's shape: present, and not
  // doing the job it is credited with.
  const rule = html.match(/\.mapsvg \.lbl \{[\s\S]*?\}/);
  if (!rule) problems.push("no `.mapsvg .lbl` rule found");
  else if (!rule[0].includes("var(--map-label)"))
    problems.push("`.mapsvg .lbl` does not take its size from var(--map-label)");

  // The collider's metrics have to follow the declared size rather than having
  // been a matching pair of numbers once.
  const cw = MARK.charW / MAP_LABEL_PX, lh = MARK.lineH / MAP_LABEL_PX;
  if (!(cw > 0.4 && cw < 0.8))
    problems.push(`MARK.charW is ${MARK.charW}, which is ${cw.toFixed(2)}em — not a glyph width`);
  if (!(lh > 1.0 && lh < 1.6))
    problems.push(`MARK.lineH is ${MARK.lineH}, which is ${lh.toFixed(2)}em — not a line height`);

  note(problems.length === 0,
       `the map's label size is declared once in the stylesheet and once in the script, ` +
       `and the collider solves against it (${MAP_LABEL_PX}px, ` +
       `dots ${MARK.dot}/${MARK.dotMulti})` +
       (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 51. The tab bar and the page's own name for each tab agree.

   The page talks about its tabs — on Home, on Data & Sources, in two tooltips
   — and it used to TYPE the name into each sentence. That is a typed count in
   words, and it had already gone wrong: `viewAbout` called it "the Places tab"
   twice, about a tab the bar has labelled "Map" since the design block. Nothing
   noticed, because nothing re-derived it.

   The fix for the PROSE is derivation, not a check: every sentence reads
   `TABS`, so it cannot disagree with `TABS` at all. That leaves exactly one
   second copy to guard — the static tab bar in the header, which has to carry
   its own text because it is on screen during the loading state, before this
   script has run.

   A MATCHER OVER THE PAGE'S PROSE WAS CONSIDERED AND REFUSED. Scanning each
   rendered view for "the <Name> tab" would catch a future block that types a
   name again — and it would also have to decide about "the same tab", "the one
   tab", "this tab", and every phrasing nobody has written yet. RULING 89
   settled that shape: a rule that has to be interpreted is a rule that will be
   broken, and inside a matcher it would be broken silently. Derivation removes
   the failure; this guard covers the one copy derivation cannot.

   THE KEYS ARE CHECKED TOO, and that is the half that catches a fifth tab. A
   tab added to the bar and not to TABS renders a button the page has no name
   for; one added to TABS and not to the bar is a name for a tab nobody can
   reach. ---- */
{
  const problems = [];
  const bar = [...html.matchAll(/<button class="tab"[^>]*data-view="([^"]+)"[^>]*>([^<]*)<\/button>/g)]
    .map(m => [m[1], m[2].trim().replace(/&amp;/g, "&")]);

  if (!bar.length) problems.push("no tab buttons found in the header");

  const barKeys = bar.map(([k]) => k);
  const tabKeys = Object.keys(TABS);
  if (barKeys.join("|") !== tabKeys.join("|"))
    problems.push(`the bar carries [${barKeys.join(", ")}] and TABS declares [${tabKeys.join(", ")}]`);

  for (const [key, label] of bar) {
    if (!(key in TABS)) continue;               // already reported above
    if (TABS[key] !== label)
      problems.push(`the bar says "${label}" for ${key} and TABS says "${TABS[key]}"`);
  }

  note(problems.length === 0,
       `every tab's name is declared once and the header agrees with it ` +
       `(${bar.map(([k, l]) => `${k}: ${l}`).join(", ")})` +
       (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 52. The Guide's trail behaves like a history, and its buttons say
   so.

   Back and forward over the things a reader has opened. RULING 84 exists
   because "two sources of truth for the selected run is how a back button
   starts fighting a click handler", and this is a back button — so the thing
   worth guarding is not that the buttons render, it is that stepping the trail
   WRITES `state.selection` and that the trail never becomes a second opinion
   about what is on screen.

   Every claim below is about a VALUE — which selection is current after a
   sequence of moves — rather than about a control being present. FINDING 105's
   lesson: the guard it replaced could say a state APPEARED and could not say it
   was right.

   The last two are the ones a hand-written back button usually gets wrong: a
   new selection made after stepping back has to DISCARD the forward entries,
   and stepping past either end has to refuse rather than wrap or run off. ---- */
{
  const saved = { sel: state.selection, trail: state.trail, at: state.trailAt };
  const problems = [];
  const A = { kind: "record", docId: "a" };
  const B = { kind: "place",  key: "b" };
  const C = { kind: "group",  cacheKey: "c" };
  const D = { kind: "edge",   idx: 4 };
  const is = (sel, want, why) => {
    if (JSON.stringify(sel) !== JSON.stringify(want)) problems.push(why);
  };

  clearTrail();
  if (canStep(-1) || canStep(1)) problems.push("an empty trail offers a step");
  if (!/disabled/.test(panelNav()) || panelNav().match(/disabled/g).length !== 2)
    problems.push("an empty trail does not draw both buttons disabled");

  [A, B, C].forEach(pushSelection);
  if (state.trail.length !== 3) problems.push(`three pushes made ${state.trail.length} entries`);
  if (canStep(1)) problems.push("the newest entry offers a forward step");
  if (!canStep(-1)) problems.push("the newest entry offers no way back");

  // pushing the same thing twice is not a step
  pushSelection(C);
  if (state.trail.length !== 3) problems.push("re-opening the same thing added an entry");

  stepSelection(-1); stepSelection(-1);
  is(state.selection, A, "two steps back did not land on the first entry");
  if (canStep(-1)) problems.push("the first entry offers a further step back");
  if ((panelNav().match(/disabled/g) || []).length !== 1)
    problems.push("at the start of the trail, exactly one button should be disabled");

  if (stepSelection(-1) !== false) problems.push("stepping past the start was allowed");
  is(state.selection, A, "a refused step still moved the selection");

  /* AND THE OTHER END, which this guard did not cover until a red test found
     the hole: `if (to < 0) return false` passes every assertion above and lets
     a forward step run off the end of the trail. Both ends, or neither. */
  stepSelection(1); stepSelection(1);
  is(state.selection, C, "two steps forward did not land on the newest entry");
  if (stepSelection(1) !== false) problems.push("stepping past the end was allowed");
  is(state.selection, C, "a refused forward step still moved the selection");
  // back to the first entry, so the step below still means what it meant before
  // this pair of checks was inserted between them.
  stepSelection(-1); stepSelection(-1);
  is(state.selection, A, "walking to the end and back did not return to the first entry");

  stepSelection(1);
  is(state.selection, B, "a forward step did not land on the second entry");

  // a new selection from the middle abandons the branch that was ahead
  pushSelection(D);
  if (state.trail.length !== 3) problems.push(`a new selection left ${state.trail.length} entries, not 3`);
  is(state.trail[2], D, "the new selection is not the newest entry");
  if (canStep(1)) problems.push("a new selection left a forward step available");
  is(state.selection, B, "pushing a selection changed what is on screen by itself");

  Object.assign(state, { selection: saved.sel, trail: saved.trail, trailAt: saved.at });

  note(problems.length === 0,
       `the Guide's trail steps back and forward and refuses both ends` +
       (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 53. Every figure in the geography ledger is re-derived, and the
   ledger is on the tab that claims it.

   Seven derived figures — drawn, placements, gaps, and the four cells — stood
   at the top of the Map tab for the whole of this project's life with NOTHING
   RE-DERIVING ONE OF THEM. That is the shape FINDING 105 had on the
   cross-tabulation: every guard in force asserted that a thing was rendered,
   and none could see that a number in it was wrong. The ledger has moved to
   Methodology, and RULING 88's test for a move is that the guard moves with it
   and gets no weaker — so this is the guard it never had.

   TWO CLAIMS, and the second is the one that makes the first worth having:

     1  every figure the ledger prints equals what `placeLedger()` derives now
     2  the ledger is rendered on the Methodology tab and NOT on Map & Sources

   Without (2) a later block could quietly restore it to the map, or print it on
   both, and (1) would stay green on either. Home promises that "places the map
   will not draw are counted and shown"; this is where the page keeps that
   promise, and a guard that could not say WHERE would be asserting the promise
   is kept somewhere. ---- */
{
  const problems = [];
  const L = placeLedger();
  const html = placeNotice();

  const attr = (name, want, why) => {
    const m = html.match(new RegExp(`${name}="(\\d+)"`));
    if (!m) problems.push(`${why}: not machine-readable on the ledger`);
    else if (Number(m[1]) !== want) problems.push(`${why}: prints ${m[1]}, derives ${want}`);
  };
  attr("data-ledger-drawn", L.groups, "points and extents drawn");
  attr("data-ledger-placements", L.placements, "placements");
  attr("data-ledger-gaps", L.gaps.length, "placements not drawn");

  for (const [cell, want] of [["gaps", L.gaps.length],
                              ["gapsNoId", L.gapsNoId.length],
                              ["gapsIdNoGeometry", L.gapsIdNoGeometry.length],
                              ["docsAllGap", L.docsAllGap.length]]) {
    const m = html.match(new RegExp(`data-cell="${cell}" data-count="(\\d+)"`));
    if (!m) problems.push(`the ${cell} cell is not on the ledger`);
    else if (Number(m[1]) !== want) problems.push(`the ${cell} cell prints ${m[1]}, derives ${want}`);
    // ...and the figure a reader SEES, not only the attribute beside it. An
    // attribute that agrees with the arithmetic while the visible number does
    // not is FINDING 105 with the axes swapped.
    else if (!new RegExp(`data-cell="${cell}"[^>]*>\\s*<div class="num">${want}<`).test(html))
      problems.push(`the ${cell} cell's printed number is not the one it declares`);
  }

  const onMethodology = viewAbout().includes(`data-ledger-drawn="${L.groups}"`);
  const onMap = viewPlaces().includes("data-ledger-drawn");
  if (!onMethodology) problems.push(`the ledger is not on the ${TABS.data} tab`);
  if (onMap) problems.push(`the ledger is on the ${TABS.map} tab as well`);

  note(problems.length === 0,
       `every figure in the geography ledger is re-derived, on ${TABS.data} and only there ` +
       `(${L.groups} drawn of ${L.placements}, ${L.gaps.length} not)` +
       (problems.length ? ` — ${problems.join("; ")}` : ""));
}


/* ================================================================= *
 * THE REGION BANDS. GUARDS 54 TO 57.
 *
 * A band is the one thing on this map that is NOT a cached coordinate, so it is
 * the one thing on this map that could quietly become a hand-placed one. These
 * four exist to make that impossible to do silently, and each was seen RED on a
 * broken version before it was believed — `UI_MAP_RESULT.md` section 4 is why:
 * a guard written to check both ends of the Guide's trail checked one of them,
 * and only breaking the code found it.
 * ================================================================= */

/* ---- GUARD 54. Every record the map cannot draw as a point is a square in a
   band, exactly once — and every square in a band is such a record.

   BOTH DIRECTIONS, and the second is the one that matters. The first says
   nothing was dropped. The second says the map is not quietly showing a record
   in a band that it ALSO draws as a point, which would double-count the corpus
   and make the arithmetic in the ledger false while every figure in it still
   agreed with itself. ---- */
{
  const homeless = new Set(Object.keys(D.corpus).filter(
    id => !((P.docs || {})[id] || []).some(e => e.kind !== "gap")));
  const svg = buildMap();
  const chips = [...svg.matchAll(/class="chip[^"]*" data-record="([^"]+)"/g)].map(m => m[1]);
  const seen = new Set(chips);
  const dupes = chips.length - seen.size;
  const missing = [...homeless].filter(id => !seen.has(id));
  const extra = [...seen].filter(id => !homeless.has(id));
  const problems = [];
  if (dupes) problems.push(`${dupes} record(s) drawn in more than one band`);
  if (missing.length) problems.push(`not on the map at all: ${missing.slice(0, 4).join(", ")}`);
  if (extra.length) problems.push(`in a band and also drawn as a point: ${extra.slice(0, 4).join(", ")}`);
  note(problems.length === 0,
       `every record the map cannot draw as a point is a square in its region's band `
       + `(${chips.length} squares, ${homeless.size} such records)`
       + (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 55. A band is placed EITHER by derivation from its own region's
   cached findspots, OR by a declaration that says so on screen.

   RULING 88's test for re-pointing a guard is that the new claim is at least as
   strong as the old one. The old claim was "every band derives its position
   from its own region's cached findspots". That claim is KEPT, unchanged, for
   every band that is not declared — the anchor is recomputed here from `P.docs`
   independently of the page, so a later block still cannot swap findspots for
   subject places, widen it to "any placement", or type a coordinate in.

   FOUR OBLIGATIONS ARE ADDED for the declared one, and they are the price of
   being allowed to declare at all:

     1  the region a declaration names EXISTS in the corpus — a typo'd region
        key would otherwise sit in the file doing nothing, forever
     2  the declaration carries a REASON, and it is not empty
     3  the band's own panel says "declared, not derived" IN THOSE WORDS, and
        prints the reason
     4  the panel ALSO prints the derived position the declaration overrules, so
        a reader can see what the corpus would have said

   (3) and (4) are the whole safeguard. A declared anchor that rendered like a
   derived one would be the worst thing this file could contain: every other
   position on this map traces to a cached gazetteer id, and a reader has no way
   to tell a judgement from a derivation unless the page says which it is.

   AND A DECLARED ANCHOR HAS TO BE INSIDE THE MAP'S OWN WINDOW. `mapBase` fits
   the window to the coordinates the map draws, and band anchors were not among
   them until this block — an anchor outside the window cannot be placed at all
   and falls silently to the crowded fallback, which is a declaration that does
   nothing while appearing to do something. ---- */
{
  const want = new Map();
  for (const entries of Object.values(P.docs || {}))
    for (const e of entries) {
      if (e.kind === "gap" || e.block !== "findspot_places") continue;
      const region = (D.corpus[e.doc_id] || {}).region;
      const g = region && (P.groups || []).find(x => x.cache_key === e.cache_key);
      if (!g) continue;
      const xy = g.kind === "pin" ? g.resolved.point
        : [(g.resolved.bbox[0] + g.resolved.bbox[2]) / 2, (g.resolved.bbox[1] + g.resolved.bbox[3]) / 2];
      /* KEYED BY CACHE_KEY, so a site three records share counts once. The
         page counts distinct sites and the harness counted placements, and this
         guard went red on the difference — which is what an independent
         re-derivation is for. */
      if (!want.has(region)) want.set(region, new Map());
      want.get(region).set(e.cache_key, xy);
    }
  const centre = ps => [
    (Math.min(...ps.map(q => q[0])) + Math.max(...ps.map(q => q[0]))) / 2,
    (Math.min(...ps.map(q => q[1])) + Math.max(...ps.map(q => q[1]))) / 2];
  const svg = buildMap();
  const view = mapWindow();
  const problems = [];
  let derivedN = 0, declaredN = 0;

  // (1) a declaration naming a region the corpus does not have does nothing.
  const regions = new Set(Object.values(D.corpus).map(r => r.region));
  for (const region of Object.keys(REGION_ANCHOR)) {
    if (!regions.has(region))
      problems.push(`REGION_ANCHOR declares "${region}", which is not a region in this corpus`);
    const why = (REGION_ANCHOR[region] || {}).why;
    if (!why || !why.trim()) problems.push(`${region}: declared with no reason given`);
  }

  for (const b of regionBands()) {
    const ps = want.has(b.region) ? [...want.get(b.region).values()] : null;
    // The DERIVATION is checked for every band, declared or not — a declaration
    // overrules where the band is drawn and never what the corpus would say.
    if (ps) {
      const [wx, wy] = centre(ps);
      if (!b.derived || Math.abs(b.derived[0] - wx) > 1e-9 || Math.abs(b.derived[1] - wy) > 1e-9)
        problems.push(`${b.region}: derived anchor ${b.derived} is not the centre of its findspots ${[wx, wy]}`);
      if (b.findspots !== ps.length)
        problems.push(`${b.region}: says ${b.findspots} findspots, derives ${ps.length}`);
    } else if (b.derived) {
      problems.push(`${b.region}: a derived anchor with no cached findspot of its own`);
    }

    if (b.anchorKind === "declared") {
      declaredN++;
      const panel = renderRegionProvenance(b.region);
      if (b.anchor !== b.declared.point)
        problems.push(`${b.region}: declared, and its anchor is not the declared point`);
      /* AND IT IS DRAWN THERE. The anchor being right while the placer moved
         the band somewhere else is exactly the defect this caught: a
         declaration that gets nudged is not a declaration. */
      const laidHere = layoutBands(view).find(o => o.band.region === b.region);
      if (laidHere && laidHere.drawn && view) {
        const cx = (b.anchor[0] - view.lonMin) / (view.lonMax - view.lonMin) * view.W;
        const cy = view.H - (b.anchor[1] - view.latMin) / (view.latMax - view.latMin) * view.H;
        if (Math.abs(laidHere.x + laidHere.w / 2 - cx) > 0.5
         || Math.abs(laidHere.y + laidHere.h / 2 - cy) > 0.5)
          problems.push(`${b.region}: declared, and the placer moved the band off the declared point`);
      }
      if (!/declared, not derived/.test(panel))
        problems.push(`${b.region}: declared, and its panel does not say so`);
      if (!panel.includes(b.declared.why.replace(/\s+/g, " ").trim().slice(0, 40)))
        problems.push(`${b.region}: declared, and its panel does not print the reason`);
      if (b.derived && !panel.includes(b.derived[1].toFixed(2)))
        problems.push(`${b.region}: declared, and its panel does not print the derivation it overrules`);
      if (!mapLegend().includes(b.region))
        problems.push(`${b.region}: declared, and the legend still says every band's position is derived`);
      if (view && (b.anchor[0] < view.lonMin || b.anchor[0] > view.lonMax
                || b.anchor[1] < view.latMin || b.anchor[1] > view.latMax))
        problems.push(`${b.region}: declared at ${b.anchor}, which is outside the map's own window`);
    } else {
      derivedN++;
      if (ps && b.anchor !== b.derived)
        problems.push(`${b.region}: not declared, and not placed on its derivation`);
    }
  }

  /* AND A BAND THAT COULD NOT SIT ON ITS ANCHOR SAYS SO. `layoutBands` gives up
     after two rings and clamps to the anchor rather than walking out of the
     region, so a crowded band overlaps the markers it could not avoid — which a
     reader can see and cannot explain. The panel explains it, and this is what
     stops the explanation being dropped the next time the panel is rewritten. */
  const laid = layoutBands(view);
  let crowded = 0;
  for (const o of laid) {
    if (!o.drawn || !o.crowded) continue;
    crowded++;
    if (!svg.includes(`data-region="${o.band.region}" data-crowded="1"`))
      problems.push(`${o.band.region}: crowded, and the map does not mark it`);
    if (!/No room at its anchor/.test(renderRegionProvenance(o.band.region)))
      problems.push(`${o.band.region}: crowded, and its own panel does not say so`);
  }
  note(problems.length === 0,
       `every band is placed on its own region's cached findspots, or on a declaration that says so `
       + `on screen (${derivedN} derived, ${declaredN} declared, `
       + `${crowded} with no room at the anchor and saying so)`
       + (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 56. A band's plate is the size its contents declare, AND the size
   it is declared to hold is the size the browser draws.

   THE FIRST VERSION OF THIS GUARD WAS WORTHLESS AND ONLY BREAKING THE CODE SAID
   SO. It recomputed the plate's width from `BAND.nameCharW` — the same constant
   `buildMap` draws with — so the two moved together and the guard saw nothing.
   Setting `nameCharW` back to the 6.6 that had actually shipped the defect, the
   longest region name running off its own plate, left this GREEN. It caught a
   hand-edited rectangle and could not catch the one thing that had gone wrong.
   Same hole as guard 52's, found the same way, and this is the second time on
   this project that a red test found the hole in the guard rather than in the
   code.

   So the band's type size is declared TWICE now — `--band-label` in the
   stylesheet and `BAND.namePx` in the script — exactly as `--map-label` and
   `MAP_LABEL_PX` are, and for exactly the same reason: the browser draws the
   name and this file sizes the plate to hold it, and no expression can be
   shared between them. The width is derived from a RATIO of that size, so the
   ratio is a number a reader can argue with rather than a width that agrees
   with itself.

   WHAT IT STILL DOES NOT COVER, said plainly, because guard 50 says it too:
   this harness has no layout engine and cannot measure a glyph. It checks that
   the two declarations agree, that the rule drawing the name reads the token,
   that the ratio is a plausible glyph width for tracked uppercase, and that
   every plate is the size its own contents declare. `ui/measure_map.mjs` and
   looking at the page are what read the type the browser actually drew. ---- */
{
  const svg = buildMap();
  const problems = [];
  let checked = 0;

  const decl = html.match(/--band-label:\s*([\d.]+)px/);
  if (!decl) problems.push("the stylesheet declares no --band-label");
  else if (Number(decl[1]) !== BAND.namePx)
    problems.push(`the stylesheet says --band-label: ${decl[1]}px and the script says ${BAND.namePx}`);
  const rule = html.match(/\.mapsvg \.band \.bname \{[\s\S]*?\}/);
  if (!rule) problems.push("no `.mapsvg .band .bname` rule found");
  else if (!rule[0].includes("var(--band-label)"))
    problems.push("`.mapsvg .band .bname` does not take its size from var(--band-label)");
  if (!(BAND.nameRatio > 0.62 && BAND.nameRatio < 0.85))
    problems.push(`BAND.nameRatio is ${BAND.nameRatio}, which is not a tracked-uppercase glyph width`);
  if (Math.abs(BAND.nameCharW - BAND.namePx * BAND.nameRatio) > 1e-9)
    problems.push(`BAND.nameCharW is ${BAND.nameCharW} and does not follow namePx x nameRatio`);

  /* The band's own chunk of the SVG, found by splitting rather than by a
     constructed RegExp. The first version of this guard built its pattern with
     `new RegExp(\`...[\\s\\S]*?...\`)`, and a template literal eats the
     backslash — so the pattern the harness actually compiled contained `[sS]`
     and matched nothing, and the guard reported that no band had a plate at
     all. It went red on its FIRST run, which is the only reason it is right
     now, and it is the same lesson as guard 52: the check is the thing being
     tested. */
  const chunkOf = region => {
    /* The key stops at the closing quote, NOT at the closing angle bracket. It
       used to include the `>`, and the day a band gained a second attribute —
       `data-crowded` — every crowded band reported "no plate drawn". The guard
       was right to go red and right about nothing: it was reading its own
       pattern, not the page. */
    const key = `<g class="band" data-region="${region}"`;
    const at = svg.indexOf(key);
    if (at < 0) return null;
    const rest = svg.slice(at + key.length);
    const next = rest.indexOf('<g class="band" data-region="');
    return next < 0 ? rest : rest.slice(0, next);
  };
  for (const b of regionBands()) {
    if (!b.anchor) continue;
    const chunk = chunkOf(b.region);
    const m = chunk && chunk.match(/class="plate"[^>]*?width="([\d.]+)"\s+height="([\d.]+)"/);
    if (!m) { problems.push(`${b.region}: no plate drawn`); continue; }
    const box = bandBox(b.members.length, b.region);
    if (Math.abs(Number(m[1]) - box.w) > 0.05)
      problems.push(`${b.region}: plate is ${m[1]} wide, ${b.members.length} record(s) and a `
        + `${box.lines.length}-line name declare ${box.w.toFixed(1)}`);
    // The name has to FIT the plate it sized, line by line.
    for (const line of box.lines)
      if (line.length * BAND.nameCharW > box.w - BAND.pad * 2 + 0.05)
        problems.push(`${b.region}: the line "${line}" is wider than its own plate`);
    if (Math.abs(Number(m[2]) - box.h) > 0.05)
      problems.push(`${b.region}: plate is ${m[2]} tall, declares ${box.h.toFixed(1)}`);
    checked++;
  }
  note(problems.length === 0,
       `every band is drawn the size its contents declare, and its name's size is `
       + `declared once in the stylesheet and once in the script (${checked} bands, `
       + `${BAND.namePx}px names, ${BAND.chip}u squares ${BAND.perRow} to a row)`
       + (problems.length ? ` — ${problems.join("; ")}` : ""));
}

/* ---- GUARD 57. THE WHOLE CORPUS REACHES THE MAP, and the ledger says the same
   number this does.

   `UI_MAP_REGIONS_START.md` opened on 32 of 54, and this is the check that the
   answer to it is real rather than rendered. Points and squares must PARTITION
   the corpus: every record in exactly one of them, nothing in both, nothing in
   neither. The ledger on Methodology prints the same two figures and they are
   re-derived here, because a page that draws 54 and prints 40 is worse than one
   that draws 40. ---- */
{
  const svg = buildMap();
  const drawnIds = new Set();
  for (const [id, entries] of Object.entries(P.docs || {}))
    if (entries.some(e => e.kind !== "gap")) drawnIds.add(id);
  const chips = new Set([...svg.matchAll(/class="chip[^"]*" data-record="([^"]+)"/g)].map(m => m[1]));
  const all = Object.keys(D.corpus);
  const both = all.filter(id => drawnIds.has(id) && chips.has(id));
  const neither = all.filter(id => !drawnIds.has(id) && !chips.has(id));
  const B = bandLedger();
  const html = placeNotice();
  const problems = [];
  if (both.length) problems.push(`${both.length} record(s) drawn twice`);
  if (neither.length) problems.push(`${neither.length} record(s) reach the map at all: ${neither.slice(0, 4).join(", ")}`);
  if (B.inBands !== chips.size) problems.push(`the ledger counts ${B.inBands} in bands, the map draws ${chips.size}`);
  if (B.asPoints !== drawnIds.size) problems.push(`the ledger counts ${B.asPoints} as points, the map draws ${drawnIds.size}`);
  for (const [attr, wantN] of [["data-band-records", B.inBands], ["data-band-points", B.asPoints]]) {
    const m = html.match(new RegExp(`${attr}="(\\d+)"`));
    if (!m) problems.push(`${attr} is not machine-readable on the ledger`);
    else if (Number(m[1]) !== wantN) problems.push(`${attr} prints ${m[1]}, derives ${wantN}`);
  }
  note(problems.length === 0,
       `all ${all.length} records reach the map — ${drawnIds.size} as points, ${chips.size} as squares in a band`
       + (problems.length ? ` — ${problems.join("; ")}` : ""));
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

/* ---- 2f-ii. RULING 89: the note a record shows is the curator's own words ----
 *
 * The notes in `data/seed_corpus/` are working documents — which tranche placed
 * the record, which ruling bought its slot, which prediction it tests — wrapped
 * around the best writing in this project about what each source actually is.
 * The page shows only the second part, as VERBATIM EXCERPTS declared in
 * `PUBLIC_NOTES` and sliced out by `ui/build_public_notes.py` rather than
 * retyped.
 *
 * This asserts the property that makes that safe: every fragment on the page is
 * still a substring of the note it came from, whitespace aside. A note edited
 * underneath an excerpt goes RED here instead of the page quietly attributing
 * to a curator a sentence they no longer hold.
 *
 * And a record with NO entry is a failure rather than a blank: the defect this
 * exists to catch is a record curated later whose whole note reaches the screen
 * because nobody looked at it. An entry declared empty is fine — that is
 * somebody having looked. ---- */
{
  const flat = t => String(t).replace(/\s+/g, " ").trim();
  const undeclared = [], drifted = [], blank = [];
  for (const [docId, rec] of Object.entries(D.corpus)) {
    if (!(docId in PUBLIC_NOTES)) { undeclared.push(docId); continue; }
    const note = flat(rec.notes || "");
    for (const frag of PUBLIC_NOTES[docId]) {
      if (!flat(frag)) { blank.push(docId); continue; }
      if (!note.includes(flat(frag)))
        drifted.push(`${docId}: "${flat(frag).slice(0, 60)}…" is not in the record's note`);
    }
  }
  const shown = Object.values(PUBLIC_NOTES).filter(f => f.length).length;
  const frags = Object.values(PUBLIC_NOTES).reduce((n, f) => n + f.length, 0);
  note(undeclared.length === 0 && drifted.length === 0 && blank.length === 0,
       undeclared.length || drifted.length || blank.length
         ? `a record note on screen is not the curator's — `
           + `${undeclared.length} record(s) with no declaration`
           + (undeclared.length ? ` (e.g. ${undeclared[0]})` : "")
           + `, ${drifted.length} drifted`
           + (drifted.length ? ` (${drifted[0]})` : "")
           + `, ${blank.length} blank`
         : `every record note shown is a verbatim excerpt of that record's own note `
           + `(${frags} fragments across ${shown} of ${Object.keys(D.corpus).length} records)`);
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
