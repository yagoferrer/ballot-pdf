---
name: ballot-pdf
description: Generate a printable, annotated PDF ballot for an election (San Diego / California) — every contest in the order of the voter's printed ballot, with party, +/− notes against the voter's rules, corruption findings, a ★ best pick per race and a Yes/No recommendation per measure. Use when the user asks to research a ballot, make/update "the ballot PDF", or prepare for an upcoming election.
---

# Ballot PDF

Produces `<election-folder>/<name>.html` + `.pdf` (Letter, page-numbered, clean page breaks) from one data file, `ballot-data.json`.

## Inputs to gather first
1. **The voter's rules** — read `voting-rules.md` at the project root (e.g. `~/git/mid2026/voting-rules.md`). Never invent rules; if the user adds one ("billionaire taxes are fine"), update that file and memory.
2. **The real ballot** — photos of the printed/sample ballot are the source of truth for which contests appear, their order, candidate order and ballot designations. Look in `~/Downloads` for recent `IMG_*.HEIC` (convert with `sips -s format jpeg -Z 1800 in.HEIC --out out.jpg`) or `~/Desktop/Screenshot*.png`. If none, use the Registrar's sample ballot and mark the PDF "verify against your official sample ballot". Ask for photos of any card side that's missing.
3. **Prior election folder** (e.g. `2026-06-02-primary/`) — earlier filter lists (`corrupt.md`, `pro-guns.md`, …) and the voter's previous picks (`people.md`) feed the notes and the `prior_pick` badge.

## Workflow
1. **Folder**: one per election, named by date and type (`YYYY-MM-DD-general`, `YYYY-MM-DD-primary`). Rename any `old/` folder to the election it holds.
2. **Research** (spawn parallel Sonnet agents, background; each writes a markdown file in the election folder with source URLs, marks gaps UNVERIFIED, never invents):
   - statewide + legislative + congressional finalists (`candidates.md`)
   - statewide propositions — yes/no meaning, fiscal impact, supporters/opponents, top funders (`propositions.md`)
   - local races and county/city/school measures (`local.md`)
   - judicial retention (Supreme Court + Court of Appeal) (`research-appellate-justices.md`)
   - **corruption check on every candidate and on measure funders** — verdict CLEAN / MINOR / SERIOUS, dated, labeled proven/alleged/dismissed (`corruption-*.md`)
3. **Write `ballot-data.json`** in the election folder (schema below). Contests go in exact printed-ballot order (Card A front → back → Card B …). Party label "D"/"R" for partisan races; for nonpartisan offices use the known affiliation ("DEM-endorsed", "REP-backed", "NPP (ex-REP)", "Unknown").
   - pros/cons are judged **only** against the voter's rules; say "(June filter)" / "(allowed by your rules)" where it helps.
   - `best` on exactly one candidate per contested race; `lean: true` when every option breaks a rule. Unopposed: still mark, note "you can leave it blank".
   - every measure gets `rec` {vote YES/NO, lean, why}. Judges: rule 1 (corruption) is the test.
4. **Build**: `bash ~/.claude/skills/ballot-pdf/scripts/make_pdf.sh <folder>/ballot-data.json <folder>/<name>` (needs Google Chrome, poppler `pdfinfo/pdftoppm/pdftotext`).
5. **Check every preview page** with Read (`$TMPDIR/ballot-preview/pg-N.png`): no contest split across pages, no orphan banners, no near-empty last page. Fix by trimming wording or reordering only within ballot order — never break ballot order to save space.
6. Also write/refresh a markdown report (`<name>.md`) with the same picks, recommendations and corruption table, then `open` the PDF.

## `ballot-data.json` schema
```json
{
 "meta": {"title": "...", "heading": "OFFICIAL BALLOT — ...", "subheading": "DATE · COUNTY · DISTRICTS",
          "page_label": "Nov 3, 2026 Ballot", "disclaimer": "Verify against your official sample ballot."},
 "rules": [{"title": "1. No corruption", "detail": "short reason"}],
 "rules_footer": "When every option breaks a rule, the pick is marked \"Lean\" (toss-up).",
 "items": [
  {"type": "card", "text": "CARD A · FRONT"},
  {"type": "banner", "text": "State"},
  {"type": "office", "title": "Governor", "vote_for": "Vote for One", "note": "optional",
   "candidates": [{"name": "...", "title": "ballot designation", "party": "D",
     "pros": ["..."], "cons": ["..."], "corruption": "CLEAN — nothing found.",
     "incumbent": true, "prior_pick": true, "best": {"lean": false, "why": "..."}}]},
  {"type": "note", "style": "rec-yes", "text": "★ Recommendation: YES on all justices — ..."},
  {"type": "retention", "title": "Associate Justice, Supreme Court",
   "justices": [{"name": "...", "bio": "appointed by …", "corruption": "CLEAN", "rec": "YES"}]},
  {"type": "measure", "title": "Proposition 1", "subtitle": "Short name", "summary": "what it does",
   "pros": [], "cons": [], "money": "who funds it", "rec": {"vote": "NO", "lean": false, "why": "..."}}
 ]
}
```
**Other languages**: set `meta.lang` (e.g. `"es"`) and `meta.labels` to override the built-in UI text — keys: `corruption, money, incumbent, prior_pick, lean, best, vote_for, yes, no, recommendation, rules_title, rules_footer, legend_pro, legend_con, legend_corr, legend_rec, page, of, question` (defaults in `scripts/build_ballot.py`). Write all content in that language too.

Full worked example: `assets/example-ballot-data.json` (San Diego, Nov 3 2026). Styling lives in `assets/ballot.css` (print rules: `@page` Letter with "Page X of Y" footer, `break-inside: avoid` on each contest, 2-column flow that reads down the left column then the right on each page).
