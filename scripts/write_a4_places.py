"""Write `subject_places` into the seven literary records (Phase 2, A4).

Generated rather than hand-edited because it is ~70 placements across 7 files
and a hand pass would differ from itself. Idempotent: rebuilds each block and
writes only if the result differs.

Every id below was accepted on its **coordinate and feature types**, never its
name, against `pleiades-places-20260810.csv.gz` on 2026-08-13. Every entry
carries a note recording what it was checked against, and every id examined and
refused is named in the note that displaces it — standing decision of
2026-08-12, because "we looked at this and decided against it" is invisible
otherwise and the next curator re-opens it from scratch.

Two conventions worth stating once rather than in seventy notes:

* **`regional` with no id is the honest answer, not a gap.** Six of these places
  resolve in Pleiades and are marked UNLOCATED, so they carry no coordinate and
  `--check` would fail on them; the rest have no entry at all. The map is
  sparser and that is correct.
* **Roles are relative to the focus.** `source -> focus -> destination`, and
  `mentioned` draws no edge. A place the passage merely names is not a trade
  route, and an edge there would make the network assert something the text
  does not.

Run: python scripts/write_a4_places.py [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data" / "seed_corpus"
sys.path.insert(0, str(ROOT))
from ingest.places import canonical_uri  # noqa: E402

CONFIRMED = "Confirmed against the Pleiades snapshot of 2026-08-10 on 2026-08-13"


def P(name, role, ground, gid=None, note=None, cite=None, contested=None):
    """One entry. `gid` None means regional with no id, which then needs a note."""
    e = {"name": name, "ground": ground}
    if gid:
        e["gazetteer"] = "pleiades"
        e["gazetteer_id"] = gid
        e["uri"] = canonical_uri("pleiades", gid)
    if cite:
        e["ground_citation"] = cite
    if contested:
        e["contested"] = True
        e["contested_citations"] = contested
    e["role"] = role
    if note:
        e["note"] = note
    return e


# Reused across records, so written once.
EGYPT = lambda role: P(
    "Egypt", role, "regional", "766",
    "766 'Aegyptus (Roman imperial province)', locationPrecision 'related', "
    "attested -30..2100 — contemporary with the Periplus, which is why it is "
    "used where Pleiades 837 'Asia Minor' was refused for persia-02 (that one "
    "is attested 1700..1799, a modern cartographic label). Its representative "
    "point 31.201/29.910 is Alexandria's own coordinate, so this placement must "
    "render as an extent and never as a pin; see `has_area` in gazetteer.py.")

BARYGAZA = lambda role, extra: P(
    "Barygaza", role, "stated", "59737",
    f"59737 Barygaza 21.701/72.983, settlement, -330..2099 — Bharuch on the "
    f"Gulf of Khambhat. {extra}")

MUZIRIS_NOTE = (
    "50146 Muziris 10.154/76.213, 'settlement, port', -30..640, locationPrecision "
    "'precise'. That coordinate IS Pattanam. Pleiades has therefore already "
    "adopted the identification `southasia-04-pattanam` treats as open, and "
    "marks it precise; read that record's findspot note before changing this "
    "one. What is contested there is whether the excavation site is Muziris — a "
    "claim about the coordinate. What this record does is name the place, which "
    "is why the ground here is 'stated' and the contested flag is not repeated: "
    "per PLACES.md, contested belongs to an identification, not to the fact "
    "that a text names a place.")

BLOCKS: dict[str, list[dict]] = {}

# ---------------------------------------------------------------- africa-03
BLOCKS["subsaharan_africa/periplus-adulis.json"] = [
    P("Adulis", "focus", "stated", "39271",
      f"{CONFIRMED}: 39271, title 'Adouli', 15.262/39.659, 'settlement, port', "
      f"-30..300 — the Eritrean Red Sea coast near Zula. Title search on the "
      f"corpus's own spelling misses it; found under the Greek form."),
    P("Ptolemais of the Hunts", "mentioned", "stated", "39409",
      "39409 Ptolemais Theron 18.583/37.885, 'settlement, port, anchorage', "
      "-30..2099. §4 places it 3,000 stadia (~530 km) north of Adulis; the "
      "coordinate is ~370 km NNW, the right order and the right direction."),
    P("Oreine", "mentioned", "stated", "39404",
      "39404 'Oreine (island)' 15.464/39.751, island, -30..2100 — ~25 km NNE of "
      "Adulis, inside the gulf, matching §4's 200 stadia seaward. Two decoys "
      "refused on coordinate: 736994 'Patsonteos (Oreine)', a canal in Egypt at "
      "29.750/31.250, and 741584, unlocated."),
    P("the island called Diodorus", "mentioned", "regional", None,
      "Named in §4 as the older anchorage, in text recovered 2026-08-13. "
      "Pleiades 759556 'Diodorou' exists and is UNLOCATED, so it carries no "
      "coordinate and cannot be cached. Note also that the Periplus names a "
      "DIFFERENT Diodorus island at §25, in the Bab el-Mandeb strait; that one "
      "is not this one and must not be substituted."),
    P("Coloe", "source", "stated", "39363",
      "39363 Koloe 14.709/39.553, settlement, -330..300 — inland, ~62 km SSW of "
      "Adulis and ~110 km NE of Aksum, which fits §4's three days inland and "
      "five more to Aksum. Refused on coordinate: 550659 Koloe and 550556 "
      "Gygaia/Koloe, both in Lydia; 554259 and 614708, both unlocated. Pleiades "
      "also attaches the name 'Koloe' to 403627899 Matara and holds 698596572 "
      "Qohaito, the two modern candidates for the site; 39363 is used because "
      "it is the entry Pleiades titles Koloe and dates to the Periplus."),
    P("the Auxumites", "source", "stated", "39303",
      "39303 'A(u)xoume' 14.134/38.721, 'cultural-landscape, settlement', "
      "-30..2100. The same id `africa-01-ezana-stone` carries as its findspot "
      "and `africa-02-aksumite-coin` as its origin — the third use, and the "
      "reason those are separate blocks. §4: all the ivory is brought there and "
      "thence to Adulis."),
    P("Cyeneum", "waypoint", "regional", None,
      "§4's district the ivory is carried through. Pleiades 40186 Kyeneion "
      "resolves and is UNLOCATED — an entry with no coordinate, which "
      "`gazetteer --check` refuses. The schema cannot currently distinguish "
      "'the gazetteer has never heard of this' from 'the gazetteer has it and "
      "does not know where it is'; flagged for A6."),
    P("the Nile", "mentioned", "stated", "727172",
      "727172 'Nilus (river)' 9.904/30.657, river, -6000..2100. §4 has the "
      "ivory coming from beyond it."),
    P("the Alalaei islands", "source", "stated", "39281",
      "39281 'Alalaiou (islands)' 15.729/40.003, 'archipelago, island', "
      "-30..2100 — the Dahlak archipelago, NE of Adulis. Named in §4 as the "
      "source of the tortoise-shell brought to market by the Fish-Eaters, in "
      "text recovered 2026-08-13; before that this place was in Schoff's "
      "English and not in the Greek."),
    EGYPT("source"),
    P("the Arsinoite nome", "source", "stated", "736893",
      "§6's Ἀρσινοητικαὶ στολαί. 736893 'Arsinoites/Krokodeilopolites Nomos' "
      "29.286/30.735, 'nome-gr, label', -330..640 — the Fayyum. Ἀρσινοητικαί is "
      "the NOME adjective, which is what chooses this over 39295 Arsinoe, a Red "
      "Sea station at 12.712/43.251 that is in the right region and is not the "
      "place the cloth is made."),
    P("Diospolis", "source", "stated", "786017",
      "§6's murrine, τῆς γινομένης ἐν Διοσπόλει. 786017 'Diospolis Magna/Thebai' "
      "25.665/32.632, settlement — Upper Egyptian Thebes. Refused: 727111 "
      "'Diospolis Kato' and 730107 'Diospolis', both 31.260/31.573 in the Delta, "
      "and 216859, which a name search returns and which is Kabyle, in Bulgaria."),
    P("Laodicea", "source", "stated", "668290",
      "§6's οἶνος Λαδικηνός. 668290 Laodicea 35.519/35.777, 'settlement, port, "
      "settlement-modern', -550..2100 — Laodicea ad Mare, modern Latakia, whose "
      "wine is the export. The feature type 'port' is what confirms it. Refused: "
      "668291 'Laodicea ad Libanum' 34.557/36.519, inland, and the several "
      "Anatolian Laodiceas a title search returns first."),
    P("Italy", "source", "regional", "1052",
      "§6's οἶνος Ἰταλικός. 1052 Italia 43.694/11.095, region, "
      "locationPrecision 'related', attested **-30..300** — contemporary. "
      "Refused: 452346 'Italia (region)' 38.393/16.198, which is 'precise' and "
      "therefore the more tempting of the two, but is dated -750..-330 — the "
      "archaic Italia of the southern toe, four centuries too early; and 992073 "
      "'Italia (Diocese)', unlocated. A precise coordinate for the wrong "
      "century is still the wrong place."),
    P("the Calf-Eaters", "mentioned", "regional", None,
      "§5's Μοσχοφάγοι, from whose territory Zoskales' kingdom runs. A people, "
      "not a settlement; nothing resolves in either gazetteer under any form "
      "searched."),
    P("Barbaria", "mentioned", "regional", None,
      "§5's ἡ ἄλλη Βαρβαρία, the far limit of Zoskales' rule — the Somali "
      "coast. **Pleiades 471890 'Barbaria' was examined and refused**: it sits "
      "at 40.020/9.084, which is Barbagia in Sardinia. A name match would have "
      "taken it and drawn a Roman-African trade network through the "
      "Mediterranean."),
]

# ---------------------------------------------------------------- arabia-01
BLOCKS["arabia/periplus-frankincense-country.json"] = [
    P("Cana", "focus", "stated", "39355",
      f"{CONFIRMED}: 39355 Kane 13.992/48.236, settlement, -30..1999 — Bir Ali "
      f"on the Hadrami coast. The passage's port: §28 lists what is imported "
      f"into and exported from it."),
    P("Arabia Eudaemon", "mentioned", "stated", "39269",
      "§27 measures the coast from it. 39269 'Adane/Athenae/Eudaimon Arabia' "
      "12.772/45.039, settlement — Aden. **Refused: 746710 'Arabia Eudaemon'**, "
      "a peninsula label at 28.960/35.350 in north-west Arabia, which matches "
      "the term exactly and is a thousand kilometres wrong. Note 39269 was also "
      "examined and refused as the Aksumite coin's findspot, for a different "
      "reason: there it was ~300 km from where the coin was found."),
    P("the Island of Birds", "mentioned", "stated", "39405",
      "39405 'Orneon Ins.' 13.932/48.387, island — ~17 km east of Kane, "
      "consistent with §27's 120 stadia. Refused: 50179 'Orneon? Pr.' in Sri "
      "Lanka and 50706, unlocated."),
    P("Trullas", "mentioned", "regional", None,
      "§27's second desert island off Kane. Nothing resolves; the only hit for "
      "the name is 424659855 San Nicola di Trullas, a medieval church in "
      "Sardinia, refused on coordinate and on date."),
    P("Sabbatha", "source", "regional", None,
      "§27's inland metropolis where all the frankincense of the country is "
      "stored before going to Cana — Shabwa. Pleiades 906027 "
      "'Sabbatha/Sabatha/Sabdata' resolves and is UNLOCATED, so it has no "
      "coordinate to cache. Same class as Kyeneion; see A6."),
    BARYGAZA("destination",
             "Named in §27's closing clause — 'this place has a trade also with "
             "the far-side ports' — which was absent from the original text on "
             "disk until 2026-08-13 and existed only in Schoff's English."),
    P("Scythia", "destination", "regional", "59850",
      "§27's Σκυθία. 59850 Indoskythia 26.366/67.811, 'region, label', -30..300 "
      "— Indo-Scythia, the lower Indus. **Refused: 1001892 'Skythia'** "
      "42.500/27.500, a province on the Black Sea, and 222186 'Skythias', "
      "unlocated. A far-side port of Cana is on the Indian Ocean, which is what "
      "decides it. Recovered text, as above."),
    P("Ommana", "destination", "regional", None,
      "§27's Ὄμμανα, a Persian Gulf port (the Periplus returns to it at §36). "
      "Nothing resolves: the exact form returns nothing, and 'Omana' matches "
      "only Spanish and Italian sites containing 'romana'. Recovered text."),
    P("the neighbouring coast of Persia", "destination", "regional", None,
      "§27's τῆς παρακειμένης Περσίδος. Refused: 609499 'Persis (mountain)' "
      "38.847/30.809, which is in Phrygia. No entry covers the Persian coast as "
      "the passage means it. Recovered text."),
    EGYPT("source"),
    P("Muza", "mentioned", "stated", "39390",
      "§28 twice uses it as the comparison — 'as at Muza'. 39390 'Mouza "
      "Emporion' 13.261/43.421, station, -330..300 — modern Mocha on the Red "
      "Sea. Refused: 756300531 Gebel el-Muzawaka, a cemetery in the Egyptian "
      "western desert, which is what a bare title search returns first."),
    P("the Sachalites bay", "mentioned", "stated", "39419",
      "§29's ὁ λεγόμενος Σαχαλίτης. 39419 'Sachalites Sinus' 15.927/52.209, "
      "'water-open, bay', -30..2100 — the Dhofar coast."),
    P("the Frankincense Country", "source", "regional", "39370",
      "§27 and §29's χώρα λιβανωτοφόρος, the region the incense comes from. "
      "39370 'Libanophoros Chora' 17.411/53.407, region, -30..300 — note "
      "Pleiades titles it *Libano-*, not *Libanoto-*, which is why a search on "
      "the text's own form returned only a name-list hit."),
]

# ---------------------------------------------------------- southasia-02
BLOCKS["south_asia/periplus-muziris.json"] = [
    P("Muziris", "focus", "stated", "50146", MUZIRIS_NOTE),
    P("Calliena", "mentioned", "stated", "50023",
      "50023 Kalliena 19.273/73.139, settlement, -30..640 — Kalyan, near "
      "Mumbai. §53's list of market-towns begins from it."),
    P("Semylla", "mentioned", "stated", "50261",
      "50261 Semylla 18.521/72.947, settlement, -30..300 — the Konkan coast."),
    P("Mandagora", "mentioned", "stated", "50116",
      "50116 'Mandagara?' 17.951/73.039, settlement, -30..300. Pleiades' own "
      "query mark is retained in its title and is its uncertainty, not ours."),
    P("Palaepatmae", "mentioned", "stated", "50196",
      "50196 'Palaipatmai?' 17.526/73.302, settlement, -30..300."),
    P("Melizeigara", "mentioned", "regional", None,
      "§53's Μελιζειγάρα. No entry in Pleiades under any form searched; one of "
      "the Konkan market-towns that has never been located."),
    P("Byzantion", "mentioned", "stated", "49929",
      "**Not Constantinople.** 49929 'Byzantion?' 16.503/73.340, settlement, "
      "-30..300 — a market-town on the Konkan coast, in §53's list between "
      "Melizeigara and Toparon. The case where accepting an id on its "
      "coordinate rather than its name pays for the whole rule."),
    P("Toparon", "mentioned", "stated", "50308",
      "50308 'Toparon?' 16.220/73.585, settlement, -30..300. The Greek reads "
      "Τοπαρόν; Schoff prints 'Togarum', which resolves to nothing — the "
      "placement follows the original."),
    P("Tyrannosboas", "mentioned", "stated", "50315",
      "50315 'Tyrannosboas?' 16.079/73.472, settlement, -30..300. Greek "
      "Τυραννοσβόας against Schoff's 'Aurannohoas', which resolves to nothing."),
    P("the Sesecrienae islands", "mentioned", "stated", "50264",
      "50264 'Sesekreienai? Inss.' 17.500/72.500, 'archipelago, label', "
      "locationPrecision 'rough'."),
    P("the island of the Aegidii", "mentioned", "stated", "49842",
      "49842 'Aigidion Nesos' 15.432/73.276, label, -30..300."),
    P("the island of the Caenitae", "mentioned", "stated", "50015",
      "50015 'Kaineiton Nesos' 12.500/72.500, island, locationPrecision 'rough'."),
    P("Chersonesus", "mentioned", "regional", None,
      "§53's Χερσόνησος, on the Konkan. Twenty-three entries carry the name and "
      "every one is Black Sea, Aegean, Libyan or Thracian; none is Indian. "
      "Refused rather than resolved to a Greek peninsula."),
    P("the White Island", "mentioned", "stated", "50091",
      "§53's Λευκὴ νῆσος. 50091 'Leuke (island)' 14.019/74.325, island, "
      "-30..2100 — the Karnataka coast. Found only on a description match; a "
      "title search returns 226677 'Leuke Ins./Achilleos Nesos' at "
      "45.255/30.204, which is Snake Island in the **Black Sea**, and which is "
      "refused."),
    P("Naura", "waypoint", "stated", "50160",
      "50160 'Naoura/Nitriae' 14.281/74.450, settlement, -30..300 — §53 makes "
      "it one of the first two markets of Limyrike, on the way down the coast "
      "to Muziris. Refused: 638923 Kitanaura, in Lycia."),
    P("Tyndis", "waypoint", "stated", "50312",
      "50312 Tyndis 10.764/75.926, settlement, -30..300 — the Kerala coast, "
      "§54's 500 stadia from Muziris. Refused: 50313 'Tyndis (river)' at "
      "22.500/82.500, 'rough', which shares the name and is inland."),
    P("Nelcynda", "mentioned", "stated", "50165",
      "50165 Nelkynda 9.273/76.559, settlement, -30..300 — §54 puts it ~500 "
      "stadia from Muziris and in the other kingdom, the Pandian."),
    P("Bacare", "waypoint", "stated", "49890",
      "§55's village at the river mouth where ships drop down to take on cargo. "
      "49890 Bakare 9.351/76.368, 'settlement, settlement-modern', -30..2099. "
      "**Refused: 785982 'Bakare'**, an Egyptian mine at 25.210/34.274 — the "
      "same name, the wrong continent."),
    P("the Kingdom of Cerobothra", "mentioned", "regional", None,
      "§54's βασιλεία Κηπροβότρου, the Chera kingdom, to which Tyndis and "
      "Muziris both belong. Nothing resolves: 246333 'Chera' is a settlement in "
      "Spain and is refused; the other hits are Italian and Anatolian."),
    P("the Kingdom of the Pandion", "mentioned", "regional", "50201",
      "§54's βασιλεία τῆς Πανδίονος, Nelkynda's kingdom. 50201 Pandion "
      "9.654/78.194, label, -330..640 — the Pandya country around Madurai. "
      "Refused: 599854 'Pandion Collis', a mountain in Caria."),
    P("Limyrike", "mentioned", "regional", "50092",
      "§53 and §56's Λιμυρική. 50092 Limyrike 11.072/75.922, label, -30..300. "
      "**Schoff prints 'Damirica' throughout**, which resolves to nothing; the "
      "placement follows the Greek."),
    P("Ariake", "source", "regional", None,
      "§54: ἀκμάζουσα τοῖς ἀπὸ τῆς Ἀριακῆς εἰς αὐτὴν ἐρχομένοις πλοίοις — "
      "Muziris thrives on the ships that come to it FROM ARIAKE. **Schoff "
      "prints 'from Arabia' here**, and Arabia is a thousand miles from the "
      "Konkan; this entry is the reason the standing rule is that a placement "
      "follows the original and not the reference translation. Two ids were "
      "examined and neither is used: 59700 'Ariake/Larike' 22.304/71.976, the "
      "Saurashtra label, and 49874 'Ariake Sadenon' 18.143/74.499, inland "
      "Maharashtra. The Periplus's Ariake spans the coast between them (cf. §41, "
      "where it adjoins Barygaza, and §14), so either id would assert a "
      "narrower place than the text does. Regional, and the map is sparser."),
    BARYGAZA("mentioned",
             "§56 uses it only as the measure of how much wine is imported — "
             "'as much as at Barygaza'. A comparison, so no edge."),
    P("Cottonara", "source", "stated", "49953",
      "§56: pepper is produced in one region only, τῇ λεγομένῃ Κοττοναρικῇ. "
      "49953 Cottonara 9.004/76.889, 'district, label', -30..300."),
    P("the Ganges", "source", "stated", "59822",
      "§56's νάρδος ἡ Γαγγητική, spikenard from the Ganges. 59822 'Ganges "
      "(river)' 25.932/83.780, river, -330..2100. **Refused: 49984**, which "
      "carries the name 'Ganges' and is a river in **Sri Lanka**."),
    P("Chryse", "source", "regional", None,
      "§56's tortoise-shell ἥ τε Χρυσονησιωτική, from Chryse Island. Both "
      "candidates resolve and are UNLOCATED — 60485 'Chryse/Aurea' and 50630 "
      "'Chrysei' — so neither carries a coordinate. The Aegean and Anatolian "
      "Chryses are refused on coordinate."),
    EGYPT("source"),
]

# ---------------------------------------------------------------- eastasia-01
BLOCKS["east_asia/weilue-da-qin.json"] = [
    P("Da Qin", "focus", "regional", None,
      "大秦, the passage's subject — the Roman Empire, also called 犂靬 Lijian in "
      "the same sentence. A polity, not a settlement, and Pleiades holds no "
      "entry for it under any form searched. The English gloss identifies it "
      "with Rome, but that is the translator's identification and the record "
      "carries no citation for it, so the honest ground is regional with no id "
      "rather than `identified` without the scholar who made the "
      "identification. Pleiades 423025 Roma 41.890/12.491 was examined and is "
      "not used: the city is not the empire, and the Chinese excerpt is elided "
      "at exactly the point where the capital is described."),
    P("Anxi", "mentioned", "regional", None,
      "安息, west of which Da Qin lies — Parthia. Refused: 952097 "
      "'Parthyene/Parthia' 38.500/57.500 and 590282460 'Parthian empire', which "
      "is locationPrecision 'related' and dated **2000..2099** — a modern label, "
      "not an ancient place. Both are identifications of the Chinese name "
      "rather than the name itself, and the record has no citation for either."),
    P("Tiaozhi", "mentioned", "regional", None,
      "條支, named beside Anxi. The gloss offers Characene and Susiana; Pleiades "
      "912905 'Mesene/Characene' 31.468/47.344 was examined and is not used, "
      "for the same reason as Anxi — it is the gloss's identification and no "
      "citation supports it here."),
    P("Angu", "waypoint", "regional", None,
      "安谷城, the city on the Parthian frontier where one takes ship. The gloss "
      "offers Gerrha; Pleiades holds no resolving entry for it, only the name "
      "'sinus Gerrhaicus' on 932455, which is a gulf and not the city."),
    P("Haixi", "destination", "regional", None,
      "海西, 'west of the sea', where the crossing lands. The gloss identifies "
      "it with Egypt; that identification is the translator's and is not "
      "cited, so Pleiades 766 Aegyptus is deliberately NOT used here even "
      "though it is used for Egypt elsewhere in this corpus — there the Greek "
      "names Αἴγυπτος outright, and here the text names 海西."),
]

# ---------------------------------------------------------------- eastasia-02
BLOCKS["east_asia/hou-hanshu-166-envoy.json"] = [
    P("Rinan", "focus", "regional", None,
      "日南, the commandery on the central Vietnamese coast the embassy arrived "
      "through — 自日南徼外, 'from beyond the frontier of Rinan'. Pleiades is a "
      "Greco-Roman gazetteer and holds nothing here; this is GeoNames "
      "territory, and the GeoNames reader is the outstanding Block A item. "
      "Promote to a named place when it exists."),
    P("Da Qin", "source", "regional", None,
      "大秦, whose king 安敦 sent the envoys. Same reasoning as "
      "`eastasia-01-weilue`: a polity with no gazetteer entry, and the "
      "identification with Rome is the gloss's rather than the record's. "
      "Luoyang, the court the tribute was offered to, is NOT named in this "
      "passage and is deliberately not placed."),
]

# ---------------------------------------------------------- southasia-01
BLOCKS["south_asia/akananuru-149-yavanas.json"] = [
    P("Muciri", "focus", "stated", "50146",
      "முசிறி, where the Yavana ships arrive with gold and leave with pepper. "
      + MUZIRIS_NOTE + " This record and `southasia-02-periplus-muziris` name "
      "the same place and use the same id; the two must not diverge."),
    P("the Culli", "mentioned", "regional", None,
      "The river the Yavana ships stir to foam. Pleiades 50234 'Pseudostomos "
      "(river)' 9.848/76.819 is the Periyar under its Greek name and is the "
      "likely referent, but Culli ≈ Periyar ≈ Pseudostomos is a chain of "
      "scholarly identifications and this record carries a citation for none of "
      "them. `identified` without its ground_citation is an assertion wearing "
      "the word; regional is the honest ground until the citation exists."),
    P("the Chera country", "mentioned", "regional", None,
      "The poem places the Culli in Chera territory. Nothing resolves: 246333 "
      "'Chera' is in Spain and is refused, as it is for `southasia-02`."),
    P("the land of the Yavanas", "source", "regional", None,
      "யவனர், whose ships bring the gold. **Yavanar names a people, not a "
      "place** — a Tamil term for Greeks and Romans generally — so there is no "
      "place to resolve and no id that would not be an invention. The role is "
      "source because the poem is explicit that the gold arrives with them."),
]

# ---------------------------------------------------------- southasia-03
BLOCKS["south_asia/muziris-papyrus.json"] = [
    P("Muziris", "focus", "stated", "50146",
      "κατὰ Μουζεῖριν at recto col. ii line 12 — 'the loan contracts made at "
      "Muziris'. **This record did not name its own port until 2026-08-13**: "
      "the excerpt ran to line 8, and Muziris appeared only in the title, the "
      "notes and the papyrus's conventional name. " + MUZIRIS_NOTE),
    P("Koptos", "waypoint", "stated", "786010",
      "Κόπτος, twice in the recto — the goods go by camel across the desert to "
      "the public tax-receiving warehouses there, then down the river. 786010 "
      "Coptos 25.996/32.816, 'settlement, port, archaeological-site', "
      "-750..640 — modern Qift on the Nile."),
    P("Alexandria", "destination", "stated", "727070",
      "εἰς τὴν ἐν Ἀλεξανδρείᾳ τῆς τετάρτης παραλημπτικὴν ἀποθήκην — the "
      "warehouse of the fourth-tax at Alexandria, where the cargo ends. 727070 "
      "Alexandria 31.201/29.910, 'settlement, port', -2010..2000. Refused: the "
      "forty-odd other Alexandrias, in Aria, Carmania, Arachosia and elsewhere, "
      "which a title search returns first."),
    P("the Ganges", "source", "stated", "59822",
      "νάρδου Γανγιτικῆς on the verso — Gangetic nard, sixty boxes of it, the "
      "first item of the cargo valuation. Named adjectivally, which is how the "
      "text attests it. Same id and the same refusal as `southasia-02`: 49984 "
      "is a river in Sri Lanka."),
]


def main(argv: list[str]) -> int:
    check = "--check" in argv
    changed = 0
    for rel, block in BLOCKS.items():
        path = SEED / rel
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("subject_places") == block:
            print(f"  =  {rel} ({len(block)}) already current")
            continue
        roles: dict[str, int] = {}
        for e in block:
            roles[e["role"]] = roles.get(e["role"], 0) + 1
        ided = sum(1 for e in block if "gazetteer_id" in e)
        print(f"  -> {rel}: {len(block)} places, {ided} with an id, {roles}")
        changed += 1
        if check:
            continue
        record["subject_places"] = block
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"\n{changed} record(s) {'would be ' if check else ''}written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
