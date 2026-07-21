#!/usr/bin/env python3
"""magnuslodefalk.com — clean, papers-forward academic site (benchmarked on
leading economists' pages). Single page from data/*.yaml. Edit YAML, run, push."""
from pathlib import Path
import shutil, yaml, html, hashlib, json

ROOT = Path(__file__).parent
def load(n): return yaml.safe_load((ROOT / "data" / n).read_text(encoding="utf-8"))
S, LINKS, PAPERS = load("site.yaml"), load("econ_links.yaml"), load("papers.yaml")
OUT = ROOT / "docs"; BASE = S["base_url"].rstrip("/")
h = lambda s: html.escape(str(s), quote=True)

def asset(rel):
    p = ROOT / rel; v = hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"
    return f"/{rel}?v={v}"

MINE = lambda p: "Lodefalk" in p["authors"]

def paper_entry(p, compact=False):
    links = p.get("links", []) or []
    primary = links[0]["url"] if links else ""
    title = h(p["title"])
    if primary: title = f'<a href="{primary}">{title}</a>'
    if compact:
        return f'<li>{title} <span style="color:var(--muted)">— {h(p["authors"])}</span></li>'
    ab = f'<details><summary>Abstract</summary><p class="ab">{h(p["abstract"])}</p></details>' if p.get("abstract") else ""
    chips = "".join(f'<a href="{l["url"]}">{h(l["label"])}</a>' for l in links)
    cov = ""
    for c in p.get("coverage", []) or []:
        nm = c["name"] if isinstance(c, dict) else c
        if isinstance(c, dict) and c.get("url"): cov += f'<a class="media" href="{c["url"]}">{h(nm)}</a>'
    linkrow = f'<div class="links">{chips}{cov}</div>' if (chips or cov) else ""
    return (f'<div class="pub"><div class="t">{title}</div>'
            f'<div class="au">{h(p["authors"])}</div>'
            f'<div class="vn"><span class="yr">{h(p["year"])}</span> · {h(p["venue"])}</div>'
            f'{ab}{linkrow}</div>')

def research():
    pub = [p for p in PAPERS["published"] if MINE(p)]
    wp_all = [p for p in PAPERS["working"] if MINE(p)]
    wp = [p for p in wp_all if (p.get("links") or p.get("abstract"))]
    wip = [p for p in wp_all if not (p.get("links") or p.get("abstract"))]
    out = '<div class="subhd">Published &amp; accepted</div>' + "".join(paper_entry(p) for p in pub)
    out += '<div class="subhd">Working papers</div>' + "".join(paper_entry(p) for p in wp)
    if wip:
        out += '<div class="subhd">Work in progress</div><ul class="compact">' + "".join(paper_entry(p, True) for p in wip) + "</ul>"
    return out

def page():
    b = S
    nav = "".join(f'<a href="{n}">{t}</a>' for t, n in
                  [("Research", "#research"), ("Writing", "#writing"), ("Teaching", "#teaching"),
                   ("Resources", "#resources"), ("About", "#about")])
    quick = "".join(f'<a class="{"pri" if a.get("primary") else ""}" href="{a["href"]}">{h(a["label"])}</a>' for a in b["actions"])
    interests = "".join(f'<span class="chip">{h(x)}</span>' for x in b["interests"])
    roles = "".join(f'<div class="row"><span class="y"></span><span class="x"><a href="{r["href"]}"><b>{h(r["label"])}</b></a> — {h(r["note"])}</span></div>' for r in b["roles"])
    bio = "".join(f"<p>{h(p)}</p>" for p in b["bio"])
    inprog = "".join(f"<li>{h(x)}</li>" for x in b["ongoing"]["inprogress"])
    def wr(w):
        t = f'<a href="{w["href"]}">{h(w["title"])}</a>' if w.get("href") else h(w["title"])
        return f'<div class="row"><span class="y">{h(w["year"])}</span><span class="x">{t}. <span style="color:var(--muted)">{h(w["outlet"])}</span></span></div>'
    writing = "".join(wr(w) for w in b["writing"])
    media = "".join(f'<div class="row"><span class="y">{h(m["year"])}</span><span class="x">{h(m["items"])}</span></div>' for m in b["media_selected"])
    def course(c):
        code = f' <span style="color:var(--muted)">{h(c["code"])}</span>' if c.get("code") else ""
        return f'<div class="row"><span class="y"></span><span class="x"><b>{h(c["name"])}</b>{code} — {h(c["note"])}</span></div>'
    masters = "".join(course(c) for c in b["teaching"]["masters"])
    undergrad = "".join(course(c) for c in b["teaching"]["undergrad"])
    grps = "".join(f'<details class="grp"><summary>{h(g["name"])}</summary><div class="linkgrid">'
                   + "".join(f'<a href="{l["href"]}">{h(l["label"])}</a>' for l in g["links"]) + "</div></details>"
                   for g in LINKS["groups"])
    profiles = "".join(f'<a href="{p["href"]}">{h(p["label"])}</a>' for p in b["profiles"])
    ppara = "".join(f"<p>{h(p)}</p>" for p in b["personal"]["paras"])
    c = b["contact"]
    ld = json.dumps({"@context":"https://schema.org","@type":"Person","name":b["name"],"jobTitle":b["title"],
        "url":BASE,"email":c["email"],"affiliation":{"@type":"CollegeOrUniversity","name":"Örebro University"},
        "sameAs":[p["href"] for p in b["profiles"]]}, ensure_ascii=False)
    v = hashlib.md5((ROOT/"assets"/b["photo"]).read_bytes()).hexdigest()[:8]
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(b['name'])} · {h(b['title'])}</title>
<meta name="description" content="{h(b['name'])}, {h(b['title'])} at Örebro University. Research on AI and the labour market, firm growth, trade and migration.">
<link rel="canonical" href="{BASE}/">
<meta property="og:type" content="profile"><meta property="og:title" content="{h(b['name'])}">
<meta property="og:description" content="{h(b['title'])} · {h(b['affil'])}"><meta property="og:url" content="{BASE}/">
<link rel="stylesheet" href="{asset('assets/styles.css')}">
<script type="application/ld+json">{ld}</script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="top"><div class="wrap"><div class="topbar">
  <a class="home" href="/">{h(b['name'])}</a>
  <nav class="topnav">{nav}</nav>
  <button class="tbtn" id="themebtn" aria-label="Toggle colour theme">◐</button>
</div></div></div>

<main id="main"><div class="wrap">
  <header class="hd"><div class="hdgrid">
    <div>
      <h1>{h(b['name'])}</h1>
      <p class="pos"><b>{h(b['title'])}</b><br>{h(b['affil'])}</p>
      <div class="quick">{quick}</div>
    </div>
    <img class="avatar" src="/assets/{b['photo']}?v={v}" alt="{h(b['name'])}">
  </div>
  <p class="lead" style="margin-top:24px;font-size:17px">{h(b['lede'])}</p></header>

  <section id="research"><p class="eyebrow">Research</p><h2>Papers</h2>
    {research()}
    <p class="note">The complete list, including earlier work on trade, migration and the servicification of
      firms, is in my <a href="{b['actions'][0]['href']}">CV</a> and on
      <a href="https://scholar.google.se/citations?user=z0WQ2JcAAAAJ">Google Scholar</a>.</p></section>

  <section id="writing"><p class="eyebrow">Writing &amp; media</p><h2>Dissemination</h2>
    <div class="rows">{writing}</div>
    <div class="subhd">Selected media</div><div class="rows">{media}</div></section>

  <section id="teaching"><p class="eyebrow">Teaching</p><h2>Courses &amp; supervision</h2>
    <div class="subhd">Master's</div><div class="rows">{masters}</div>
    <div class="subhd">Undergraduate</div><div class="rows">{undergrad}</div>
    <p class="note">{h(b['teaching']['note'])}</p></section>

  <section id="resources"><p class="eyebrow">Resources</p><h2>Economics links</h2>
    <p class="lead">Data, papers, tools and reading I keep coming back to.</p>
    <div style="margin-top:14px">{grps}</div></section>

  <section id="about"><p class="eyebrow">About</p><h2>Background</h2>
    <div class="prose" style="margin-top:12px">{bio}</div>
    <div class="chips">{interests}</div>
    <div class="subhd">Roles</div><div class="rows">{roles}</div>
    <div class="subhd">Currently in progress</div><ul class="compact">{inprog}</ul>
    <div class="subhd">Personal</div><div class="prose">{ppara}</div></section>

  <section id="contact"><p class="eyebrow">Elsewhere &amp; contact</p><h2>Find me</h2>
    <div class="linkwrap">{profiles}</div>
    <div class="facts" style="margin-top:20px">
      <p><span class="k">E-mail</span><a href="mailto:{c['email']}">{h(c['email'])}</a></p>
      <p><span class="k">Phone</span>{h(c['phone'])}</p>
      <p><span class="k">Post</span>{h(c['address'])}</p></div></section>
</div></main>

<footer><div class="wrap"><div class="foot">
  <span>© 2026 {h(b['name'])}</span>
  <span>Örebro University · Ratio · GLO · <a href="https://ai-econlab.com">AI-Econ Lab</a></span>
</div></div></footer>
<script src="{asset('assets/app.js')}"></script>
</body></html>"""

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.html").write_text(page(), encoding="utf-8")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if S.get("build", {}).get("emit_cname"): (OUT / "CNAME").write_text(S["domain"] + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{BASE}/</loc></url></urlset>', encoding="utf-8")
    print(f"built magnuslodefalk.com (papers-forward) · {sum(1 for p in PAPERS['published']+PAPERS['working'] if MINE(p))} papers")

if __name__ == "__main__":
    build()
