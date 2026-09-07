/* ------------------------------------------------------------------ *
 * ui/build_banner.mjs — the masthead script band's images.
 *
 * WHY IMAGES AND NOT WEB TYPE. The band shows source text in five writing
 * systems. Set as live text it depends on the visitor having a font for each,
 * and a visitor without one gets tofu boxes — which on a page whose claim is
 * that you can see the characters would be worse than showing nothing.
 *
 * WHY A MASK AND NOT A PICTURE. Each PNG is black glyphs on transparency and
 * is used in CSS as a `mask-image`, with the colour supplied by
 * `background: var(--ink)`. One file therefore serves the light theme and the
 * dark theme and any future palette, and no ink colour is baked into an asset.
 *
 * WHAT IS DECLARED AND WHAT IS DERIVED. The list below is a CURATION decision —
 * which nine of the corpus's records stand at the top of the page, and in what
 * order — so it is declared here rather than inferred from the data, in the
 * spirit of W3_DECLARE_DONT_INFER.md. Everything else is read from the record:
 * the characters, the label, the record's title, the alt text.
 *
 * `from` is a substring of the record's own `original_text_excerpt` marking
 * where the specimen starts. Several excerpts open with the edition's
 * apparatus — a line number, a section letter, a note about the script — which
 * is part of the field and not part of the text. Starting past it is a SLICE
 * FROM WITHIN the field, never an edit to it. If a record is re-curated and
 * the substring goes away, check_ui.mjs fails rather than this quietly
 * rendering the wrong characters.
 *
 * The same list is declared in index.html, and check_ui.mjs asserts the two
 * agree. Two declarations with a check that they match is the data.manifest.json
 * pattern (FINDING 74): a description is only safe when something re-derives it.
 *
 * Run:  node ui/build_banner.mjs
 * ------------------------------------------------------------------ */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

/* Resolved through createRequire so a global `npm i -g playwright` works as
   well as a local one; a bare ESM import only finds a local node_modules. */
const require_ = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require_("playwright")); }
catch {
  console.error("This generator needs Playwright and the Noto fonts for Tamil,\n" +
    "Devanagari, CJK and Greek. It is NOT part of the page's runtime: ui/banner/\n" +
    "is committed, and this script exists to regenerate it when the corpus moves.");
  process.exit(2);
}

const UI = dirname(fileURLToPath(import.meta.url));
const OUT = join(UI, "banner");

/* Order is deliberate: the two scripts that say at a glance that this is not a
   European archive come first, then the other non-Latin ones, then Greek, then
   the records the corpus holds only in romanised transliteration. At 390px
   roughly one specimen is visible at a time, so first is not a small decision. */
const SPECIMENS = [
  { code: "oty",     doc: "southasia-01-akananuru-149",     chars: 24, from: "சிறுபுன்" },
  { code: "lzh",     doc: "eastasia-02-hou-hanshu",         chars: 15, from: "至桓帝延熹九年" },
  { code: "san",     doc: "southasia-05-brihatsamhita",     chars: 30, from: "म्लेच्छा" },
  { code: "ko",      doc: "eastasia-03-hwangnam-glass",     chars: 18, from: "경주 98호" },
  { code: "grc",     doc: "africa-04-silko-talmis",         chars: 30, from: "ἐγὼ Σιλκώ" },
  { code: "xsa",     doc: "arabia-07-cih541",               chars: 30, from: "mlkn w-bn-hw" },
  { code: "gez",     doc: "africa-06-ezana-rie189",         chars: 30, from: "Wa-takalkū" },
  { code: "omy",     doc: "seasia-06-kedukan-bukit",        chars: 32, from: "svasti śrī" },
  { code: "gmq-pro", doc: "scandinavia-05-thorsberg-chape", chars: 26, from: "owlþuþewaz" },
];

/* One family per script. Everything else falls back to the page's own serif. */
const FACE = {
  oty: '"Noto Sans Tamil", serif',
  lzh: '"Noto Serif CJK SC", "Noto Sans CJK SC", serif',
  san: '"Noto Sans Devanagari", serif',
  ko:  '"Noto Sans CJK KR", "Noto Sans CJK HK", sans-serif',
  grc: '"Noto Serif", "FreeSerif", Georgia, serif',
};
const ROMAN_FACE = '"Liberation Mono", "DejaVu Sans Mono", monospace';

const SCALE = 3;                 // physical pixels per CSS pixel
const NATIVE_PX = 26, ROMAN_PX = 17, BOX_H = 44;

/* Trim back to a word boundary ONLY when the slice actually cut a word in half.
   Trimming unconditionally drops the final token even when the specimen ended
   cleanly, which is how `owlþuþewaz / niwajemariz` first rendered as
   `owlþuþewaz /` — a specimen missing the second half of a two-word inscription. */
function specimenText(rec, s) {
  const full = (rec.fields && rec.fields.original_text_excerpt) || "";
  const at = full.indexOf(s.from);
  if (at < 0) throw new Error(`${s.doc}: the declared start "${s.from}" is not in original_text_excerpt`);
  const flat = full.slice(at).replace(/\s+/g, " ");
  const t = flat.slice(0, s.chars);
  const cutMidWord = flat.length > s.chars && !/\s/.test(flat[s.chars]) && !/\s$/.test(t);
  return (cutMidWord ? t.replace(/\S*$/, "") : t).trim() || t;
}

const browser = await chromium.launch();
const page = await (await browser.newContext({ deviceScaleFactor: SCALE })).newPage();
await page.goto("file://" + join(UI, "index.html"), { waitUntil: "load" });
await page.waitForTimeout(1200);
const corpus = await page.evaluate(() => window.MU_DATA.corpus);

mkdirSync(OUT, { recursive: true });
const manifest = { generated: new Date().toISOString(), scale: SCALE, specimens: [] };

for (const s of SPECIMENS) {
  const rec = corpus[s.doc];
  if (!rec) throw new Error(`${s.doc}: no such record in the corpus`);
  const native = !!FACE[s.code];
  const text = specimenText(rec, s);

  const shot = await browser.newContext({ deviceScaleFactor: SCALE });
  const p2 = await shot.newPage();
  await p2.setContent(`<!doctype html><meta charset="utf-8"><style>
    html,body{margin:0;background:transparent}
    #g{display:inline-block;color:#000;white-space:nowrap;line-height:${BOX_H}px;height:${BOX_H}px;
       padding:0 2px;font-family:${native ? FACE[s.code] : ROMAN_FACE};
       font-size:${native ? NATIVE_PX : ROMAN_PX}px;${native ? "" : "letter-spacing:.01em;"}}
  </style><span id="g"></span>
  <script>document.getElementById("g").textContent=${JSON.stringify(text)}</script>`);
  await p2.waitForTimeout(350);
  const el = await p2.$("#g");
  const box = await el.boundingBox();
  await el.screenshot({ path: join(OUT, `${s.code}.png`), omitBackground: true });
  await shot.close();

  manifest.specimens.push({
    code: s.code, doc: s.doc, from: s.from, chars: s.chars,
    text, native, image: `banner/${s.code}.png`,
    w: Math.round(box.width), h: Math.round(box.height),
  });
  console.log(`${s.code.padEnd(9)} ${String(Math.round(box.width)).padStart(4)}x${Math.round(box.height)}  ${text}`);
}

writeFileSync(join(OUT, "manifest.json"), JSON.stringify(manifest, null, 1) + "\n");
console.log(`\n${manifest.specimens.length} specimen(s) -> ui/banner/`);
await browser.close();
