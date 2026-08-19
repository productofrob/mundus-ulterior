# C2 — review of the 205 renderings, before they are committed

_2026-08-16, ruling 19's review step. Every figure below was computed from
`eval/gold/query_renderings.json` as written by the run, not read off the
console, which truncates at 56 characters and hid most of what follows._

```
164 assertions      eval.test_ranking_check
64/64 mutations     scripts/mutate_ranking.py, sources restored
205 renderings      196 admitted, 9 held, 0 call failures
```

## 1. The guard worked, and it found a failure in exactly one language

**Eight of the nine refusals are `oty`, and every one is the same mistake: the
model produced Devanagari or Malayalam instead of Tamil.** One is Malayalam at
1% Tamil (`ഫുനെനിൽ കണ്ടെത്തിയ…`); the rest are Tamil-Devanagari hybrids at
16–42%. This is the Part 4 chrF-0.004 failure class, caught before it entered a
run rather than after twenty-six minutes of it.

The ninth is `xpr` for the frankincense query, where the model returned the
English query verbatim. The echo check caught it.

**The two languages carrying most of the gold set rendered cleanly:**

```
grc      28 admitted    28 wholly Greek
lzh      29 admitted    28 wholly Han   (one carries a Latin "Kane")
```

Twelve of the 33 pairs expect `grc`. If C2 works anywhere, it works there, and
nothing in this file argues against measuring it.

## 2. The refusals land on the pairs C2 exists for

```
pair                          expect   pool          loses
muziris-cargo-periplus        grc      -             oty
muziris-cargo-papyrus         grc      -             oty
muziris-cargo-akananuru       oty      -             oty     <- rank 309
probe-tamil-akananuru-en      oty      non_english   oty     <- the designed probe
probe-pepper-cargo            grc      non_english   oty
probe-roman-provinces         xpr      non_english   oty
probe-frankincense-kane       grc      non_english   xpr
probe-greek-muziris           grc      -             oty
probe-muziris-ports-grc       grc      -             oty
au-hoby-silver                en       -             oty
au-gudme-hoard                en       -             oty
```

Two of these matter more than the rest.

**`probe-tamil-akananuru-en` was added by Block C's fifth item** — an
English→Tamil probe with `lang_pool: non_english`, written because ruling 1 had
stopped counting the corpus's worst cross-lingual result and *"the four existing
cross-lingual probes cover Greek, Chinese and Parthian only"*. It is the only
designed English→Tamil evidence in the set. **Its Tamil rendering was refused, so
C2 cannot help the one probe built to test what C2 is for.**

**The whole `muziris-cargo` unit loses `oty`**, including
`muziris-cargo-akananuru` at rank 309 — the corpus's one genuinely broken
cross-lingual link, and the case named in ruling 1 as the standing finding.

So: the rule is gold-blind and stayed gold-blind, but its **execution is weakest
exactly where the gold set's worst failure lives.** That sentence belongs beside
every C2 number, next to ruling 17(d)'s.

## 3. Three holes the run exposes in the guard

### Hole 1 — `latin` is a null check, and it covers four of the seven targets

`xpr`, `xna`, `xsa` and `gmq-pro` are all stored romanised, so `required_script`
returns `latin` for all four and any Latin string passes. The guard verifies a
writing system; it was never able to verify a language, and this run shows what
that costs:

- **Every `gmq-pro` rendering is Old Norse or modern Icelandic, not Proto-Norse
  in runic transliteration.** *"Hvernig lýstu Kínversk heimildir Rómaveldinu?"*,
  *"Hvat fylgdi brakteatiskum fé funnu á Fúnum?"* — `hvernig`, `ý`, `ð`, `á` are
  not Proto-Norse. 30 of 30 admitted.
- **`xpr` for the Old Tamil query is romanised Tamil**, not Parthian:
  *"yawanā Mousirē sōnē āgamya kāriyē parinayanti"*.
- **`gmq-pro` for the same query is the Tamil query transliterated and nothing
  else**: *"Yavana Muciṛi poṉṉoṭu vantu kaṛiyoṭu peyarum"*.
- **`xsa` likewise**: *"Yawnr mwsyry pnnwdu wnd qrydu pyrwm"*.

I looked for this mechanically and **it is not mechanically detectable**, which
is worth recording as a negative result rather than left as an untried idea. If
the model were emitting one romanisation for four languages, the four Latin
renderings of a query would resemble each other; character-3-gram Jaccard
between them has **median 0.12 and maximum 0.34** across all 30 queries, with
nothing above 0.55. The model is producing four genuinely different strings. It
is simply producing the wrong language in some of them, and only reading found
it.

### Hole 2 — `SCRIPT_FLOOR = 0.6` admits mixed-script renderings

Eight admitted `oty` renderings still contain another writing system. The worst
is 66% Tamil and contains Hangul, Han, Malayalam and Latin in one string:

```
கேரளக் கரையில்발掘된 지중해 amphora sherds
```

That was admitted. So was an `lzh` rendering at 69% Han (`乳香國及阿拉伯之Kane港`)
and two `oty` renderings at 74% and 78% with Devanagari mixed in. A rendering a
third of which is in another script is not a rendering, and the floor was set at
0.6 on the argument that a wholly-wrong rendering sits at 0.0 — true, but it left
a band nobody was thinking about.

What a tighter floor costs, computed over the 78 admitted native-script
renderings:

```
floor 0.60   0 further refusals   (as run)
floor 0.90   5
floor 0.95   7
floor 1.00   9
```

### Hole 3 — the echo check is exact-match only

It caught the one verbatim English return. It cannot catch the three
transliteration-echoes in hole 1, because a romanisation of the source is not
string-equal to the source.

## 4. One more, and it is a measurement risk rather than a guard hole

`lzh` for the Parthian query is **沙漢沙赫伊蘭烏德安伊蘭沙布爾** — a phonetic
transcription of the *sounds* of "šāhān šāh Ērān ud Anēran Šābuhr" into Chinese
characters, not a translation of its meaning. It is 100% Han and passes cleanly.
Embedded, it is noise wearing a valid script.

**Ruling 17(b)'s query-to-query cosine is the instrument for this and it is not
built yet.** It is free — the vectors are computed anyway — and it would have
flagged this row without a single extra call.

## 5. Two things worth saying about `gmq-pro` specifically

`answer/evidence.py` describes the Vimose material as *"a machine 'translation'
of six partly undeciphered runic sequences — the worst case"*. A query rendered
into Proto-Norse is being matched against text that is partly undeciphered. Even
a perfect rendering has little to match. The model substituting Old Norse is
predictable, and a corrected `gmq-pro` rendering may be worth no more than the
wrong one.

That is an argument about the index, not about any pair's expectation, so it is
available to ruling 12 without leakage.

## 6. What has to be ruled before fusion

Ruling 19 makes this review a gate, so the file is **not committed** and no
fusion is written until this is settled. Four ways forward, and each states its
cost.

**20a — proceed on the 196, print the losses.** No further spend. Honest only if
the eleven pairs above are printed with their lost languages beside every C2
number. Accepts that `probe-tamil-akananuru-en` is untested and that four of
seven target languages are unguarded.

**20b — tighten the native-script floor to 1.00 and re-render the refusals.**
9 further refusals, 18 held of 205, about 18 calls to re-render. Removes hole 2.
Holes 1 and 3 stay, and are stated rather than fixed.

**20c — 20b, plus drop the four Latin-script languages from ruling 12's target
set** on the ground that a romanised language cannot be distinguished from a
romanisation of the source, so a rendering into it cannot be verified. The rule
stays gold-blind: it is stated about the index's writing systems, not about any
pair. Renderings fall from 205 to about 88. Cost: five gold pairs expect
`xpr`/`xna`/`xsa`/`gmq-pro` and would get no rendering in their own target
language — which is the same position they are in today, since those four are
the ones the guard cannot vouch for.

**20d — 20b, plus build ruling 17(b) now** and re-review with the
query-to-query cosine in hand before deciding about the Latin four. Costs one
embedding pass, no chat calls, and replaces an argument about hole 1 with a
number. It is the only option that puts evidence under the `gmq-pro` question
instead of judgement.

My recommendation is **20d then a second look**, because hole 1 is currently
settled by my reading of eight strings and that is the weakest evidence in this
file.

---

## 7. RULED 20d, 2026-08-16 — and what it turned out to cost

### The floor

`SCRIPT_FLOOR` 0.6 -> **1.0**. The rule is now sayable in one line: *a rendering
contains no letter outside its own writing system.* `U+02B0-02FF` was added to
the Latin ranges first, because `ʾ` and `ʿ` are Unicode letters in no Latin
block and a whole-language floor would otherwise have refused the corpus's own
transliteration convention — 117 of 118 Latin renderings move to wholly-Latin
with that range in, and the one that does not is a genuine stray Greek gamma.

Re-judged offline against the existing file: **19 of 205 held, up from 9.**
Ten verdicts change — eight `oty`, one `xpr`, one `lzh`:

```
oty  66%  Kerala amphora        35 strays  [ahrs掘mpoedരള발된지중해]
oty  74%  Tyndis/Muziris ports  10 strays  [सരલकयणडరജ]
oty  78%  Adulis ivory           8 strays  [सगतरजधन]
oty  89%  Shapur titles          2 strays  [හह]        Sinhala and Devanagari
oty  91%  Sasanian hunt          2 strays  [സന]        Malayalam
oty  94%  Nabataean epitaph      2 strays  [銘文]        Han
oty  96%  Rome/Aksum trade       1 stray   [ജ]
oty  98%  Hermapollon valuation  1 stray   [র]         Bengali
lzh  69%  frankincense/Kane      4 strays  [Kane]
xpr  98%  Danish bog             1 stray   [γ]
```

The refusal now names the offending characters. That is not decoration: this
whole review was possible only because the characters could be read, and "78%"
sends you back to the file where "8 Devanagari letters" is the diagnosis.

### The retry is a different prompt, and it has to be

`_chat` runs at `temperature=0` so the harness is reproducible. Re-issuing the
same prompt is therefore **not a retry, it is the same call** — it would return
the same wrong-script string while reading like a second attempt. So
`--redo-held` uses a retry prompt under `QUERY_RETRY_PROMPT_VERSION =
c2-render-retry-v1`, and `prompt_version` is now recorded **per rendering**, not
only per file: after a retry pass the file holds two prompts' output and "which
rows came from which" is the first question anybody asks of it.

The file is also **re-judged on load** against the current guard rather than
trusting the verdict stored beside each row. A file that kept its 0.6-era
verdicts would carry ten renderings under an `ok: true` that no longer means
what it says. The text is evidence; the verdict is derived, and it is re-derived
every time.

### Ruling 17(b) is built: `scripts/check_renderings.py`

One batched embedding pass, no chat calls, `cos(source query, rendering)` from
the same vectors a ranking run computes anyway. Per-language median, MAD, min
and max, plus rows more than N MADs below their language's median. Archived
first, printed second. **Reported, never gated** — there is no baseline for this
quantity.

What it will and will not settle, said before the numbers arrive so the answer
cannot be read into them afterwards:

- it **will** catch the Chinese phonetic transcription of the Parthian query,
  a rendering that answered instead of restating, and a rendering that dropped
  half the query;
- it **will** show whether `gmq-pro`'s renderings sit further from their queries
  as a group than `grc`'s do — which is evidence about hole 1;
- it **will not** tell you whether a string is Proto-Norse or Old Norse. A
  competent rendering in either sits close to the query. No embedding distance
  identifies a language, and the report says so on its own last line.

### A trap this session paid for

Verifying the new mutations in-process reported two of them as unwatched. The
cause was **CPython's bytecode cache**: `SCRIPT_FLOOR = 1.0` -> `0.6` and
`if retry:` -> `if False:` are the same number of bytes, and written inside the
same mtime second they are invisible to the interpreter's `.pyc` validity check.
`scripts/mutate_ranking.py` already runs the suite with `-B` as a precaution its
own comment says was suspected and never observed. **It has now been observed.**
The comment can be upgraded from "closes the mechanism that was suspected" to
"closes a mechanism that has been seen to fire."

### What to run

```powershell
python -m eval.test_ranking_check                        # expect 174
python scripts\mutate_ranking.py                         # expect 67
python scripts\build_query_renderings.py --dry-run       # expect: re-judged 10
python scripts\build_query_renderings.py --redo-held     # ~19 retry calls
python scripts\check_renderings.py                       # ruling 17(b)
```

Then the second look, and only then the fusion.
