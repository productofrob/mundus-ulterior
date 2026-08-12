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
    "\n;globalThis.__api = { D, byQuestion, QUESTIONS, state, renderAnswerText," +
    " renderQuoteProvenance, renderPassageProvenance, renderRecordProvenance," +
    " viewQuestions, viewRegions, viewAbout };",
    sandbox, { filename: "index.html<script>" });
  note(true, "the page's script parses and runs to completion");
} catch (e) {
  note(false, `the page's script threw: ${e.message}`);
  console.log(e.stack);
  process.exit(1);
}

const { D, byQuestion, QUESTIONS, state, renderAnswerText,
        renderQuoteProvenance, renderPassageProvenance,
        renderRecordProvenance, viewQuestions, viewRegions,
        viewAbout } = sandbox.__api;

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
try { viewRegions(); viewAbout(); note(true, "regions and about views render"); }
catch (e) { note(false, `a view threw: ${e.message}`); }

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
const tally = { resolved: 0, case_only: 0, moved: 0, absent: 0 };
for (const run of D.runs)
  for (const s of run.grounding?.quote_spans || [])
    if (s.resolution) tally[s.resolution.state]++;
const audit = D.span_audit || {};
note(["resolved", "case_only", "moved", "absent"].every(k => tally[k] === (audit[k] || 0)),
     `the headline audit matches the spans: ${JSON.stringify(tally)}`);

console.log();
if (fail.length) {
  console.log(`${fail.length} check(s) failed:`);
  for (const f of fail) console.log("  - " + f);
  process.exit(1);
}
console.log("all checks passed");
