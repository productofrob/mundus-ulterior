# The browser passes F5 Part 2 asked for — run 2026-09-05

*All four were "blocked to every fetcher tried and none is blocked to a person."
Two are run. Both were blocked to fetchers. **Neither is blocked to a person, and
neither was blocked for the reason the hunt recorded.***

---

# Pass 1 — Bhaṭṭotpala's Vivṛti on Bṛhatsaṃhitā 2.14. ANSWERED YES.

**Run in Chrome against both open editions.**

| the question asked | the answer |
| --- | --- |
| is there commentary under 2.14? | **yes**, in both editions, agreeing in shape |
| running prose or a three-word gloss? | **neither** — about three lines of gloss, then `तथा च` introducing a quoted authority set as verse, then about two lines closing `इति ॥ १४ ॥` |
| roughly how many lines? | **about ten printed lines**, a third of a page |
| which scan is more legible? | **Dvivedī, VSS 18, CC0** |

- **Dvivedī** — BookReader leaf **n101** of 662, printed p. **82**. Cleaner
  letterpress, higher contrast, and the whole verse-14 unit on ONE page.
- **Tripāṭhī** — leaf **n117**, printed p. **75**, running onto p. 76.

**The runbook's page-density inference is refuted, by the mechanism it warned
about.** It put verse 14 near printed pp. 17–19, "roughly scan pages 47–49" and
said in terms that this "must not be written up as a reading". It was right to.
Tripāṭhī leaf n47 is printed p. 3 and leaf n61 is printed p. 17, **both still
`[अ. १] उपनयाध्यायः`**. The item carries a front-matter offset of about 42–44
leaves and adhyāya 2 does not begin until printed p. ~71. The estimate was
**seventy leaves short**, and the error was entirely in assuming no offset.

**Search-inside is dead on the Dvivedī item** — the query returns "Sorry, there
was an error with your search", consistent with the never-built index the hunt
recorded. The location is eyes-only.

**Two independent open witnesses to the same commentary**, so a capture can be
checked against something other than itself — stronger than record 36's
repetition check, which compared a paste to another paste of the same page.

**KNOW WHAT THE "YES" BOUGHT.** The runbook warned that discursive prose commits
the curator to hand-capturing a page of Devanagari from a corrupt-OCR scan, the
most expensive capture in the tranche. It is not that. Ten lines from a clean
CC0 letterpress scan, on one page, checkable against a second edition.

**Consequence: South Asia's `verbatim_machine_english` slot is FILLABLE and is
taken.** F5 delivers **6 of 7**, the vme tier **5 of 10**, the corpus **55**.
Only Persia's vme slot is recorded as a searched failure.

*CORRECTED 2026-09-05, after the close. This paragraph read "the vme tier **6 of
10**". The tier stood at 4 and one more record would have made it 5. The slot was
not taken -- ruling 75 -- so the tier is 4 of 10 and this whole paragraph is a
counterfactual that did not happen. FINDING 75.*

**AND `eastasia-07-tang-huiyao.json` NOW CONTAINS A FALSE SENTENCE.** Its notes
call record 36 "the LAST such record this project can curate", on the strength of
F6 and F7 placing no vme slot. The Bhaṭṭotpala record takes that title.
`F5_PART3_START.md` and the tier note repeat it. **The correction must land in
the same commit as the Bhaṭṭotpala record**, or the corpus holds two records each
claiming to be the last of its tier.

---

# Pass 3 — DASI, `dasi.cnr.it`, CIH 541. IT OPENS. COMPLETELY.

**`F5_CANDIDATES.md` recorded this as the single most valuable thing lost in the
hunt:** *"DASI, the standard open corpus for Ancient South Arabian, is behind an
Anubis anti-bot wall and returned 'Access Denied' to every route tried. This
closes the whole Sabaic vein for now."*

**Chrome was not challenged once.** No interstitial, no delay, no login. What is
behind it:

```
CIH 541 Sadd Ma'rib 5
  stable URL      dasi.cnr.it/project/1/epigraphs/2382
  DOI             10.82194/dasi-epi-2382        -- per record
  LICENCE         CC BY 4.0, stated on the record itself:
                  "The above license applies to the data in this record, but not
                   to any images displayed. The images are the property of third
                   parties and are either used with permission or reproduced
                   from publications (see the credits below each image)."
  cite as         CIH 541 Sadd Ma'rib 5
  text            136 numbered lines of Late Sabaic, with word dividers,
                  restorations, line-continuation and editorial markers intact
  TRANSLATIONS    TWO -- CSAI's own, and Nebes 2005. The CSAI translation is
                  English, on the record, under the same CC BY 4.0.
  apparatus       named-editor variants printed on the record:
                    84       Glaser and CIH: (S²)wlmn.
                    87       Muller and CIH: Frnt.
                    129-130  Muller and CIH: 'l[y] hlb.
  date            548 CE, "Date accuracy: Accurate"
  object          Marib Museum, inv. BAR 2, monumental stela, h.250 w.66 th.40
  site            linked site record, Ma'rib, Yemen -- so places resolve
  bibliography    ten entries with full references
```

**And the Roman content is in the text, at line 89.** The passage listing the
delegations reads `mḥs²kt ngs²yn` — the delegation of the Negus — then
`mḥs²kt mlk Rmn`, the delegation of the king of Rome, then `tnblt mlk Frs¹`, the
king of Persia, then the envoys of al-Mundhir, of al-Ḥārith b. Jabala and of
Abū Karib b. Jabala. Exactly what the hunt described and could not reach.

**The corpus behind it: 9,102 actual epigraphs of 14,617 titles**, Sabaic,
Minaic, Qatabanic and Ḥaḍramitic, each with a stable URL and a DOI.

## What this record would be, if F6 takes it

`verbatim_with_provenance` with a CC BY 4.0 source text AND a CC BY 4.0 English
translation on the same page, a DOI, a stable per-record URL, a linked site
record for the placement, and **three named-editor variant readings in a printed
apparatus** — Glaser against CIH, Müller against CIH twice. That is
gloss-capable on the same standard `arabia-05-ruwafa` was declared on, and it is
better provenanced than anything F5 curated.

**It is not F5's.** Both Arabia slots are filled and the sub-tranche's allocation
is closed. It is the strongest thing now sitting unclaimed in front of F6 and F7,
and the Sub-Saharan Africa F6 slot that `requires_provenance: local_language`
should be read against it too.

## The exposure, declared

**This session read CIH 541's text and the opening of its English translation.**
That is hunt work and the hunt has always read at source — `F5_CANDIDATES.md`'s
own provenance block lists what Part 2 read. But if F6 curates this record, the
capture is still a curator's blind paste, and this session is no longer an
independent check on it. Same note as browser pass 1 and `southasia-05`.

---

# What the two passes have in common, and it is a finding

**Both negatives were about FETCHERS and both were recorded as facts about
SOURCES.**

```
recorded by the hunt                          measured by a person
------------------------------------------    ------------------------------
"the original cannot be reached" --            ten legible lines on one page
  fulltext/inside.php 403, djvu OCR            of a clean CC0 letterpress scan
  "significantly corrupted throughout"

"Anubis anti-bot wall, Access Denied to        CC BY 4.0, a DOI, a stable URL,
  every route tried. This closes the           two translations and a
  whole Sabaic vein"                           named-editor apparatus
```

**`F5_CANDIDATES.md`'s candidate finding cannot be written as it stands.** It
says the `verbatim_machine_english` tier's yield tracks a tradition's
**digitisation** history — "East Asia has Kanripo; Persia and South Asia have
photographs of books." Pass 1 shows the South Asian photographs are perfectly
readable by a person, and pass 3 shows the Sabaic corpus was never a
digitisation problem at all: it is keyed, licensed, DOI'd and free, and it was
invisible because a bot check stood in front of it.

**What the tier's yield actually tracked, in this hunt, is what an automated
fetcher could reach.** That is a claim about anti-bot infrastructure and about
this project's own capture method — not about scholarship, and not about
digitisation. It is also a sharper claim than either of the ones it replaces,
because it predicts something checkable: **put a person in front of the same
sources and the negatives move.** Two for two so far.

**Ruling 39 is why this document does not take it.** This is the hunt half.
Part 3's result document rules.

---

# Passes 2 and 4, still owed

- **Pass 2 — `parsigdatabase.com` and `noorlib.ir`.** Both have refused every
  automated request since F3, and **every claim in this repository resting on
  parsigdatabase rests on a human pass nobody has made.** Given passes 1 and 3,
  the prior on these two has moved a long way.
- **Pass 4 — the Mojmal's title page**,
  `archive.org/details/MujmalUt-TawarikhWal-QisasFarsi/page/n0/mode/2up` —
  editor, publisher, year. Expected Bahār, Tehran 1318 Sh./1939.

Neither fills an F5 slot.
