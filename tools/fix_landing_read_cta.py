#!/usr/bin/env python3
"""
fix_landing_read_cta.py — point the primary button at the full text.

    python3 tools/fix_landing_read_cta.py            (dry run, writes nothing)
    python3 tools/fix_landing_read_cta.py --apply

21 landings show:

    <a class="cta cta-primary" href="https://doi.org/...">View on OSF &rarr;</a>
    <a class="cta cta-secondary" href="/pdf/...">Download PDF</a>

17 landings show:

    <a class="cta cta-primary" href="/read/wp01">Read &rarr;</a>
    <a class="cta cta-secondary" href="/pdf/...">Download PDF</a>

Same slot, same class. The 21 were built when those papers had no read page, so
the primary button went off-site. The read pages shipped; the buttons never
moved. Same 21 as the sitemap, llms.txt, citation_pdf_url, the backlog, the
build failures, and the nav links — this is the seventh artifact of one stale
boolean.

The /read/ page is the only surface carrying full text AND Scholar tags AND
JSON-LD. A PDF has text but no structured metadata. An OSF link has both but
sends the reader — and the crawler — off the site entirely.

Guards:
  - only touches a landing whose public/read/<slug>.html actually exists
  - refuses unless the page already has a cite-doi link, so the archival record
    survives the button being replaced. Nothing here should be the only path to
    a DOI.
  - matches "View on OSF" exactly. The Starter Packs say "Get the pack on OSF"
    and have no read page; they are not touched.
  - verifies the button's DOI matches the paper's own DOI before replacing it
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
CTA_RE = re.compile(
    r'<a class="cta cta-primary" href="https://doi\.org/10\.17605/OSF\.IO/([A-Z0-9]+)">'
    r'View on OSF &rarr;</a>'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write. Default is a dry run.")
    a = ap.parse_args()

    if not DATA.exists():
        sys.exit(f"FAIL  {DATA} not found. Run from repo root.")
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))

    rows, skipped, problems = [], [], []
    for p in d.get("papers", []):
        if not p.get("built"):
            continue
        slug, doi = p["slug"], p.get("doi")
        landing = ROOT / f"{slug}.html"
        read = ROOT / "read" / f"{slug}.html"

        if not landing.exists():
            problems.append(f"  {slug}: no landing at {landing}")
            continue
        text = landing.read_text(encoding="utf-8")
        m = CTA_RE.search(text)

        if not read.exists():
            if m:
                skipped.append((slug, "no read page — OSF button is correct"))
            continue
        if not m:
            continue

        if m.group(1) != doi:
            problems.append(
                f"  {slug}: button DOI {m.group(1)} != site_data DOI {doi} — adjudicate"
            )
            continue
        if 'class="cite-doi"' not in text:
            problems.append(
                f"  {slug}: no cite-doi link — the button is the only path to the DOI.\n"
                f"      Refusing to remove it. Adjudicate."
            )
            continue

        new = f'<a class="cta cta-primary" href="/read/{slug}">Read &rarr;</a>'
        rows.append((slug, m.group(0), new))
        if a.apply:
            landing.write_text(text.replace(m.group(0), new, 1), encoding="utf-8")

    verb = "REWROTE" if a.apply else "WOULD REWRITE"
    print(f"{verb} the primary CTA on {len(rows)} landing(s):\n")
    for slug, old, new in rows:
        print(f"  /{slug}")
        print(f"    from : {old}")
        print(f"    to   : {new}")
    print()

    if skipped:
        print(f"LEFT ALONE ({len(skipped)}):")
        for slug, why in skipped:
            print(f"  {slug}: {why}")
        print()

    if problems:
        print(f"PROBLEMS ({len(problems)}) — nothing written for these:")
        for x in problems:
            print(x)
        print()

    if not a.apply:
        print("Dry run. Nothing written. Re-run with --apply.")
        return 0

    print("✓ applied. The DOI survives on every page via its cite-doi link.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
