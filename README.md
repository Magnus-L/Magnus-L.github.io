# Magnus-L.github.io — magnuslodefalk.com

Personal academic site. Single page, data-driven (edit `data/site.yaml`, run `python3 build.py`, push).
Shares the AI-Econ Lab design system (`assets/styles.css`). GitHub Pages serves `main` `/docs`.
Photo in `assets/magnus.jpg`. DNS cutover mirrors the lab site (Crossnet: apex A -> GitHub IPs, www CNAME -> magnus-l.github.io); do it only when ready.

## How this site publishes

`data/*.yaml` -> `build.py` -> `docs/` -> GitHub Pages, and **the runner does all of it**.
`.github/workflows/deploy.yml` builds and deploys on every push to `main`. So editing the YAML
and pushing is the whole workflow: you do not run `build.py` yourself, and `docs/` is gitignored
because it is a build output rather than the thing that is served.

It was not always so. Until 31 August 2026 Pages served `main:/docs` directly and nothing built
the site, which meant pushing edited YAML without remembering to run `build.py` published
nothing, silently: no job failed and no warning appeared, and the live site simply kept serving
the previous HTML. A local pre-push hook and a CI comparison both detected that; building on the
runner removes it, and both have been retired.

**Rollback**, if this ever needs undoing:

```bash
gh api -X PUT repos/Magnus-L/Magnus-L.github.io/pages -f build_type=legacy \
  -f 'source[branch]=main' -f 'source[path]=/docs'
python3 build.py && git add -f docs && git commit -m "Restore committed docs/" && git push
```

The deploy workflow checks that `docs/index.html` and `docs/CNAME` are non-empty before it
uploads anything, so a build that quietly produced nothing fails rather than replacing a working
site with an empty one.
