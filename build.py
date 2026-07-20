#!/usr/bin/env python3
"""magnuslodefalk.com — personal academic site. Single page, from data/site.yaml.
Shares the AI-Econ Lab design system (assets/styles.css). Edit YAML, run, push."""
from pathlib import Path
import shutil, yaml, html, hashlib

ROOT = Path(__file__).parent
S = yaml.safe_load((ROOT / "data" / "site.yaml").read_text(encoding="utf-8"))
OUT = ROOT / "docs"
BASE = S["base_url"].rstrip("/")
h = lambda s: html.escape(str(s), quote=True)

def photo_src():
    p = ROOT / "assets" / S["photo"]
    v = hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"
    return f"/assets/{S['photo']}?v={v}"

NAV = [("About", "#about"), ("Research", "#research"), ("Links", "#links"), ("Contact", "#contact")]

def build_html():
    b = S
    nav = "".join(f'<a href="{href}">{h(label)}</a>' for label, href in NAV)
    actions = "".join(
        f'<a class="btn {"primary" if a.get("primary") else "ghost"}" href="{a["href"]}">{h(a["label"])}</a>'
        for a in b["actions"])
    bio = "".join(f"<p>{h(p)}</p>" for p in b["bio"])
    interests = "".join(f"<li>{h(x)}</li>" for x in b["interests"])
    roles = "".join(
        f'<div class="rolecard"><a href="{r["href"]}"><b>{h(r["label"])}</b></a><span>{h(r["note"])}</span></div>'
        for r in b["roles"])
    profiles = "".join(f'<a class="lchip" href="{p["href"]}">{h(p["label"])}</a>' for p in b["profiles"])
    c = b["contact"]
    ld = {"@context": "https://schema.org", "@type": "Person", "name": b["name"], "jobTitle": b["title"],
          "url": BASE, "email": c["email"], "affiliation": {"@type": "CollegeOrUniversity", "name": "Örebro University"},
          "sameAs": [p["href"] for p in b["profiles"]]}
    import json
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(b['name'])} · {h(b['title'])}</title>
<meta name="description" content="{h(b['name'])}, {h(b['title'])} at Örebro University: AI and the labour market, firm growth, trade and migration.">
<link rel="canonical" href="{BASE}/">
<meta property="og:type" content="profile"><meta property="og:title" content="{h(b['name'])}">
<meta property="og:description" content="{h(b['title'])} · {h(b['affil'])}"><meta property="og:url" content="{BASE}/">
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="mast"><div class="wrap"><div class="mastbar">
  <a class="brand" href="/"><span class="plaque"><b>ML</b></span>
    <span class="brandtext"><b>{h(b['name'])}</b><small>{h(b['title'])}</small></span></a>
  <nav class="top">{nav}</nav>
  <button class="tbtn" id="themebtn" aria-label="Toggle colour theme">◐ Theme</button>
</div></div></div>

<main id="main"><div class="wrap">
  <div class="hero"><div class="herogrid">
    <div>
      <div class="eyebrow"><span class="dot"></span> {h(b['affil'])}</div>
      <h1 class="title">{h(b['name'])}</h1>
      <p class="lede">{h(b['lede'])}</p>
      <div class="cta-row">{actions}</div>
    </div>
    <div class="portrait"><img src="{photo_src()}" alt="{h(b['name'])}" width="360" height="360"></div>
  </div></div>
</div>

<div class="rule" id="about"><div class="wrap"><section>
  <p class="kicker">About</p><h2 class="sec">What I work on.</h2>
  <div class="prose" style="margin-top:14px">{bio}</div>
</section></div></div>

<div class="rule" id="research"><div class="wrap"><section>
  <p class="kicker">Research</p><h2 class="sec">Interests &amp; what I lead.</h2>
  <div class="two" style="grid-template-columns:1fr 1fr;margin-top:16px">
    <div><div class="grouphdr">Interests</div><ul class="reslist">{interests}</ul></div>
    <div><div class="grouphdr">Groups &amp; roles</div><div class="roles">{roles}</div></div>
  </div>
</section></div></div>

<div class="rule" id="links"><div class="wrap"><section>
  <p class="kicker">Publications &amp; profiles</p><h2 class="sec">Find my work.</h2>
  <p class="secintro">{h(b['publications_note'])}</p>
  <div class="chips" style="margin-top:16px">{profiles}</div>
</section></div></div>

<div class="rule" id="contact"><div class="wrap"><section>
  <p class="kicker">Contact</p><h2 class="sec">Get in touch.</h2>
  <div class="card" style="margin-top:16px;max-width:520px">
    <p style="margin:0 0 8px"><span class="lbl">E-mail</span> <a href="mailto:{c['email']}">{h(c['email'])}</a></p>
    <p style="margin:0 0 8px"><span class="lbl">Phone</span> {h(c['phone'])}</p>
    <p style="margin:0"><span class="lbl">Post</span> {h(c['address'])}</p>
  </div>
</section></div></div>

<footer><div class="wrap"><div class="footend">
  <span>© 2026 {h(b['name'])}</span>
  <span>Örebro University · Ratio · GLO · <a style="color:#fff" href="https://ai-econlab.com">AI-Econ Lab</a></span>
</div></div></footer>
</main>
<script src="/assets/app.js"></script>
</body></html>"""

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.html").write_text(build_html(), encoding="utf-8")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if S["build"].get("emit_cname") if "build" in S else False:
        (OUT / "CNAME").write_text(S["domain"] + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}/</loc></url></urlset>', encoding="utf-8")
    print("built magnuslodefalk.com (1 page) ->", OUT)

if __name__ == "__main__":
    build()
