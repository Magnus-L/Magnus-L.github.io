#!/usr/bin/env python3
"""magnuslodefalk.com — personal academic site (warm editorial identity).
Single page from data/site.yaml + data/econ_links.yaml. Edit YAML, run, push."""
from pathlib import Path
import shutil, yaml, html, hashlib, json

ROOT = Path(__file__).parent
S = yaml.safe_load((ROOT / "data" / "site.yaml").read_text(encoding="utf-8"))
LINKS = yaml.safe_load((ROOT / "data" / "econ_links.yaml").read_text(encoding="utf-8"))
OUT = ROOT / "docs"
BASE = S["base_url"].rstrip("/")
h = lambda s: html.escape(str(s), quote=True)

def photo_src():
    p = ROOT / "assets" / S["photo"]
    v = hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"
    return f"/assets/{S['photo']}?v={v}"

def page():
    b = S
    nav = "".join(f'<a href="{n["href"]}">{h(n["label"])}</a>' for n in b["nav"])
    actions = "".join(f'<a class="btn {"primary" if a.get("primary") else ""}" href="{a["href"]}">{h(a["label"])}</a>'
                      for a in b["actions"])
    bio = "".join(f"<p>{h(p)}</p>" for p in b["bio"])
    interests = "".join(f'<span class="tag">{h(x)}</span>' for x in b["interests"])
    roles = "".join(f'<div class="entry"><div class="t"><a href="{r["href"]}">{h(r["label"])}</a></div>'
                    f'<div class="m">{h(r["note"])}</div></div>' for r in b["roles"])
    active = "".join(f'<div class="entry"><div class="t">{h(w["title"])}</div>'
                     f'<div class="m">{h(w["authors"])} · {h(w["status"])}</div></div>' for w in b["ongoing"]["active"])
    inprog = "".join(f"<li>{h(x)}</li>" for x in b["ongoing"]["inprogress"])
    def wentry(w):
        t = f'<a href="{w["href"]}">{h(w["title"])}</a>' if w.get("href") else h(w["title"])
        return f'<div class="entry"><div class="t">{t}</div><div class="m"><span class="yr">{h(w["year"])}</span> · {h(w["outlet"])}</div></div>'
    writing = "".join(wentry(w) for w in b["writing"])
    media = "".join(f'<div class="entry"><div class="m"><span class="yr">{h(m["year"])}</span></div>'
                    f'<div class="t" style="font-size:15px;color:var(--ink-2)">{h(m["items"])}</div></div>'
                    for m in b["media_selected"])
    def course(c):
        code = f'<span style="color:var(--muted)"> {h(c["code"])}</span>' if c.get("code") else ""
        return f'<div class="entry"><div class="t">{h(c["name"])}{code}</div><div class="m">{h(c["note"])}</div></div>'
    masters = "".join(course(c) for c in b["teaching"]["masters"])
    undergrad = "".join(course(c) for c in b["teaching"]["undergrad"])
    grps = "".join(
        f'<details class="grp"><summary>{h(g["name"])}</summary><div class="linkgrid">'
        + "".join(f'<a href="{l["href"]}">{h(l["label"])}</a>' for l in g["links"]) + "</div></details>"
        for g in LINKS["groups"])
    ppara = "".join(f"<p>{h(p)}</p>" for p in b["personal"]["paras"])
    profiles = "".join(f'<a class="btn" href="{p["href"]}">{h(p["label"])}</a>' for p in b["profiles"])
    c = b["contact"]
    ld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": b["name"], "jobTitle": b["title"],
                     "url": BASE, "email": c["email"], "affiliation": {"@type": "CollegeOrUniversity", "name": "Örebro University"},
                     "sameAs": [p["href"] for p in b["profiles"]]}, ensure_ascii=False)
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(b['name'])} · {h(b['title'])}</title>
<meta name="description" content="{h(b['name'])}, {h(b['title'])} at Örebro University. Research on AI and the labour market, firm growth, trade and migration.">
<link rel="canonical" href="{BASE}/">
<meta property="og:type" content="profile"><meta property="og:title" content="{h(b['name'])}">
<meta property="og:description" content="{h(b['title'])} · {h(b['affil'])}"><meta property="og:url" content="{BASE}/">
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">{ld}</script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="mast"><div class="wrap"><div class="mastbar">
  <a class="who" href="/">{h(b['name'])}</a>
  <nav class="top">{nav}</nav>
  <button class="tbtn" id="themebtn" aria-label="Toggle colour theme">◐</button>
</div></div></div>

<main id="main"><div class="wrap">
  <div class="hero"><div class="herowrap">
    <div>
      <p class="eyebrow">{h(b['affil'])}</p>
      <h1>{h(b['name'])}</h1>
      <p class="role">{h(b['title'])}</p>
      <p class="lede">{h(b['lede'])}</p>
      <div class="actions">{actions}</div>
    </div>
    <div class="portrait"><img src="{photo_src()}" alt="{h(b['name'])}"></div>
  </div></div>

  <section id="about"><p class="kicker">About</p><h2>What I work on</h2>
    <div class="prose" style="margin-top:14px">{bio}</div></section>

  <section id="research"><p class="kicker">Research</p><h2>Interests &amp; current work</h2>
    <div class="tags">{interests}</div>
    <div style="margin-top:24px"><p class="lbl" style="color:var(--muted)">In review &amp; working papers</p>
      <div class="entries">{active}</div></div>
    <div style="margin-top:22px"><p class="lbl" style="color:var(--muted)">In progress</p>
      <ul class="plain">{inprog}</ul></div>
    <p class="intro" style="margin-top:20px">{h(b['publications_note'])}
      <a href="https://ai-econlab.com/research/">Papers →</a></p></section>

  <section id="writing"><p class="kicker">Writing &amp; media</p><h2>Dissemination</h2>
    <p class="intro">Op-eds, columns and popular writing, and selected media. The full record is in my
      <a href="{b['actions'][0]['href']}">CV</a>.</p>
    <div class="entries" style="margin-top:20px">{writing}</div>
    <p class="lbl" style="color:var(--muted);margin-top:26px">Selected media</p>
    <div class="entries">{media}</div></section>

  <section id="teaching"><p class="kicker">Teaching</p><h2>Courses &amp; supervision</h2>
    <div class="cols"><div><p class="lbl" style="color:var(--muted)">Master's</p><div class="entries">{masters}</div></div>
      <div><p class="lbl" style="color:var(--muted)">Undergraduate</p><div class="entries">{undergrad}</div></div></div>
    <p class="intro" style="margin-top:18px">{h(b['teaching']['note'])}</p></section>

  <section id="resources"><p class="kicker">Resources</p><h2>Economics links</h2>
    <p class="intro">A working list of data, papers, tools and reading I keep coming back to.</p>
    <div style="margin-top:14px">{grps}</div></section>

  <section id="personal"><p class="kicker">Personal</p><h2>Away from economics</h2>
    <div class="prose" style="margin-top:14px">{ppara}</div>
    <div class="facts">{"".join(f'<p><span class="lbl" style="color:var(--muted)">{h(f["lbl"])}</span> {h(f["val"])}</p>' for f in b["personal"]["facts"])}</div></section>

  <section id="contact"><p class="kicker">Elsewhere &amp; contact</p><h2>Find me</h2>
    <div class="actions" style="margin-top:16px">{profiles}</div>
    <div class="facts" style="margin-top:22px">
      <p><span class="lbl" style="color:var(--muted)">E-mail</span> <a href="mailto:{c['email']}">{h(c['email'])}</a></p>
      <p><span class="lbl" style="color:var(--muted)">Phone</span> {h(c['phone'])}</p>
      <p><span class="lbl" style="color:var(--muted)">Post</span> {h(c['address'])}</p></div></section>
</div></main>

<footer><div class="wrap"><div class="foot">
  <span>© 2026 {h(b['name'])}</span>
  <span>Örebro University · Ratio · GLO · <a href="https://ai-econlab.com">AI-Econ Lab</a></span>
</div></div></footer>
<script src="/assets/app.js"></script>
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
    print("built magnuslodefalk.com (warm editorial) ->", OUT)

if __name__ == "__main__":
    build()
