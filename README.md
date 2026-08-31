# Magnus-L.github.io — magnuslodefalk.com

Personal academic site. Single page, data-driven (edit `data/site.yaml`, run `python3 build.py`, push).
Shares the AI-Econ Lab design system (`assets/styles.css`). GitHub Pages serves `main` `/docs`.
Photo in `assets/magnus.jpg`. DNS cutover mirrors the lab site (Crossnet: apex A -> GitHub IPs, www CNAME -> magnus-l.github.io); do it only when ready.

## The docs/ freshness hook

GitHub Pages serves `main:/docs` directly and this repository has **no build Action**, so
editing `data/*.yaml` and pushing without running `build.py` publishes nothing, silently:
the YAML lands in the repository and the live site keeps serving the previous HTML.

`.githooks/pre-push` closes that. It rebuilds into a temporary directory and compares
against `docs/`, rather than comparing timestamps, which are meaningless after a clone. A
mismatch blocks the push and names the differing files. It fails open if `python3` or
PyYAML is missing, so a broken toolchain never blocks a push, and `git push --no-verify`
bypasses it deliberately.

**It is enabled per clone**, by `git config core.hooksPath .githooks`. That setting lives in
`.git/config` and is not pushed, so after re-cloning this repository run that command again
or the hook does nothing.
