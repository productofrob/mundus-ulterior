/*
 * Mutation-verify ui/check_chain.mjs — G1 criterion 4.
 *
 *     node scripts/mutate_chain.mjs
 *
 * Same standard as scripts/mutate_places.py and scripts/mutate_ui_places.py:
 * each mutation breaks EXACTLY ONE hop of the chain and asserts that the check
 * protecting THAT hop reports FAIL — not merely that something failed. A run
 * where every mutation is caught by the same assertion would prove only that
 * the file is fragile, not that it is discriminating.
 *
 * Why this file exists at all: PROGRESS.md records six occasions on which an
 * over-broad check passed on data it did not actually validate, most
 * expensively the map that plotted 49 points onto an inverted planet with 20/20
 * green. `check_chain.mjs` is the file written in response, and a guard never
 * seen to fail is not known to work.
 *
 * How it runs: each case copies the tree into a temp directory, applies one
 * mutation to the COPY, and runs the copied `check_chain.mjs` there. The
 * checker derives its own root from its file location, so no test hook is
 * needed in the production file — nothing in `ui/check_chain.mjs` knows this
 * script exists.
 *
 * Two of the eight mutations touch the seed files on disk rather than
 * `ui/data.js`. Those are the load-bearing ones: if the last hop secretly read
 * the bundle instead of the disk, `ui/data.js` would still agree with itself
 * and the check would stay green while the characters it claims to have found
 * were gone.
 *
 * This file has already paid for itself once. Its third case originally moved a
 * run to an unlisted question, and check_chain.mjs passed on it — the assertion
 * that hop was supposed to have was a tautology, and nothing but a mutation
 * would have shown that. See the comment on that case below.
 */

import { cpSync, mkdtempSync, readFileSync, writeFileSync, rmSync, utimesSync,
         readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

/* ---- the tree each case runs against ---- */
function makeTree() {
  const dir = mkdtempSync(join(tmpdir(), "mu-chain-"));
  cpSync(join(ROOT, "ui", "check_chain.mjs"), join(dir, "ui", "check_chain.mjs"), { recursive: true });
  cpSync(join(ROOT, "ui", "index.html"),      join(dir, "ui", "index.html"));
  cpSync(join(ROOT, "ui", "data.js"),         join(dir, "ui", "data.js"));
  cpSync(join(ROOT, "data", "seed_corpus"),   join(dir, "data", "seed_corpus"), { recursive: true });
  try { cpSync(join(ROOT, "eval", "answer_runs"), join(dir, "eval", "answer_runs"), { recursive: true }); }
  catch { /* absent is fine; the staleness walk tolerates it */ }

  // The staleness guard compares mtimes, and copying gives everything the same
  // fresh timestamp. Age the evidence so the guard passes on an unmutated tree
  // — otherwise every case below would fail at section 0 and prove nothing.
  const old = new Date(Date.now() - 3600_000);
  const walk = (d) => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      const p = join(d, e.name);
      if (e.isDirectory()) walk(p); else utimesSync(p, old, old);
    }
  };
  for (const sub of ["data", "eval"]) { try { walk(join(dir, sub)); } catch {} }
  return dir;
}

const readData  = (dir) => readFileSync(join(dir, "ui", "data.js"), "utf8");
const writeData = (dir, js) => writeFileSync(join(dir, "ui", "data.js"), js);

// data.js is `window.MU_DATA = {...};` on one line — parse, mutate, re-emit.
function editBundle(dir, fn) {
  const js = readData(dir);
  const open = js.indexOf("{", js.indexOf("MU_DATA"));
  const close = js.lastIndexOf("}");
  const D = JSON.parse(js.slice(open, close + 1));
  fn(D);
  writeData(dir, js.slice(0, open) + JSON.stringify(D) + js.slice(close + 1));
}

function seedFileFor(dir, docId) {
  const base = join(dir, "data", "seed_corpus");
  for (const sub of readdirSync(base, { withFileTypes: true })) {
    if (!sub.isDirectory()) continue;
    for (const f of readdirSync(join(base, sub.name))) {
      if (!f.endsWith(".json")) continue;
      const p = join(base, sub.name, f);
      if (JSON.parse(readFileSync(p, "utf8")).id === docId) return p;
    }
  }
  throw new Error(`no seed file for ${docId}`);
}

// A doc that is on the full chain, so mutations to it are actually traversed.
const CHAIN_DOC = "southasia-02-periplus-muziris";

/* ---- helpers for picking a target the traversal will actually reach ---- */
function bundle(dir) {
  const js = readData(dir);
  return JSON.parse(js.slice(js.indexOf("{", js.indexOf("MU_DATA")), js.lastIndexOf("}") + 1));
}
const groupWith = (D, docId) => D.places.groups.find(g => g.members.some(m => m.doc_id === docId));
function firstLiveSpan(D, docId) {
  for (const r of D.runs) {
    const spans = r.grounding?.quote_spans || [];
    for (let i = 0; i < spans.length; i++)
      if (spans[i].doc_id === docId &&
          ["resolved", "case_only"].includes(spans[i].resolution?.state))
        return { run: r, i, span: spans[i] };
  }
  throw new Error(`no live span for ${docId}`);
}

/* ---- the mutations ----
 *
 * `expect` is a substring of the assertion that MUST report FAIL. Matching on
 * the assertion text rather than on the exit code is the whole point: an exit
 * code says something broke, and this file is here to prove the right thing
 * breaks.
 */
const MUTATIONS = [
  {
    hop: "marker -> member -> record",
    what: "a drawn marker's member points at a doc_id with no seed record",
    expect: "every drawn marker's member resolves to a seed record",
    apply: (dir) => editBundle(dir, (D) => {
      groupWith(D, CHAIN_DOC).members.find(m => m.doc_id === CHAIN_DOC).doc_id = "no-such-record";
    }),
  },
  {
    hop: "member -> placement list",
    what: "a member's key is not among the placements its own record carries",
    expect: "every member is on its own record's placement list",
    apply: (dir) => editBundle(dir, (D) => {
      groupWith(D, CHAIN_DOC).members.find(m => m.doc_id === CHAIN_DOC).key =
        `${CHAIN_DOC}::findspot_places[99]`;
    }),
  },
  {
    // The one that found a real defect. The first version of this case moved a
    // run to an unlisted question and expected the check to notice it was
    // unreachable. It did not, and could not: `byQuestion` and `QUESTIONS` are
    // both derived from `D.runs`, so every run is reachable by construction and
    // the assertion could never have failed. It was a tautology inside the file
    // written to stop trusting tautologies. This case replaced it.
    hop: "quotation -> the file the page names",
    what: "the record points the user at a different seed file than the one " +
          "holding its characters",
    expect: "holds its characters in the file the page names",
    apply: (dir) => editBundle(dir, (D) => {
      D.corpus[CHAIN_DOC].file = D.corpus["arabia-01-periplus"].file;
    }),
  },
  {
    hop: "quotation -> the file the page names",
    what: "the record points at a path that is not on disk at all",
    expect: "holds its characters in the file the page names",
    apply: (dir) => editBundle(dir, (D) => {
      D.corpus[CHAIN_DOC].file = "data/seed_corpus/south_asia/no-such-file.json";
    }),
  },
  {
    hop: "quotation -> characters",
    what: "a chain span's offsets are shifted off its quote",
    expect: "holds its characters in the file the page names",
    apply: (dir) => editBundle(dir, (D) => {
      const { span } = firstLiveSpan(D, CHAIN_DOC);
      span.abs_start += 40; span.abs_end += 40;
    }),
  },
  {
    hop: "quotation -> characters (ON DISK)",
    what: "the seed file's text is edited so the bundle still agrees with itself",
    expect: "holds its characters in the file the page names",
    onDisk: true,
    apply: (dir) => {
      const D = bundle(dir);
      const { span } = firstLiveSpan(D, CHAIN_DOC);
      const p = seedFileFor(dir, CHAIN_DOC);
      const j = JSON.parse(readFileSync(p, "utf8"));
      const t = j[span.source_field];
      j[span.source_field] =
        t.slice(0, span.abs_start) +
        "X".repeat(span.abs_end - span.abs_start) +
        t.slice(span.abs_end);
      writeFileSync(p, JSON.stringify(j, null, 2));
      const old = new Date(Date.now() - 3600_000);
      utimesSync(p, old, old);
    },
  },
  {
    hop: "quotation -> characters (case, ON DISK)",
    what: "a `resolved` span's characters differ only in case on disk — the " +
          "leniency granted to `case_only` must not extend to it",
    expect: "holds its characters in the file the page names",
    onDisk: true,
    apply: (dir) => {
      const D = bundle(dir);
      let target = null;
      for (const r of D.runs)
        for (const s of r.grounding?.quote_spans || [])
          if (s.doc_id === CHAIN_DOC && s.resolution?.state === "resolved" &&
              /[a-z]/.test(s.quote || "")) { target = s; break; }
      if (!target) throw new Error("no resolved lower-case span on the chain doc");
      const p = seedFileFor(dir, CHAIN_DOC);
      const j = JSON.parse(readFileSync(p, "utf8"));
      const t = j[target.source_field];
      j[target.source_field] =
        t.slice(0, target.abs_start) +
        t.slice(target.abs_start, target.abs_end).toUpperCase() +
        t.slice(target.abs_end);
      writeFileSync(p, JSON.stringify(j, null, 2));
      const old = new Date(Date.now() - 3600_000);
      utimesSync(p, old, old);
    },
  },
  {
    hop: "the traversal itself",
    what: "no marker is drawn at all, so the walk has nothing to check",
    expect: "the traversal is not empty",
    apply: (dir) => editBundle(dir, (D) => { D.places.groups = []; }),
  },
];

/* ---- run ---- */
console.log(`Mutation-verifying ui/check_chain.mjs — ${MUTATIONS.length} mutation(s)\n`);

let caught = 0;
const wrong = [];

// The unmutated copy must pass, or every FAIL below is ambiguous.
{
  const dir = makeTree();
  try {
    execFileSync("node", [join(dir, "ui", "check_chain.mjs")], { encoding: "utf8" });
    console.log("  ok    the unmutated copy passes (the baseline every case below is measured against)\n");
  } catch (e) {
    console.log("  FAIL  the unmutated copy does not pass — no mutation below would mean anything");
    console.log((e.stdout || "") + (e.stderr || ""));
    process.exit(1);
  } finally { rmSync(dir, { recursive: true, force: true }); }
}

for (const m of MUTATIONS) {
  const dir = makeTree();
  let out = "", exit = 0;
  try {
    m.apply(dir);
    out = execFileSync("node", [join(dir, "ui", "check_chain.mjs")], { encoding: "utf8" });
  } catch (e) {
    exit = e.status ?? 1;
    out = (e.stdout || "") + (e.stderr || "");
  } finally { rmSync(dir, { recursive: true, force: true }); }

  const failedLines = out.split("\n").filter(l => l.trimStart().startsWith("FAIL"));
  const rightOne = failedLines.some(l => l.includes(m.expect));
  const label = `${m.hop}${m.onDisk ? "  [disk]" : ""} — ${m.what}`;

  if (exit !== 0 && rightOne && failedLines.length === 1) {
    console.log(`  ok    ${label}`);
    caught++;
  } else if (exit !== 0 && rightOne) {
    // Caught by the right assertion, but others fell over with it. Not a
    // failure of discrimination, but worth printing: a mutation that trips
    // four checks tells you less than one that trips its own.
    console.log(`  ok    ${label}`);
    console.log(`          (also tripped ${failedLines.length - 1} other check(s))`);
    caught++;
  } else if (exit === 0) {
    console.log(`  FAIL  ${label}`);
    console.log(`          the check PASSED on mutated data — this hop is not guarded`);
    wrong.push(label);
  } else {
    console.log(`  FAIL  ${label}`);
    console.log(`          failed, but not on "${m.expect}" — got: ${failedLines.join(" | ") || "(no FAIL line)"}`);
    wrong.push(label);
  }
}

console.log(`\n${caught}/${MUTATIONS.length} mutations caught by the assertion that owns the hop`);
if (wrong.length) {
  for (const w of wrong) console.log(`  - ${w}`);
  process.exit(1);
}
