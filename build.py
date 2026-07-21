#!/usr/bin/env python3
"""magnuslodefalk.com — clean, papers-forward academic site (benchmarked on
leading economists' pages). One page rendered from data/*.yaml. Edit YAML, run, push.

Data files:
  site.yaml          identity, bio, roles, press kit, profiles, contact
  papers.yaml        AI research (the lab library; filtered to Lodefalk here)
  other_research.yaml trade / migration / services / firm-growth (collapsible)
  dissemination.yaml popular writing + media archive (every link)
  teaching.yaml      current courses, PhD students, MSc thesis advice
  econ_links.yaml    curated resources (with Magnus's annotations)
  metrics.yaml       Google Scholar snapshot (refresh via scripts/refresh_metrics.py)
"""
from pathlib import Path
import shutil, yaml, html, hashlib, json, re

ROOT = Path(__file__).parent
def load(n): return yaml.safe_load((ROOT / "data" / n).read_text(encoding="utf-8"))
S       = load("site.yaml")
LINKS   = load("econ_links.yaml")
PAPERS  = load("papers.yaml")
OTHER   = load("other_research.yaml")
DISS    = load("dissemination.yaml")
TEACH   = load("teaching.yaml")
METRICS = load("metrics.yaml")
OUT = ROOT / "docs"; BASE = S["base_url"].rstrip("/")
h = lambda s: html.escape(str(s), quote=True)

def asset(rel):
    p = ROOT / rel; v = hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"
    return f"/{rel}?v={v}"

def cb(rel):
    """cache-busting query for a file under assets/, given a path relative to repo root."""
    p = ROOT / rel; return hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"

MINE = lambda p: "Lodefalk" in p["authors"]

_LINK = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')
def linkify(s):
    """Escape prose but turn [text](url) into a link. Used for bio paragraphs."""
    out, i = [], 0
    for m in _LINK.finditer(s):
        out.append(h(s[i:m.start()]))
        out.append(f'<a href="{h(m.group(2))}">{h(m.group(1))}</a>')
        i = m.end()
    out.append(h(s[i:]))
    return "".join(out)

# ---------- papers ----------
def paper_entry(p, compact=False):
    links = p.get("links", []) or []
    primary = links[0]["url"] if links else ""
    title = h(p["title"])
    if primary: title = f'<a href="{primary}">{title}</a>'
    if compact:
        au = f' <span class="mut">— {h(p["authors"])}</span>' if p.get("authors") else ""
        return f'<li>{title}{au}</li>'
    ab = (f'<details><summary>Abstract</summary><p class="ab">{h(p["abstract"])}</p></details>'
          if p.get("abstract") else "")
    chips = "".join(f'<a href="{l["url"]}">{h(l["label"])}</a>' for l in links)
    cov = ""
    for c in p.get("coverage", []) or []:
        nm = c["name"] if isinstance(c, dict) else c
        if isinstance(c, dict) and c.get("url"):
            cov += f'<a class="media" href="{c["url"]}">{h(nm)}</a>'
        else:
            cov += f'<span class="media">{h(nm)}</span>'
    linkrow = f'<div class="links">{chips}{cov}</div>' if (chips or cov) else ""
    return (f'<div class="pub"><div class="t">{title}</div>'
            f'<div class="au">{h(p["authors"])}</div>'
            f'<div class="vn"><span class="yr">{h(p["year"])}</span> · {h(p["venue"])}</div>'
            f'{ab}{linkrow}</div>')

def research_ai():
    pub = [p for p in PAPERS["published"] if MINE(p)]
    wp_all = [p for p in PAPERS["working"] if MINE(p)]
    wp  = [p for p in wp_all if (p.get("links") or p.get("abstract"))]
    wip = [p for p in wp_all if not (p.get("links") or p.get("abstract"))]
    out  = '<div class="subhd">Published &amp; accepted</div>' + "".join(paper_entry(p) for p in pub)
    out += '<div class="subhd">Working papers</div>' + "".join(paper_entry(p) for p in wp)
    if wip:
        out += ('<div class="subhd">Work in progress</div><ul class="compact">'
                + "".join(paper_entry(p, True) for p in wip) + "</ul>")
    return out

def research_other():
    pub = OTHER["published"]
    feat = [p for p in pub if p.get("featured")]
    rest = [p for p in pub if not p.get("featured")]
    wip = OTHER.get("wip", [])
    out = ""
    if feat:
        out += '<div class="subhd">Selected</div>' + "".join(paper_entry(p) for p in feat)
    body = "".join(paper_entry(p) for p in rest)
    if wip:
        body += ('<div class="subhd">Work in progress</div><ul class="compact">'
                 + "".join(f'<li>{h(w["title"])} <span class="mut">— {h(w["authors"])}</span></li>' for w in wip)
                 + "</ul>")
    out += (f'<details class="more"><summary>Show {len(rest)} further papers on trade, migration, '
            f'services and firm growth</summary><div class="more-body">{body}</div></details>')
    return out

# ---------- writing & media ----------
def diss_row(d):
    t = f'<a href="{d["href"]}">{h(d["title"])}</a>' if d.get("href") else h(d["title"])
    return (f'<div class="row"><span class="y">{h(d["year"])}</span>'
            f'<span class="x">{t}. <span class="mut">{h(d["outlet"])}</span></span></div>')

def media_row(m):
    label = f'{h(m["outlet"])} — {h(m["desc"])}' if m.get("desc") else h(m["outlet"])
    x = f'<a href="{m["href"]}">{label}</a>' if m.get("href") else label
    return f'<div class="row"><span class="y">{h(m["year"])}</span><span class="x">{x}</span></div>'

def _diss_block(items, render, subhd, n=10):
    """Show the n most recent, put the rest behind a toggle (items are newest-first)."""
    head = "".join(render(x) for x in items[:n])
    rest = items[n:]
    out = f'<div class="subhd">{subhd}</div><div class="rows">{head}</div>'
    if rest:
        out += (f'<details class="more"><summary>Show {len(rest)} more</summary>'
                f'<div class="rows more-body">' + "".join(render(x) for x in rest) + "</div></details>")
    return out

def writing_media():
    return (_diss_block(DISS["writing"], diss_row, "Popular writing &amp; policy")
            + _diss_block(DISS["media"], media_row, "Selected media"))

# ---------- teaching ----------
def course(c):
    code = f' <span class="mut">{h(c["code"])}</span>' if c.get("code") else ""
    name = f'<a href="{c["href"]}"><b>{h(c["name"])}</b></a>' if c.get("href") else f'<b>{h(c["name"])}</b>'
    return f'<div class="row"><span class="y"></span><span class="x">{name}{code} — {h(c["note"])}</span></div>'

def phd_row(p):
    nm = f'<a href="{p["href"]}"><b>{h(p["name"])}</b></a>' if p.get("href") else f'<b>{h(p["name"])}</b>'
    note = f' — {h(p["note"])}' if p.get("note") else ""
    return f'<div class="row"><span class="y">{h(p["period"])}</span><span class="x">{nm}{note}</span></div>'

def teaching():
    out  = '<div class="subhd">Master\'s</div><div class="rows">' + "".join(course(c) for c in TEACH["masters"]) + "</div>"
    out += '<div class="subhd">Undergraduate</div><div class="rows">' + "".join(course(c) for c in TEACH["undergrad"]) + "</div>"
    if TEACH.get("msc_advice"):
        out += f'<p class="note"><b>Choosing a thesis topic.</b> {h(TEACH["msc_advice"])}</p>'
    phd = TEACH.get("phd", [])
    if phd:
        out += (f'<details class="more"><summary>Doctoral students supervised ({len(phd)})</summary>'
                f'<div class="rows more-body">' + "".join(phd_row(p) for p in phd) + "</div></details>")
    return out

# ---------- resources ----------
def resource_groups():
    def link(l):
        note = f' <span class="gloss">{h(l["note"])}</span>' if l.get("note") else ""
        return f'<a href="{l["href"]}">{h(l["label"])}</a>{note}'
    return "".join(
        f'<details class="grp"><summary>{h(g["name"])}</summary><div class="linkgrid">'
        + "".join(f'<div class="lk">{link(l)}</div>' for l in g["links"]) + "</div></details>"
        for g in LINKS["groups"])

# ---------- metrics + press ----------
def metrics_strip():
    n_pub = len([p for p in PAPERS["published"] if MINE(p)]) + len(OTHER["published"])
    m = METRICS
    tiles = [
        (n_pub, "peer-reviewed articles"),
        (m["citations"], "citations"),
        (m["h_index"], "h-index"),
        (m["i10_index"], "i10-index"),
    ]
    cells = "".join(f'<div class="stat"><span class="n">{h(v)}</span><span class="l">{h(l)}</span></div>'
                    for v, l in tiles)
    asof = h(fmt_date(m["as_of"]))
    return (f'<div class="metrics">{cells}</div>'
            f'<p class="metrics-cap"><a href="{m["scholar_url"]}">Google Scholar</a>, as of {asof}</p>')

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def fmt_date(iso):
    try:
        y, mo, d = iso.split("-"); return f"{int(d)} {MONTHS[int(mo)]} {y}"
    except Exception:
        return iso

def press_kit():
    pr = S.get("press")
    if not pr: return ""
    shots = ""
    for ph in pr["photos"]:
        rel = f'assets/press/magnus-lodefalk-{ph["slug"]}.jpg'
        thumb = f'/assets/press/thumb/{ph["slug"]}.jpg?v={cb("assets/press/thumb/" + ph["slug"] + ".jpg")}'
        full  = f'/{rel}?v={cb(rel)}'
        shots += (f'<a class="shot {"v" if ph.get("w")=="2:3" else ""}" href="{full}" '
                  f'download title="Download — {h(pr["credit"])}">'
                  f'<img src="{thumb}" alt="Magnus Lodefalk — {h(ph["label"].lower())}" loading="lazy">'
                  f'<span class="cap">{h(ph["label"])}</span></a>')
    bio = f'<p class="pressbio" style="margin-top:0">{h(pr["bio"])}</p>' if pr.get("bio") else ""
    return (f'<details class="more"><summary>Press kit: short bio and photos</summary>'
            f'<div class="more-body">{bio}'
            f'<p class="note">Click any photo to download a high-resolution version. {h(pr["credit"])}</p>'
            f'<div class="press">{shots}</div></div></details>')

# ---------- page ----------
def page():
    b = S
    nav = "".join(f'<a href="{n}">{t}</a>' for t, n in
                  [("Research", "#research"), ("Writing", "#writing"), ("Teaching", "#teaching"),
                   ("Resources", "#resources"), ("About", "#about")])
    quick = "".join(f'<a class="{"pri" if a.get("primary") else ""}" href="{a["href"]}">{h(a["label"])}</a>'
                    for a in b["actions"])
    # obfuscated e-mail action (assembled by app.js)
    eu, ed = b["contact"]["email"].split("@")
    email_obf = f'{eu} (at) {ed.replace(".", " (dot) ")}'
    quick += f'<a class="email" data-u="{h(eu)}" data-d="{h(ed)}" data-reveal="keep" href="#contact">Email</a>'

    affil = " · ".join(f'<a href="{a["href"]}">{h(a["name"])}</a>' for a in b["affil"])
    interests = "".join(f'<span class="chip">{h(x)}</span>' for x in b["interests"])
    roles = "".join(
        f'<div class="row"><span class="y"></span><span class="x">'
        f'<a href="{r["href"]}"><b>{h(r["label"])}</b></a> — {h(r["note"])}</span></div>' for r in b["roles"])
    bio = "".join(f"<p>{linkify(p)}</p>" for p in b["bio"])
    full_bio = ""
    if b.get("full_bio"):
        fb = "".join(f"<p>{h(p)}</p>" for p in b["full_bio"])
        full_bio = (f'<details class="more"><summary>Full biography</summary>'
                    f'<div class="prose more-body" style="margin-top:8px">{fb}</div></details>')
    ppara = "".join(f"<p>{h(p)}</p>" for p in b["personal"]["paras"])
    profiles = "".join(f'<a href="{p["href"]}">{h(p["label"])}</a>' for p in b["profiles"])
    c = b["contact"]
    ld = json.dumps({"@context":"https://schema.org","@type":"Person","name":b["name"],"jobTitle":b["title"],
        "url":BASE,"affiliation":{"@type":"CollegeOrUniversity","name":"Örebro University"},
        "sameAs":[p["href"] for p in b["profiles"]]}, ensure_ascii=False)
    pv = cb("assets/" + b["photo"])
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(b['name'])} · {h(b['title'])}</title>
<meta name="description" content="{h(b['name'])}, {h(b['title'])} at Örebro University. Research on AI and the labour market, firm growth, trade and migration.">
<link rel="canonical" href="{BASE}/">
<meta property="og:type" content="profile"><meta property="og:title" content="{h(b['name'])}">
<meta property="og:description" content="{h(b['title'])} · Örebro University, Ratio, GLO"><meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/assets/{b['photo']}?v={pv}">
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
      <p class="pos"><b>{h(b['title'])}</b><br>{affil}</p>
      <div class="quick">{quick}</div>
    </div>
    <figure class="avatarfig">
      <img class="avatar" src="/assets/{b['photo']}?v={pv}" alt="{h(b['name'])}">
      <figcaption>Photo: {h(b['photo_credit'])}</figcaption>
    </figure>
  </div>
  <p class="lead" style="margin-top:22px;font-size:17px">{h(b['lede'])}</p>
  </header>

  <section id="research"><p class="eyebrow">Research</p><h2>Research on AI</h2>
    {research_ai()}
    <div class="subhd" style="margin-top:30px">Other research</div>
    <p class="note" style="margin-top:2px">Earlier and continuing work on trade, migration, the
      servicification of firms, and firm growth.</p>
    {research_other()}</section>

  <section id="writing"><p class="eyebrow">Dissemination</p><h2>Writing &amp; media</h2>
    {writing_media()}</section>

  <section id="teaching"><p class="eyebrow">Teaching</p><h2>Courses &amp; supervision</h2>
    {teaching()}</section>

  <section id="resources"><p class="eyebrow">Resources</p><h2>Economics links</h2>
    <p class="lead">Data, papers, tools and reading I keep coming back to.</p>
    <div style="margin-top:14px">{resource_groups()}</div></section>

  <section id="about"><p class="eyebrow">About</p><h2>Background</h2>
    <div class="prose" style="margin-top:12px">{bio}</div>
    {full_bio}
    <div class="chips">{interests}</div>
    <div class="subhd">Publications at a glance</div>{metrics_strip()}
    <div class="subhd">Roles</div><div class="rows">{roles}</div>
    <div class="subhd">Personal</div><div class="prose">{ppara}</div>
    {press_kit()}</section>

  <section id="contact"><p class="eyebrow">Elsewhere &amp; contact</p><h2>Find me</h2>
    <div class="linkwrap">{profiles}</div>
    <div class="facts" style="margin-top:20px">
      <p><span class="k">E-mail</span><a class="email" data-u="{h(eu)}" data-d="{h(ed)}" data-reveal="keep" href="#contact">{h(email_obf)}</a></p>
      <p><span class="k">Phone</span>{h(c['phone'])}</p>
      <p><span class="k">Post</span>{h(c['address'])}</p></div></section>
</div></main>

<footer><div class="wrap"><div class="foot">
  <span>© 2026 {h(b['name'])}</span>
  <span>{affil} · <a href="{b['lab_url']}">AI-Econ Lab</a></span>
</div></div></footer>
<script src="{asset('assets/app.js')}"></script>
</body></html>"""

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.html").write_text(page(), encoding="utf-8")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if S.get("build", {}).get("emit_cname"):
        (OUT / "CNAME").write_text(S["domain"] + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}/</loc></url></urlset>', encoding="utf-8")
    n = len([p for p in PAPERS["published"] if MINE(p)]) + len(OTHER["published"])
    print(f"built magnuslodefalk.com · {n} peer-reviewed articles · "
          f"{len(DISS['writing'])} writing + {len(DISS['media'])} media items")

if __name__ == "__main__":
    build()
