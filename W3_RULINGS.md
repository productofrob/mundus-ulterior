# W3 rulings — 80 to 82, and FINDINGS 95 and 96 — declared 2026-09-07

*Numbers read from `RULINGS.md` and the ruling files it indexes at the time of
writing. The highest ruling declared before today is 79 (`F7_CURATION_START.md`);
the highest finding is 93 (`BLOCK_G_RESULT.md`). FINDING 94 is in `W3_START.md`,
committed at `59dcd1e` before any code existed.*

**Rulings 80 and 81 were decided at the open of the session and are written here
in the words they were decided in.** The prediction document names them by
number and states their content; this file is their text.

---

## Ruling 80 — every text-bearing field DECLARES its own language, the loader REFUSES to infer one, and the classifiers are demoted from determination to cross-check

**FINDINGS 82 and 86 are one defect and are closed as one item.** A language was
being INFERRED where it should have been DECLARED.

### The declaration

Two keys, flat, beside the fields they describe:

```
original_text_excerpt   ->  original_text_lang
reference_translation   ->  reference_translation_lang
```

`language_code` is untouched and keeps its meaning and its type. **The two are
about different things and conflating them is the defect one level up:**
`language_code` is a fact about the RECORD, the languages the source is in;
`original_text_lang` is a fact about the FIELD, the language of the characters
actually stored in it. `classify_original` read the first as though it were the
second.

### The key is required on every record and `null` is a positive declaration

A record that omits either key does not load. `null` declares that the field
holds no text, and the loader raises **both ways** — a `null` over a field with
text, and a language over a field with none. The cheaper rule, requiring a
declaration only where there is text, makes an absent key mean *nobody declared*
and *there is nothing to declare* at once, which is the ambiguity this whole item
exists to remove.

**The eight loader-warning records are what this clause had to be ruled on
before it could be written.** They now declare `null` and load unchanged, and
their warnings still read exactly as they did.

### The classifiers stay, as a cross-check that can refuse

`non_latin_ratio` and the script test are not deleted. **Two fields that must
agree are a guard; one field computed from the other is a guard deleted.** Six
refusal clauses, each mutated separately in `scripts/mutate_fidelity.py`:

```
1  the key is absent
2  null declared over a field that holds text
3  a language declared over a field that holds nothing
4  a code that is not in LANG_SCRIPTS
5  `mul` over a field that is not written in two scripts
6  a script the declared language is not written in
```

**`non_latin_ratio` no longer asks a closed allowlist of script names.** It
asserts the rule — a character is non-Latin when its Unicode name does not begin
with `LATIN` — with one named exception, `MODIFIER LETTER`, because `ʾ` and `ʿ`
are the aleph and ayin of scholarly romanisation, they carry no script of their
own, and 90 of them sit inside this corpus's Latin-script transliterations. The
22-entry tuple is deleted rather than extended: `F7_RESULT.md` said adding
`"THAI"` was the wrong shape of fix and it was right, because the next language
breaks it again and French breaks it today regardless of any script name.

### The objection, answered, because it is the one that matters

*"You have replaced an allowlist of scripts with an allowlist of language
codes — same defect."* **No.** The script allowlist was a PROXY FOR A GENERAL
PROPERTY, and a proxy that omits Thai answers the general question wrongly.
`LANG_SCRIPTS` is A FACT ABOUT THE CORPUS: it is the same set the state block's
per-language chunk line already prints, and it grows deliberately, by a curator
adding a code for a record they are placing. FINDING 10's lesson applies to the
first and not the second — assert the rule, enumerate at check time.

### `mul`, and why it is not a loophole

One field in this corpus holds two languages. `mul` is ISO 639-3 for exactly
that and is the only true single-code statement about it. **It is guarded so it
cannot become the lenient default the rest of this ruling refuses:** a field
declaring `mul` must actually contain two scripts at 10% or more each, or it is
refused. One record declares it and nothing else may without earning it.

### What the rejected alternative was

**A sidecar of declarations beside the manifest, leaving records untouched and
the digest unmoved.** Refused: that is the shape of the paraphrase flag, and
FINDING 11 is what happened to it — the flag marked SUSPICION and nothing in the
pipeline ever turned suspicion into a determination. The fact belongs on the
record. The cost is ruling 82.

---

## Ruling 81 — the backfill is ROUTE A OVER ALL FIFTY-FOUR RECORDS, and there is no route B

`W3_DECLARE_DONT_INFER.md` §3 offered two routes and recommended a split. **The
split turned out to be unnecessary and the reason is worth recording, because it
is the opposite of the usual one: route A was CHEAPER than expected, not the
remainder more trustworthy.**

Reading every record's `original_text_excerpt` and `reference_translation` — head,
middle and tail — plus the `language_note` of every record where those did not
settle it, was **one pass over the corpus**, not the forty-record grind §3
budgeted for.

**So no declaration in this corpus was written from the classifier's output.**
The tautology §3 names — run the classifier, write its answer as the
declaration, then assert declaration == classifier — is not merely marked, it is
absent. The guard has force over all 54 records from its first run, and the
no-force clause §3 required for route B is not written because there is nothing
to write it about.

**Three records were settled by their own `language_note` and not by judgement**,
and that is what route A means in practice:

- `eastasia-03-hwangnam-glass` — the note says the field is the English summary
  with the Korean title quoted. `en`.
- `scandinavia-01-hoby-treasure` — the note says the catalogue text is English and
  the cups carry the Greek signature. `en`.
- `arabia-05-ruwafa` — the note describes the five interleaved lettered sections
  exactly. `mul`, and see FINDING 95.

**`persia-01-skz` is DECLARED `xpr` AND THE DOUBT IS RECORDED RATHER THAN
RESOLVED.** Its §1 transcription carries both Middle Persian and Parthian
markers — `Ērān` against `až` — the record declares `xpr` first, and nothing in
it says which of the monument's three walls the excerpt was taken from.
Overturning a curator's language identification from a hundred-character sample
is precisely the inference this item exists to forbid. **Owed investigation, and
it is a real one:** if the excerpt is Middle Persian, the corpus has been
counting a Parthian record it does not hold.

---

## Ruling 82 — `floor.json`'s corpus pin KEEPS naming `26e4a683…`, and gains a dated record that the corpus it names no longer exists

Every record gained two keys, so every record's `content_hash` moved and the
corpus digest with it:

```
26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28   24 records, superseded
0e7845055e440c7c46535f1aa2e5ea55e5116ed733d77bbb616404e8bdc2c839   54 records, on disk
```

**The pin is not re-pointed, and that is the ruling rather than an omission.**
`26e4a683…` IS the corpus this floor was calibrated on. Writing the new digest
into that field would assert that a calibration taken on one corpus holds on
another, which is the exact thing ruling 49's corpus clause exists to prevent.

`calibration_scope.corpus.superseded_by` records the move, dated, naming the new
digest, and states the sentence that was true and unwritten everywhere until
today: **the floor is UNCALIBRATED FOR THE CORPUS ON DISK.** It stays in force
as a within-session regression gate at any corpus — `what_this_does_NOT_do`
already said so — and no run against `0e784505…` can calibrate it.

**The booking is unchanged.** `recalibration_corpus` still names the corpus in
force at Block F's close, `BLOCK_G_RESULT.md` §6 item 3 read that as 54 records,
and the price is three sessions on three distinct UTC dates and ~270 chat calls.
**W3 ran on the bridge and does not write `recalibration_corpus.record_count` or
`seed_corpus_digest`:** those are written by the session that takes the sweep, on
the host, from the corpus it actually ran against. A digest transcribed by a
session that could not compute it is a digest nobody verified.

---

# FINDING 95 — the declaration is per FIELD, the language is carried per CHUNK, and one field's chunks are not all in one language

**`arabia-05-ruwafa` reported three Aramaic chunks and the corpus held none.**

The record is a bilingual: sections A, C and E of the monument are Greek, B and D
are Nabataean Aramaic in Latin transliteration, and they interleave in one field.
`chunk_field` splits that field into three chunks — and the three are
individually monolingual:

```
ruwafa::original::000   verbatim_original   Greek         was `arc`   WRONG
ruwafa::original::001   transliteration     Nabataean     was `arc`   right
ruwafa::original::002   partial_verbatim    Greek         was `arc`   WRONG
```

Every one took its language from `language_code[0]`. **Two of the three were
wrong, and the state block's per-language line has read `'arc': 3` throughout
Block F while the retrieval index contained no Aramaic chunk at all.** The line
now reads `'mul': 3` and `arc` is absent from it, which is the honest reading.

**The remaining imprecision is named rather than fixed.** `mul` is true of the
FIELD and less than the chunker knows about each CHUNK: chunk 001 goes from a
correct `arc` to a vaguer `mul`. The shape that would fix it is a per-span
declaration, and inventing one here would be a mechanism designed for one record
by a session that has just seen it. **Deferred, and the next block cannot say it
was not told.**

---

# FINDING 96 — a Greek signature in this corpus is transcribed with a Cyrillic character

`scandinavia-01-hoby-treasure.original_text_excerpt[43]` is **U+0404 CYRILLIC
CAPITAL LETTER UKRAINIAN IE**, standing in for a lunate epsilon inside
`[ΧEIPI]ΣΟΦΟΣ ЄΠΟΙΕΙ`, the signature of Cheirisophos on the Hoby cups.

**It was invisible to every instrument in this repository until today**, because
the deleted script allowlist had no `CYRILLIC` entry and `non_latin_ratio`
silently skipped anything it did not recognise. The general rule counts it, and
`script_mix` names it. One character in eighty, so no ratio crosses a threshold
and no classification moves.

**This record is NOT corrected here.** Changing a character in a text field moves
a `content_hash` for a reason unrelated to this item, and repairing a
transcription is curation, which §5 forbids. It is the third time this project's
transcription practice has caught a defect no reader would see — after the
forty-four non-breaking spaces in `arabia-07-cih541` and the byte-order error in
`seasia-08-pong-tuk-lamp` — and the first time an INSTRUMENT found one rather
than a digest comparison.
