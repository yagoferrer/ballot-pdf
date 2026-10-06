# ballot-pdf — Claude Code skill

A [Claude Code](https://claude.com/claude-code) skill that researches an election and generates a **printable, annotated PDF ballot**:

- every contest in the same order as your printed ballot (Card A front/back, Card B…)
- party label for each candidate
- **+ / −** notes judged against *your* voting rules (shown in a box at the top of the ballot)
- a corruption check for every candidate (CLEAN / MINOR / SERIOUS) and for measure funders
- a ★ best pick per race and a Yes/No recommendation per measure
- Letter size, page numbers ("Page X of Y"), and no contest split across pages

## Install

```bash
git clone https://github.com/yagoferrer/ballot-pdf ~/.claude/skills/ballot-pdf
```

Requirements: macOS with Google Chrome (headless printing) and poppler (`brew install poppler`) for `pdfinfo`, `pdftoppm` and `pdftotext`.

## Use

In Claude Code, ask for something like *"research my November ballot and make the ballot PDF"*. Give it photos of your printed or sample ballot so it gets the exact contests and their order, plus a `voting-rules.md` with your priorities.

To rebuild from an existing data file:

```bash
bash ~/.claude/skills/ballot-pdf/scripts/make_pdf.sh path/to/ballot-data.json path/to/output-name
```

## Files

| Path | What it is |
|---|---|
| `SKILL.md` | Instructions Claude follows: research, data file, build, page checks |
| `scripts/build_ballot.py` | Renders `ballot-data.json` to HTML |
| `scripts/make_pdf.sh` | HTML → PDF with Chrome, then page previews to check the layout |
| `assets/ballot.css` | Ballot look and print rules |
| `assets/example-ballot-data.json` | Worked example: San Diego County, November 3, 2026 general election |

The example's picks and recommendations reflect one voter's personal rules. They are an example of the format, not an endorsement. Research comes from web search summaries, so check it against your official sample ballot and voter guide.
