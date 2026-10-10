#!/usr/bin/env python3
"""Render an annotated ballot (HTML) from a JSON data file.

Usage: build_ballot.py ballot-data.json out.html

The JSON lists every contest in the SAME ORDER as the printed ballot.
See ../SKILL.md for the schema and ../assets/example-ballot-data.json for a full example.
"""
import html, json, os, sys

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "..", "assets", "ballot.css")).read()
PARTY = {"D": ("DEMOCRAT", "p-dem"), "R": ("REPUBLICAN", "p-rep")}
# UI text; override any key with meta.labels (e.g. for a Spanish report).
L = {"corruption": "Corruption", "money": "Money / corruption", "incumbent": "Incumbent", "prior_pick": "JUNE PICK",
     "lean": "Lean ", "best": "Best pick", "vote_for": "Vote for One", "yes": "YES", "no": "NO",
     "recommendation": "Recommendation", "rules_title": "Rules behind these picks",
     "rules_footer": "When every option breaks a rule, the pick is marked Lean (toss-up). Leaving a race blank is always an option.",
     "legend_pro": "+ Good for your priorities", "legend_con": "− Bad for your priorities",
     "legend_corr": "= CLEAN / MINOR / SERIOUS", "legend_rec": '● / ★ = recommended vote · "Lean" = toss-up',
     "page": "Page", "of": "of", "question": "Shall the Justice be elected to the office for the term provided by law?"}


def notes(pro, con, corr):
    out = [f'<div class="pro">+ {E(p)}</div>' for p in pro]
    out += [f'<div class="con">− {E(c)}</div>' for c in con]
    if corr:
        out.append(f'<div class="corr"><b>{L["corruption"]}:</b> {E(corr)}</div>')
    return f'<div class="notes">{"".join(out)}</div>'


def candidate(c):
    inc = f' <span class="incumbent">({L["incumbent"]})</span>' if c.get("incumbent") else ""
    pick = f'<span class="pick">{L["prior_pick"]}</span>' if c.get("prior_pick") else ""
    label, cls = PARTY.get(c.get("party", ""), (c.get("party", ""), "p-ind"))
    best = c.get("best")
    circle = '<div class="circle filled"></div>' if best else '<div class="circle"></div>'
    star = ""
    if best:
        lean = L["lean"] if best.get("lean") else ""
        star = f'<div class="rec rec-yes">★ {lean}{L["best"]} — {E(best["why"])}</div>'
    return (f'<div class="candidate">{circle}<div class="candidate-info">'
            f'<div class="candidate-name">{E(c["name"])}{inc}{pick}</div>'
            f'<div class="candidate-title">{E(c.get("title", ""))}</div>'
            f'{notes(c.get("pros", []), c.get("cons", []), c.get("corruption", ""))}{star}</div>'
            f'<div class="candidate-party {cls}">{E(label)}</div></div>')


def office(o):
    note = f'<div class="note">{E(o["note"])}</div>' if o.get("note") else ""
    vf = E(o.get("vote_for", L["vote_for"]))
    return (f'<div class="office"><div class="office-header">{E(o["title"])}</div>'
            f'<div class="vote-for">{vf}</div>{"".join(candidate(c) for c in o["candidates"])}{note}</div>')


def yes_no(vote):
    y = '<div class="circle filled"></div>' if vote == "YES" else '<div class="circle"></div>'
    n = '<div class="circle filled"></div>' if vote == "NO" else '<div class="circle"></div>'
    return f'<div class="yes-no"><div class="yn">{y} {L["yes"]}</div><div class="yn">{n} {L["no"]}</div></div>'


def retention(g):
    rows = []
    for j in g["justices"]:
        corr = f'<span class="jcorr">{L["corruption"]}: {E(j["corruption"])}</span>' if j.get("corruption") else ""
        rows.append(f'<div class="retention"><div class="name">{E(j["name"])}<span class="title">{E(j.get("bio", ""))}</span>{corr}</div>'
                    f'{yes_no(j.get("rec"))}</div>')
    q = E(g.get("question", L["question"]))
    return f'<div class="office"><div class="office-header">{E(g["title"])}</div><div class="vote-for">{q}</div>{"".join(rows)}</div>'


def measure(m):
    n = "".join(f'<div class="pro">+ {E(p)}</div>' for p in m.get("pros", []))
    n += "".join(f'<div class="con">− {E(c)}</div>' for c in m.get("cons", []))
    if m.get("money"):
        n += f'<div class="corr"><b>{L["money"]}:</b> {E(m["money"])}</div>'
    rec = m.get("rec") or {}
    r = ""
    if rec:
        lean = L["lean"] if rec.get("lean") else ""
        r = f'<div class="rec rec-{rec["vote"].lower()}">{L["recommendation"]}: {lean}{L[rec["vote"].lower()]} — {E(rec["why"])}</div>'
    sub = f'<br>{E(m["subtitle"])}' if m.get("subtitle") else ""
    vote = rec.get("vote")
    y = '<div class="circle filled"></div>' if vote == "YES" else '<div class="circle"></div>'
    no = '<div class="circle filled"></div>' if vote == "NO" else '<div class="circle"></div>'
    return (f'<div class="office"><div class="measure-header">{E(m["title"])}{sub}</div>'
            f'<div class="measure-body"><p>{E(m.get("summary", ""))}</p><div class="notes">{n}</div>{r}</div>'
            f'<div class="measure-vote"><div class="yn">{y} {L["yes"]}</div><div class="yn">{no} {L["no"]}</div></div></div>')


def item(i):
    t = i["type"]
    if t == "card":
        return f'<div class="card-banner">{E(i["text"])}</div>'
    if t == "banner":
        return f'<div class="section-banner">{E(i["text"])}</div>'
    if t == "note":
        cls = "rec rec-yes" if i.get("style") == "rec-yes" else "note"
        return f'<div class="office"><div class="{cls}" style="margin:4px 8px">{E(i["text"])}</div></div>'
    return {"office": office, "retention": retention, "measure": measure}[t](i)


def build(d):
    meta = d["meta"]
    L.update(meta.get("labels", {}))
    rules = "".join(f'<div><b>{E(r["title"])}</b> — {E(r["detail"])}</div>' for r in d.get("rules", []))
    rules_box = (f'<div class="rules"><div class="rules-title">{L["rules_title"]}</div><div class="rules-grid">{rules}</div>'
                 f'<div class="rules-foot">{E(d.get("rules_footer", L["rules_footer"]))}</div></div>') if rules else ""
    legend = (f'<div class="legend"><span class="pro">{E(L["legend_pro"])}</span><span class="con">{E(L["legend_con"])}</span>'
              f'<span class="corr"><b>{E(L["corruption"])}</b> {E(L["legend_corr"])}</span><span class="pick">{E(L["prior_pick"])}</span>'
              f'<span>{E(L["legend_rec"])}</span>'
              f'<span>{E(meta.get("disclaimer", "Verify against your official sample ballot."))}</span></div>')
    css = (CSS.replace("Nov 3, 2026 Ballot", meta.get("page_label", "Ballot"))
           .replace('· Page " counter(page) " of "', f'· {L["page"]} " counter(page) " {L["of"]} "'))
    body = "".join(item(i) for i in d["items"])
    return f'''<!DOCTYPE html>
<html lang="{E(meta.get("lang", "en"))}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(meta["title"])}</title>
<style>
{css}
</style>
</head>
<body>
<div class="ballot-wrapper">
  <div class="ballot-title">{E(meta.get("heading", "OFFICIAL BALLOT"))}</div>
  <div class="ballot-subtitle">{E(meta.get("subheading", ""))}</div>
  {rules_box}
  {legend}
  <div class="ballot-flow">
{body}
  </div>
</div>
</body>
</html>'''


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build_ballot.py ballot-data.json out.html")
    data = json.load(open(sys.argv[1]))
    open(sys.argv[2], "w").write(build(data))
    print(f"wrote {sys.argv[2]}")
