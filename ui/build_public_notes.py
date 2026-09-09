"""Build the PUBLIC_NOTES table for ui/index.html.

Each entry names a START and END marker inside the record's OWN note; the
excerpt is SLICED from it, never retyped, so every character the page shows is
the curator's. check_ui.mjs then re-derives the same property at run time.

A marker that is missing, or that appears more than once, is a hard error: an
ambiguous boundary is how an excerpt silently becomes a different sentence.
"""
import json
import re
import subprocess
from pathlib import Path

UI = Path(__file__).resolve().parent          # ui/

# doc_id -> [(start_marker, end_marker), ...]   [] means: nothing public to show.
SPEC = {
 "arabia-07-cih541": [("Line 89:", "after the Negus.")],
 "arabia-03-jsnab17": [("Notable for the epithet", "legal-funerary text")],
 "arabia-05-ruwafa": [("A temple on the north-west", "a bilingual and not a translation.")],
 "arabia-02-palmyrene-tariff": [
     ("Palmyra sat astride", "non-Roman-language legal text."),
     ("What the tariff regulates:", "economic life of any part of the Roman Empire.'")],
 "arabia-01-periplus": [("Directly documents the incense-route", "Red Sea trade to South Arabia")],
 "arabia-04-jabal-dabub": [
     ("the pre-Islamic South Arabian religious vocabulary",
      "relevant to Red Sea contact narratives.")],
 "arabia-06-syllaeus": [
     ("It is not an embassy", "his friends died.")],
 "arabia-08-walters-marib-pediment": [
     ("A nude fertility goddess", "as an IMAGE rather than as a word."),
     ("`arabia-07-cih541` is the Great Dam", "different kinds of contact.")],
 "eastasia-06-cefu-yuangui": [
     ("A Byzantine embassy", "on a dated day."),
     ("Fulin is one line among", "filed beside its neighbours.")],
 "eastasia-02-hou-hanshu": [
     ("Records what Chinese sources present", "identified with Marcus Aurelius.")],
 "eastasia-03-hwangnam-glass": [
     ("One of the clearest physical-evidence anchors", "sources (eastasia-01, -02).")],
 "eastasia-04-jingjiao-stele": [
     ("A Christian community in Tang China", "as much as the bounds are.")],
 "eastasia-09-jiutangshu-fulin": [
     ("A Tang-dynasty history describing Byzantium", "`priests of great virtue`.")],
 "eastasia-05-liangshu-qin-lun": [
     ("This is the most concrete Roman person", "dies on the road.")],
 "eastasia-08-songshi-fulin": [
     ("It is a description — climate", "coins with no square hole.")],
 "eastasia-07-tang-huiyao": [
     ("A Tang administrative dossier", "gifts of lions and antelopes in Kaiyuan 10.")],
 "eastasia-01-weilue": [],
 "persia-05-abnun": [
     ("A courtier — the master of ceremonies", "after the king and after himself.")],
 "persia-04-bronze-heracles": [
     ("This is a GREEK statue", "Lucius Verus's Parthian war of 161-166.")],
 "persia-03-coin": [
     ("Coinage of Shapur I is directly contemporary", "the Valerian campaign it narrates")],
 "persia-07-met-ewer-anahita": [
     ("either a Sasanian court silversmith", "leaving the reading open")],
 "persia-06-shahrestaniha": [
     ("This is an administrative list", "as an adversary")],
 "persia-02-silver-plate": [
     ("Sasanian royal silver plate imagery", "(see British Museum curator's comments).")],
 "persia-01-skz": [
     ("directly documents Roman emperors", "trilingual monumental inscription.")],
 "scandinavia-02-gudme-hoard": [
     ("Gudme was one of Iron Age Denmark's", "ordinary circulating currency")],
 "scandinavia-01-hoby-treasure": [
     ("a named Roman maker", "named/identifiable local recipient context.")],
 "scandinavia-04-illerup-adal": [
     ("the Illerup Roman coins arrived as war booty",
      "(military/mercenary rather than trade or gift-exchange)")],
 "scandinavia-07-rycksta-grikkium": [
     ("`walhakurne` and `gulli` are the same substance", "what the two inscriptions say."),
     ("It does not say `Grikkir` means", "quotes them and stops.")],
 "scandinavia-05-thorsberg-chape": [
     ("the Thorsberg moor is a votive deposit",
      "a region that received Roman goods and a region that answered them.")],
 "scandinavia-06-tjurko-bracteate": [
     ("`walhakurne` is a compound", "the connection having got as far as the language."),
     ("Bracteates are the Scandinavian descendants", "calls its own material Roman.")],
 "scandinavia-03-vimose": [
     ("Vimose is a weapon-sacrifice bog deposit", "the very same findspot and period.")],
 "southasia-01-akananuru-149": [
     ("One of only 9 Yavana references", "'arriving with gold and departing with pepper' at Muziris")],
 "southasia-07-bm-claudius-aureus": [
     ("A Julio-Claudian gold coin", "desecration and damnation in imperial Rome`."),
     ("`EX.S.C. OB CIVES SERVATOS`", "a chisel through the portrait.")],
 "southasia-05-brihatsamhita": [
     ("Varāhamihira, laying down who may be trusted",
      "conceding its learning while keeping its rank.")],
 "southasia-06-cosmas-taprobane": [
     ("A Roman merchant from Adulé", "paraded round the city with drums."),
     ("The king does not weigh armies", "picked for export to the island`.")],
 "southasia-03-muziris-papyrus": [
     ("Direct documentary evidence of the financial scale",
      "with hard numbers.")],
 "southasia-04-pattanam": [
     ("Roman amphora/terra sigillata shards", "support the port identification.")],
 "southasia-02-periplus-muziris": [
     ("Direct external (Roman-Greek) corroboration", "for the same port")],
 "seasia-04-dong-yen-chau": [
     ("This is the local voice of the same coast",
      "arriving in language rather than in objects.")],
 "seasia-06-kedukan-bukit": [
     ("Srivijaya held the Straits of Malacca", "between the Mediterranean and China."),
     ("Kedukan Bukit is the logistics document", "its religious counterpart.")],
 "seasia-03-khao-sam-kaeo": [
     ("Khao Sam Kaeo is an early port-city",
      "documented textually in the South Asia cluster (Periplus, Muziris papyrus).")],
 "seasia-05-my-son-b6": [
     ("Mỹ Sơn is the dynastic sanctuary of Champa",
      "as language and liturgy rather than as objects, and dated to the day.")],
 "seasia-01-oc-eo-medallion": [
     ("these are imitation pendants, not genuine circulating Roman coinage")],
 "seasia-02-oc-eo-site": [
     ("Óc Eo is the maritime-route site",
      "documented from the Chinese side by the Hou Hanshu (eastasia-02)."),
     ("Scholarly identification with Ptolemy's 'Cattigara' remains debated")],
 "seasia-09-oc-eo-unesco": [
     ("`International trade has been proven", "imported from India and Mediterranean countries`"),
     ("Rome, Han China and Persia in one clause",
      "goods turned up in one Mekong Delta town")],
 "seasia-08-pong-tuk-lamp": [
     ("A cast bronze lamp with its lid moulded", "`the Indian traders brought into the country`, along a route the district still sits on.")],
 "seasia-07-talang-tuo": [
     ("Srivijaya held the Straits of Malacca", "between the Mediterranean and China."),
     ("Talang Tuo is the religious counterpart", "two registers within thirteen months.")],
 "africa-05-adulis-throne": [
     ("The king sends a fleet and an army",
      "Leuke Kome is the Roman Red Sea port the Periplus names")],
 "africa-02-aksumite-coin": [
     ("Aksum was one of only a handful", "Red Sea gold-trade economy."),
     ("This specimen's findspot in Yemen", "a direct data point for Aksum-Arabia contact")],
 "africa-07-cosmas-sasu": [
     ("it follows an Aksumite state expedition",
      "with neither side speaking the other's language."),
     ("Cosmas is an Alexandrian merchant", "had been to Adulis himself")],
 "africa-06-ezana-rie189": [
     ("Nothing in these fourteen lines names Rome.", "the Lord of Heaven.")],
 "africa-01-ezana-stone": [
     ("Often called the 'African Rosetta Stone.'", "Greek-speaking Mediterranean world"),
     ("the inscription records Ezana's military campaigns",
      "his conversion to Christianity.")],
 "africa-03-periplus-adulis": [
     ("This is the first surviving external", "as an early Aksumite ruler)")],
 "africa-04-silko-talmis": [
     ("Silko calls himself", "in nothing the Romans did.")],
}

# ---- load the bundle exactly as the page does -------------------------------
node = subprocess.run(
    ["node", "-e", """
      const fs=require('fs'); global.window={};
      new Function('window', fs.readFileSync('data.js','utf8'))(global.window);
      const out={}; for (const [id,r] of Object.entries(global.window.MU_DATA.corpus))
        out[id]=r.notes||""; process.stdout.write(JSON.stringify(out));
    """],
    cwd=UI, capture_output=True, text=True, check=True)
NOTES = json.loads(node.stdout)

missing = [d for d in NOTES if d not in SPEC]
extra = [d for d in SPEC if d not in NOTES]
assert not missing, f"records with no entry in SPEC: {missing}"
assert not extra, f"SPEC names records that do not exist: {extra}"

entries = []
for doc in NOTES:
    note = NOTES[doc]
    frags = []
    for pair in SPEC[doc]:
        start, end = ((pair, pair) if isinstance(pair, str) else pair)
        if note.count(start) != 1:
            raise SystemExit(f"{doc}: start marker {start!r} appears {note.count(start)} times")
        if note.count(end) != 1:
            raise SystemExit(f"{doc}: end marker {end!r} appears {note.count(end)} times")
        i, j = note.index(start), note.index(end) + len(end)
        if j <= i:
            raise SystemExit(f"{doc}: end marker precedes start marker")
        frag = re.sub(r"\s+", " ", note[i:j]).strip()
        # The stored fragment must survive a whitespace-insensitive search of the
        # note, which is what the guard checks; nothing else is normalised.
        assert re.sub(r"\s+", " ", note).find(frag) >= 0, f"{doc}: slice did not round-trip"
        frags.append(frag)
    entries.append((doc, frags))

def js(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

lines = ["const PUBLIC_NOTES = {"]
for doc, frags in entries:
    if not frags:
        lines.append(f"  {js(doc)}: [],")
        continue
    lines.append(f"  {js(doc)}: [")
    for f in frags:
        lines.append(f"    {js(f)},")
    lines.append("  ],")
lines.append("};")
table = "\n".join(lines)

(UI / "public_notes.generated.js").write_text(table + "\n", encoding="utf-8")
shown = sum(1 for _, f in entries if f)
chars = sum(len(x) for _, f in entries for x in f)
print(f"{len(entries)} records, {shown} with a public excerpt, "
      f"{sum(len(f) for _, f in entries)} fragments, {chars} characters")
