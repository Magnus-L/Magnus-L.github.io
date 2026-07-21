#!/usr/bin/env python3
"""Refresh data/metrics.yaml from Google Scholar, then you rebuild + push.

    python3 scripts/refresh_metrics.py     # updates citations / h-index / i10 + as_of

Scholar has no official API and sometimes blocks automated requests. This does a
single polite request; if it is blocked it leaves metrics.yaml untouched and tells
you the numbers to edit by hand (open the Scholar URL, read the top-right table).
Paper counts on the site are derived from the YAML automatically and need no refresh.
"""
from pathlib import Path
import re, sys, datetime, urllib.request

ROOT = Path(__file__).resolve().parent.parent
MET = ROOT / "data" / "metrics.yaml"
URL = "https://scholar.google.se/citations?user=z0WQ2JcAAAAJ&hl=en"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def main():
    try:
        html = fetch()
        # The stats table lists six <td class="gsc_rsb_std"> cells:
        # Citations(all, since), h-index(all, since), i10(all, since).
        nums = [int(x) for x in re.findall(r'gsc_rsb_std">(\d+)<', html)]
        if len(nums) < 6:
            raise ValueError("could not locate the metrics table (Scholar may have blocked the request)")
        cit, cit_since, h, h_since, i10, i10_since = nums[:6]
    except Exception as e:
        print(f"! Could not auto-fetch: {e}")
        print(f"  Open {URL} and edit data/metrics.yaml by hand (citations / h_index / i10_index).")
        sys.exit(1)

    today = datetime.date.today().isoformat()
    txt = MET.read_text(encoding="utf-8")
    repl = {
        "as_of":            f'as_of: "{today}"',
        "citations":        f"citations: {cit}",
        "citations_since":  f"citations_since: {cit_since}          # since 2021",
        "h_index":          f"h_index: {h}",
        "i10_index":        f"i10_index: {i10}",
    }
    for key, line in repl.items():
        txt = re.sub(rf"(?m)^{key}:.*$", line, txt)
    MET.write_text(txt, encoding="utf-8")
    print(f"✓ metrics.yaml updated: {cit} citations (since 2021: {cit_since}), h={h}, i10={i10}  [{today}]")
    print("  Now: python3 build.py && git add -A && git commit && git push")

if __name__ == "__main__":
    main()
