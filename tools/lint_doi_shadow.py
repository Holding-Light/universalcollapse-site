#!/usr/bin/env python3
"""
lint_doi_shadow.py — find doi.org links that shadow a live local page.

    python3 tools/lint_doi_shadow.py            (report; exit 1 if any found)
    python3 tools/lint_doi_shadow.py --quiet    (exit code only)

Your handoff, item 2:

    "Lint gap — nothing checks a library card's DOI against the ledger. Four
     Starter Pack cards displayed dead DOIs in both href and the visible label,
     and every gate passed."

This is that check, generalised. A doi.org link is a defect when the DOI belongs
to a paper that has its own page on this site — the reader gets bounced to OSF
for something sitting one path away, and the crawler never learns the local page
exists.

Not every doi.org link is wrong. THREE are legitimate:

  - a page citing ITS OWN DOI (every read page's "Cite as" line)
  - a DOI with no local page (a deposit still in the backlog)
  - ANY DOI inside <article> — that is the paper's own bibliography, and a
    reference list MUST cite the DOI. "Cite the DOI, not the URL" is the site's
    own instruction. The first version of this linter flagged 54 correct
    citations and 6 real defects: a 90% false-positive rate, which is how you
    train someone to stop reading a linter.

So the rule is: a NAVIGATION link (outside <article>) whose DOI maps to a
`built: true` paper and is not this page's own DOI. Everything else passes.

Reports only. Fixing an href without reading its link text is how you end up
with a button that says "View on OSF" pointing at a local page.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  pip install pyyaml --break-system-packages")

DATA = Path("tools/site_data.yaml")
ROOT = Path("public")
DOI_RE = re.compile(r'href="https://doi\.org/(10\.17605/OSF\.IO/([A-Z0-9]+))"')
OWN_RE = re.compile(r'name="citation_doi"\s+content="10\.17605/OSF\.IO/([A-Z0-9]+)"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if not DATA.exists():
        sys.exit(f"FAIL  {DATA} not found. Run from repo root.")
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))

    local = {p["doi"]: p["slug"] for p in d.get("papers", []) if p.get("built") and p.get("doi")}

    shadows, checked = [], 0
    for f in sorted(ROOT.rglob("*.html")):
        text = f.read_text(encoding="utf-8", errors="replace")
        checked += 1
        own = OWN_RE.search(text)
        own_doi = own.group(1) if own else None
        # <article> holds the paper body, including its reference list. DOIs in
        # there are citations, not navigation. Never flag them.
        art = [(m.start(), m.end()) for m in re.finditer(r"<article[^>]*>.*?</article>", text, re.S)]
        for m in DOI_RE.finditer(text):
            suffix = m.group(2)
            if suffix == own_doi:
                continue
            if any(a <= m.start() < b for a, b in art):
                continue
            if suffix not in local:
                continue
            line = text[: m.start()].count("\n") + 1
            ctx = text[max(0, m.start() - 90) : m.end() + 60].replace("\n", " ")
            ctx = re.sub(r"\s+", " ", ctx).strip()
            shadows.append((f, line, suffix, local[suffix], ctx))

    if not a.quiet:
        print(f"scanned {checked} html file(s) under {ROOT}/")
        print(f"papers with a local page: {len(local)}")
        print()
        if not shadows:
            print("no doi.org links shadowing a local page ✓")
        else:
            print(f"SHADOWED — {len(shadows)} navigation link(s) point off-site "
                  f"for a paper that has a page here:")
            print("(bibliography DOIs inside <article> are citations and are not checked)")
            print()
            for f, line, doi, slug, ctx in shadows:
                print(f"  {f}:{line}")
                print(f"    DOI {doi} -> /{slug}   (live)")
                print(f"    …{ctx[:130]}…")
                print()
            print("Reports only. Check each link's TEXT before rewriting its href —")
            print("a button reading 'View on OSF' should not point at a local page.")

    return 1 if shadows else 0


if __name__ == "__main__":
    sys.exit(main())
