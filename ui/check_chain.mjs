/*
 * G1 criterion 4: one traversal from a drawn map marker to characters in a
 * seed file on disk, asserting at each hop that the next one is REACHABLE.
 *
 *     node ui/check_chain.mjs
 *
 * Why this is a separate file from check_ui.mjs
 * ---------------------------------------------
 * `check_ui.mjs` already asserts every hop of this chain separately: 51 cached
 * points are drawn, 24 record panels build, 89 placements appear on their own
 * record's panel, every quotation in an answer is highlighted, and all 157
 * `resolved` spans hold their quoted characters. All of it passes.
 *
 * None of it asserts the hops CONNECT. This repository has paid for that
 * distinction four times — PROGRESS.md's standing lesson, *an assertion about
 * presence says nothing about correctness* — and most expensively when the map
 * plotted all 49 points correctly onto an inverted planet with 20/20 green.
 *
 * It is also separate so that its headline number cannot hide. The chain is
 * complete for 6 of 24 documents. A green check over six records reads exactly
 * like a green check over twenty-four, and buried as line 24 of check_ui.mjs
 * that is what it would read like. Here it is the only number on the page.
 *
 * What it asserts, and what it does not
 * -------------------------------------
 * "no dead link" — every chain that EXISTS is unbroken. Not "every record
 * completes the chain": that is unreachable today (12 records are drawn but
 * never quoted, 2 are quoted but draw nothing, 4 are neither) and would be
 * satisfiable only by weakening what "quotation" means. So the shortfall is
 * counted and named, in the house pattern of the `unrenderable` and
 * `date_holes` reports — report it, do not fail on it.
 *
 * The one thing it does hard-fail on is a chain count of zero. A chain check
 * with nothing to traverse asserts nothing while printing green, which is the
 * failure this file exists to stop trusting.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";
import vm from "node:vm";

const UI = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(UI);

const fail = [];
const note = (ok, msg) => { console.log(`  ${ok ? "ok  " : "FAIL"}  ${msg}`);
                            if (!ok) fail.push(msg); };

/* ---- 0. the bundle is not older than the evidence ----
 *
 * Same guard, and the same reason, as check_ui.mjs section 0: a checker that
 * validates whatever it is handed will certify a stale artefact without
 * complaint. This file traverses from data.js to files on disk, so a stale
 * bundle here does not merely make the counts wrong — it makes the last hop
 * compare a bundled offset against a seed file that has since moved under it.
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
    try { walk(join(ROOT, dir)); } catch { /* absent directory is not this check's business */ }
  }
  note(newer.length === 0,
       newer.length === 0
         ? "ui/data.js is at least as new as every archived run and seed record"
         : `ui/data.js is STALE — ${newer.length} file(s) changed after it was built ` +
           `(e.g. ${newer.slice(0, 3).map(p => relative(ROOT, p)).join(", ")}). ` +
           `Run: python ui/build_ui_data.py`);
  if (newer.length) {
    console.log("\nStopping: the last hop would compare a bundled offset against a seed file that has moved.");
    process.exit(1);
  }
}

/* ---- 1. load the page exactly as a browser would ---- */
const html = readFileSync(join(UI, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (scripts.length !== 1) {
  console.log(`  FAIL  index.html has exactly one inline script (found ${scripts.length})`);
  process.exit(1);
}

const el = () => ({ innerHTML: "", scrollTop: 0, dataset: {},
                    setAttribute() {}, closest: () => null });
const sandbox = {
  console,
  window: {},
  document: { getElementById: el, querySelectorAll: () => [], addEventListener() {}, createElement: el },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(readFileSync(join(UI, "data.js"), "utf8"), sandbox, { filename: "data.js" });
vm.runInContext(
  scripts[0] +
  "\n;globalThis.__api = { D, P, state, renderQuoteProvenance," +
  " renderRecordProvenance, renderPlaceProvenance, renderGroupProvenance, buildMap };",
  sandbox, { filename: "index.html<script>" });

const { D, P, state, renderQuoteProvenance, renderRecordProvenance,
        renderPlaceProvenance, renderGroupProvenance, buildMap } = sandbox.__api;

/* ---- 2. the far end of the chain: seed files on disk ----
 *
 * The chain does not end in data.js. data.js is the bundle this whole page is
 * built from, so checking a quotation against it only proves the bundle is
 * self-consistent — the builder could have written both halves wrong together.
 * The last hop reads the seed JSON off disk and indexes it directly, which is
 * the only assertion here that data.js cannot satisfy on its own.
 *
 * The file it opens is the one `D.corpus[doc_id].file` names — NOT one found
 * by scanning the seed directory for a matching `id`. That distinction is the
 * whole hop. `renderQuoteProvenance` prints `rec.file` to the user under a
 * heading that reads "the characters on disk", so that path is a claim the
 * page makes on screen. A check that located the seed file independently would
 * happily validate characters in a file the page never names, and the page
 * could point at anything while this stayed green.
 */
const seedCache = new Map();
const seedOf = (relPath) => {
  if (!seedCache.has(relPath)) {
    let parsed = null;
    try { parsed = JSON.parse(readFileSync(join(ROOT, relPath), "utf8")); } catch { parsed = null; }
    seedCache.set(relPath, parsed);
  }
  return seedCache.get(relPath);
};

/* ---- 3. index the two graphs, joined on doc_id ---- */

// Map side. A group entry is not a marker: the marker is what buildMap()
// actually emits, so drawnness is read off the SVG the page would render.
const svg = buildMap();
const drawnGroups = (P.groups || []).filter(g => svg.includes(`data-group="${g.cache_key}"`));
const drawnDocs = new Set();
for (const g of drawnGroups) for (const m of g.members) drawnDocs.add(m.doc_id);

// Answer side. Only `resolved` and `case_only` are live links.
//
// `moved` and `absent` are excluded BY NAME, with the reason. Both predate A5,
// both are in africa-03-periplus-adulis, and both are explained on the About
// tab. A chain check that counts them as dead links fails on a phenomenon the
// page already documents; one that drops them silently hides the only two
// genuinely broken citations in the archive. Neither is acceptable, so they
// are listed on screen as known-broken and excluded from the traversal.
const LIVE = new Set(["resolved", "case_only"]);
const excluded = [];
const spansByDoc = new Map();
for (const run of D.runs) {
  const spans = run.grounding?.quote_spans || [];
  for (let i = 0; i < spans.length; i++) {
    const sp = spans[i], st = sp.resolution?.state;
    if (!LIVE.has(st)) { if (st) excluded.push({ ...sp, state: st }); continue; }
    if (!spansByDoc.has(sp.doc_id)) spansByDoc.set(sp.doc_id, []);
    spansByDoc.get(sp.doc_id).push({ run, index: i, span: sp, state: st });
  }
}
const quotedDocs = new Set(spansByDoc.keys());

const allDocs = Object.keys(D.corpus);
const fullChain     = allDocs.filter(d =>  drawnDocs.has(d) &&  quotedDocs.has(d)).sort();
const drawnNotQuoted = allDocs.filter(d =>  drawnDocs.has(d) && !quotedDocs.has(d)).sort();
const quotedNotDrawn = allDocs.filter(d => !drawnDocs.has(d) &&  quotedDocs.has(d)).sort();
const neither        = allDocs.filter(d => !drawnDocs.has(d) && !quotedDocs.has(d)).sort();

/* ---- 4. the traversal ----
 *
 * Every assertion below is on REACHABILITY through the data the renderer was
 * given, never on a substring of the markup it returned. Checking that
 * `renderRecordProvenance` output *contains* a doc_id is the presence
 * assertion this entire file exists to stop trusting: the marker could be
 * anywhere in 40KB of HTML, attached to nothing.
 */
// `paths` counts complete marker-to-disk traversals, not quotations: a record
// reachable from three markers has three chains through it, and each is checked
// on its own account. `reached` is the distinct quotations those paths land on,
// printed alongside so the larger number cannot be mistaken for corpus size.
let markers = 0, members = 0, paths = 0;
const reached = new Set();     // distinct quotations arrived at
const traversed = new Set();   // doc_ids walked all the way to disk
const broken = { member: [], record: [], placement: [], panel: [], quote: [], chars: [] };

for (const g of drawnGroups) {
  markers++;

  // Hop 1 -> 2. A marker resolves to a group with N members, and the chain
  // passes through a CHOSEN member. Assert every one of them: checking only
  // the first passes on a four-member pin while saying nothing about three of
  // its records.
  for (const m of g.members) {
    members++;

    // Hop 2 -> 3: member -> record.
    if (!D.corpus[m.doc_id]) { broken.member.push(`${g.cache_key} -> ${m.doc_id} (no corpus entry)`); continue; }

    // The member must be one of the placements the record itself carries,
    // by key — otherwise the marker leads to a record that does not claim it.
    const placements = (P.docs || {})[m.doc_id] || [];
    if (!placements.some(p => p.key === m.key))
      broken.placement.push(`${g.cache_key} -> ${m.key} (not on ${m.doc_id}'s placement list)`);

    try { renderRecordProvenance(m.doc_id); }
    catch (e) { broken.record.push(`${m.doc_id}: ${e.message}`); continue; }
    try { renderPlaceProvenance(m.key); renderGroupProvenance(g.cache_key); }
    catch (e) { broken.panel.push(`${m.key}: ${e.message}`); continue; }

    // Hop 3 -> 4: record -> quotation. Not every record is quoted; that is the
    // counted shortfall, not a dead link, so an unquoted record ends here.
    for (const { run, index, span, state: spanState } of spansByDoc.get(m.doc_id) || []) {

      state.question = run.question;
      try { renderQuoteProvenance(run, index); }
      catch (e) { broken.quote.push(`${m.doc_id} ${run.run_key}#${index}: ${e.message}`); continue; }

      // Hop 4 -> 5: quotation -> the file the PAGE names -> characters in it.
      //
      // `rec.file` is what renderQuoteProvenance prints on screen under "the
      // characters on disk". Travelling through it is what makes this a chain
      // rather than two separate facts: the file the user is shown and the
      // file these characters are in have to be the same file.
      const relPath = D.corpus[span.doc_id]?.file;
      if (typeof relPath !== "string") {
        broken.chars.push(`${span.doc_id}: the record names no source file`);
        continue;
      }
      const seed = seedOf(relPath);
      if (!seed) { broken.chars.push(`${span.doc_id}: ${relPath} is not readable on disk`); continue; }
      if (seed.id !== span.doc_id) {
        broken.chars.push(`${span.doc_id}: ${relPath} holds record '${seed.id}'`);
        continue;
      }
      const text = seed[span.source_field];
      if (typeof text !== "string") {
        broken.chars.push(`${relPath} has no '${span.source_field}' field`);
        continue;
      }
      let found = text.slice(span.abs_start, span.abs_end);
      let quote = (span.quote || "").trim();

      // `case_only` means exactly this: the characters are there and the case
      // differs. Comparing it case-sensitively would report the nine spans the
      // audit already classifies correctly as nine dead links.
      if (spanState === "case_only") { found = found.toLowerCase(); quote = quote.toLowerCase(); }

      if (!(found && (found.includes(quote) || quote.includes(found)))) {
        broken.chars.push(
          `${relPath} ${span.source_field}[${span.abs_start}:${span.abs_end}] ` +
          `holds ${JSON.stringify(found.slice(0, 40))}, not the quote`);
        continue;
      }
      paths++;
      reached.add(`${run.run_key}#${index}`);
      traversed.add(m.doc_id);
    }
  }
}

/* ---- 5. report ---- */
console.log();
note(broken.member.length === 0,
     `every drawn marker's member resolves to a seed record (${members} members of ${markers} markers)` +
     (broken.member.length ? ` — ${broken.member.slice(0, 3).join("; ")}` : ""));
note(broken.placement.length === 0,
     `every member is on its own record's placement list (${members} checked)` +
     (broken.placement.length ? ` — ${broken.placement.slice(0, 3).join("; ")}` : ""));
note(broken.record.length === 0 && broken.panel.length === 0,
     `every record and place panel on the chain builds` +
     ([...broken.record, ...broken.panel].length ? ` — ${[...broken.record, ...broken.panel].slice(0, 3).join("; ")}` : ""));
note(broken.quote.length === 0,
     `every live quotation on the chain opens its provenance panel` +
     (broken.quote.length ? ` — ${broken.quote.slice(0, 3).join("; ")}` : ""));
note(broken.chars.length === 0,
     `every one of those quotations holds its characters in the file the page names ` +
     `(${reached.size} quotation(s) over ${paths} path(s))` +
     (broken.chars.length ? ` — ${broken.chars.slice(0, 3).join("; ")}` : ""));

// Every record the cohorts CLAIM completes the chain must have been seen to
// complete it. The two sides are computed independently — `fullChain` from set
// membership in the two graphs, `traversed` from the walk above actually
// arriving at characters on disk — so this can fail, which is the only reason
// it is worth printing. (The first version of this line asserted that the four
// cohorts sum to 24. They are constructed as a partition of the same array, so
// that could never fail: a check that asserts nothing, in the file written to
// stop trusting checks that assert nothing.)
const unwalked = fullChain.filter(d => !traversed.has(d));
note(unwalked.length === 0,
     `every record counted as a complete chain was walked end to end ` +
     `(${traversed.size}/${fullChain.length})` +
     (unwalked.length ? ` — never reached: ${unwalked.join(", ")}` : ""));

// A chain check with nothing to traverse asserts nothing while printing green.
note(fullChain.length > 0 && paths > 0,
     `the traversal is not empty (${fullChain.length} record(s), ${paths} complete marker-to-disk path(s))`);

console.log(`
  marker -> record -> quotation -> characters on disk
  complete for ${fullChain.length} of ${allDocs.length} records, over ${paths} path(s)
  landing on ${reached.size} distinct quotation(s):
    ${fullChain.join(", ")}

  drawn, never quoted (${drawnNotQuoted.length}) — reachable from the map, chain ends at the record:
    ${drawnNotQuoted.join(", ")}

  quoted, never drawn (${quotedNotDrawn.length}) — reachable from an answer, no marker to start from:
    ${quotedNotDrawn.join(", ")}

  neither (${neither.length}) — not on the map and not quoted in any archived answer:
    ${neither.join(", ")}

  These are not dead links. Places with no point (Cyeneum, Sabbatha, and the
  gap placements) are reachable from a record panel and never from the map, so
  the chain does not start there; records nothing has quoted end at the record.
  The count is printed rather than folded into a pass so that a shrinking
  number is visible.`);

if (excluded.length) {
  const by = {};
  for (const e of excluded) (by[e.state] ||= []).push(`${e.doc_id}/${e.source_field}`);
  console.log(`
  Excluded by name, not silently (${excluded.length}) — the archive's only
  known-broken citations, both predating A5 and both explained on the About tab:`);
  for (const [st, list] of Object.entries(by))
    console.log(`    ${st}: ${[...new Set(list)].join(", ")}`);
}

console.log();
if (fail.length) {
  console.log(`${fail.length} check(s) failed:`);
  for (const f of fail) console.log("  - " + f);
  process.exit(1);
}
console.log("chain intact — no dead link");
