# Site feedback, thread 1: handoff (2026-10-20)

## Live

https://mundus-ulterior.pages.dev/ serves commit `b2f019e` byte for byte, except for the 214-byte Cloudflare Pages Analytics script that Cloudflare injects. `data.js` is unchanged throughout (`4acef54c7b58…`). The repo was clean at `b2f019e` when this thread closed. Harness: 64 ok.

## Commits this thread

| Commit | What |
|---|---|
| `bc8f206` | The masthead became an inline SVG landscape ("Horizon") in `--hz-` tokens. The script band and the map thumbnail were removed, and the stats line moved under the tabs. Guard 2c's two specimen checks were retired, and three masthead guards were added (loads nothing, no color in the drawing, dark mode redraws it), each seen to fail first. |
| `048a697` | Site fixes 2–6 from `claude/site-fixes-draft.md`: no claim of exactness, plus a disclosure line in §8 (derived, 635 of 1,227 highlights short); one language count (18); "source records"; the Questions heading; Oxford commas. |
| `ed3a7c3` | Two standards on the ridges (canvas variant E1): a spread-wing Roman eagle far off and a Han banner near. Two new tokens. Hidden below 860px. The §7 masthead line was updated to match. |
| `b2f019e` | Larger wordmark (new `--t-mast` token) and subtitle (`--t-l`). The subtitle now reads "Rome and wider world: 27 BC – 1204 AD", with the date range held on one line. |

## Rob's decisions this thread

- Horizon chosen, shipped as vector rather than generated art. Map thumbnail dropped, stats line kept.
- Fixes 2–6 applied. **Fix 7 and the proposed extra guards were NOT applied.**
- E1 chosen, with the eagle's wings spread horizontally. The standards are **an artistic interpretation only: no research or sourcing for them.**
- Wordmark stays left-aligned. Dates are written "27 BC – 1204 AD", as elsewhere on the site.
- Work one change at a time: commit, deploy, check, then the next.

## Open, not done

- **Portal Text Google Doc** still needs the Methodology changes mirrored: §6 (the citation outcome line), §7 (the masthead bullet, now naming the standards; the "masthead images" wording removed), §8 (the new highlights-short line), §10 ("masthead images" removed), and the Oxford commas. `METHODOLOGY_COPY_FINAL.md` already has all of them.
- **Cloudflare Web Analytics** is switched on, which adds a beacon script. Rob hasn't yet confirmed whether that was intended.
- The old banner PNGs still answer at `/banner/*.png`, though nothing links to them.
- Cleanup candidates, left in place: `ui/build_banner.mjs`, `ui/banner/`, the header comment in `ui/measure_data.mjs`, and the several deploy folders under `Claude outputs/`.
- `claude/site-fixes-draft.md` is superseded (everything applied except fix 7).
- Optional: §10 now reads "no content delivery network, and no server, and the page itself is not compiled", which could be split into two sentences.

## Starting point for the next thread

Revising site text. Deploy routine: copy `ui/index.html` and `ui/data.js` into a fresh folder under `Claude outputs/`, deploy it to **Production** in Cloudflare Pages, then check the live `index.html` digest (with the analytics block removed) against the commit.
