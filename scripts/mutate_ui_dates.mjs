/*
 * Mutation-verify the two date-verdict guards added to ui/check_ui.mjs.
 *
 *     node scripts/mutate_ui_dates.mjs
 *
 * Scope, deliberately narrow. `date_audit` — which DECIDES `ok` / `outside` /
 * `hole` / `unknown` / `no_dates`, and where the hole-versus-unknown boundary
 * lives — is already mutation-verified by `scripts/mutate_places.py`, three of
 * whose 43 cases target exactly that function. Repeating them here would prove
 * nothing twice.
 *
 * What is new, and therefore what this file covers, is the two hops AFTER the
 * verdict is decided:
 *
 *   1. the builder CARRIES it into `ui/data.js`
 *   2. the renderer SURFACES it on the placement panel
 *
 * Those are the hops that were missing until now: `--check` had been printing
 * `hole` and `unknown` since A6 and neither reached the screen, so the page
 * could not say that a point's dates fail to corroborate the record citing it.
 * A guard against that regression which has never been seen to fail is not
 * known to work.
 *
 * Same temp-tree method as `scripts/mutate_chain.mjs`: copy, mutate the copy,
 * run the copied checker. Nothing in `ui/check_ui.mjs` knows this file exists.
 */

import { cpSync, mkdtempSync, readFileSync, writeFileSync, rmSync, utimesSync,
         readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

function makeTree() {
  const dir = mkdtempSync(join(tmpdir(), "mu-dates-"));
  for (const f of ["check_ui.mjs", "index.html", "data.js"])
    cpSync(join(ROOT, "ui", f), join(dir, "ui", f), { recursive: true });
  cpSync(join(ROOT, "data", "seed_corpus"), join(dir, "data", "seed_corpus"), { recursive: true });
  try { cpSync(join(ROOT, "eval", "answer_runs"), join(dir, "eval", "answer_runs"), { recursive: true }); }
  catch { /* absent is tolerated by the staleness walk */ }

  // check_ui.mjs section 0 hard-fails on a bundle older than the evidence, and
  // copying gives everything one fresh timestamp. Age the evidence, or every
  // case below would stop at section 0 and prove nothing.
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

const editFile = (dir, rel, fn) => {
  const p = join(dir, rel);
  const before = readFileSync(p, "utf8");
  const after = fn(before);
  if (after === before) throw new Error(`mutation changed nothing in ${rel}`);
  writeFileSync(p, after);
};

function editBundle(dir, fn) {
  editFile(dir, "ui/data.js", (js) => {
    const open = js.indexOf("{", js.indexOf("MU_DATA"));
    const close = js.lastIndexOf("}");
    const D = JSON.parse(js.slice(open, close + 1));
    fn(D);
    return js.slice(0, open) + JSON.stringify(D) + js.slice(close + 1);
  });
}

// Every placement in the bundle that carries a live verdict, so a mutation
// lands on something the checks actually look at.
const withVerdict = (D, want) =>
  Object.values(D.places.docs).flat()
        .filter(e => e.resolved && (want ? e.resolved.date_verdict === want : true));

const MUTATIONS = [
  {
    hop: "builder carries the verdict",
    what: "a resolved placement reaches the bundle with no verdict at all",
    expect: "every resolved placement carries a date verdict",
    apply: (dir) => editBundle(dir, (D) => {
      const target = withVerdict(D)[0];
      if (!target) throw new Error("no resolved placement to blank");
      target.resolved.date_verdict = null;
    }),
  },
  {
    hop: "renderer surfaces the verdict",
    what: "the panel drops the machine-readable marker but keeps the prose",
    expect: "date verdict is surfaced on its placement panel",
    apply: (dir) => editFile(dir, "ui/index.html",
      (s) => s.replace(' data-date-verdict="${esc(v)}"', "")),
  },
  {
    hop: "renderer surfaces the verdict",
    what: "the box is suppressed entirely, the way it was before this block",
    expect: "date verdict is surfaced on its placement panel",
    apply: (dir) => editFile(dir, "ui/index.html",
      (s) => s.replace("  if (v !== \"hole\" && v !== \"unknown\") return \"\";",
                       "  return \"\";")),
  },
];

console.log(`Mutation-verifying the date-verdict guards in ui/check_ui.mjs — ${MUTATIONS.length} mutation(s)\n`);

{
  const dir = makeTree();
  try {
    execFileSync("node", [join(dir, "ui", "check_ui.mjs")], { encoding: "utf8" });
    console.log("  ok    the unmutated copy passes (the baseline every case below is measured against)\n");
  } catch (e) {
    console.log("  FAIL  the unmutated copy does not pass — no mutation below would mean anything");
    console.log((e.stdout || "") + (e.stderr || ""));
    process.exit(1);
  } finally { rmSync(dir, { recursive: true, force: true }); }
}

let caught = 0;
const wrong = [];
for (const m of MUTATIONS) {
  const dir = makeTree();
  let out = "", exit = 0;
  try {
    m.apply(dir);
    out = execFileSync("node", [join(dir, "ui", "check_ui.mjs")], { encoding: "utf8" });
  } catch (e) {
    exit = e.status ?? 1;
    out = (e.stdout || "") + (e.stderr || "");
  } finally { rmSync(dir, { recursive: true, force: true }); }

  const failed = out.split("\n").filter(l => l.trimStart().startsWith("FAIL"));
  const rightOne = failed.some(l => l.includes(m.expect));
  const label = `${m.hop} — ${m.what}`;

  if (exit !== 0 && rightOne) {
    console.log(`  ok    ${label}`);
    if (failed.length > 1) console.log(`          (also tripped ${failed.length - 1} other check(s))`);
    caught++;
  } else if (exit === 0) {
    console.log(`  FAIL  ${label}`);
    console.log(`          check_ui PASSED on mutated data — this hop is not guarded`);
    wrong.push(label);
  } else {
    console.log(`  FAIL  ${label}`);
    console.log(`          failed, but not on "${m.expect}" — got: ${failed.join(" | ") || "(no FAIL line)"}`);
    wrong.push(label);
  }
}

console.log(`\n${caught}/${MUTATIONS.length} mutations caught by the assertion that owns the hop`);
if (wrong.length) { for (const w of wrong) console.log(`  - ${w}`); process.exit(1); }
