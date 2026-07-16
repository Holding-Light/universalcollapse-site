#!/usr/bin/env python3
"""
patch_citation_pdf.py — add citation_pdf_url to landings whose PDF now exists.

The Download button serves humans. `citation_pdf_url` is what Google Scholar
reads: it follows the tag from the landing to the file and indexes the paper.
15 landings currently have a working button and no tag — downloadable, but not
indexable as PDFs.

Anchors on the existing citation_* block and matches kernel_first's exact format:

    <meta name="citation_public_url" content="...">
    <meta name="citation_pdf_url" content="https://universalcollapse.com/pdf/...">   <- inserted
    <meta name="citation_fulltext_world_readable" content="">

RULES:
  - Only writes a tag when the PDF actually exists in public/pdf/. A citation_pdf_url
    pointing at a 404 is worse than none — Scholar will try to fetch it.
  - Filename comes from site_data's pdf_file (Rule 3). Never inferred.
  - Idempotent, dry-run default, .bak on apply, refuses on structure mismatch.

    python3 tools/patch_citation_pdf.py
    python3 tools/patch_citation_pdf.py --apply
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUBLIC = Path("public")
BASE = "https://universalcollapse.com"

# insertion anchors, in order of preference
ANCHORS = [
    re.compile(r'^\s*<meta name="citation_public_url"[^>]*>\s*$', re.M),
    re.compile(r'^\s*<meta name="citation_doi"[^>]*>\s*$', re.M),
    re.compile(r'^\s*<meta name="citation_publication_date"[^>]*>\s*$', re.M),
]


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    on_disk = {p.name for p in (PUBLIC / "pdf").glob("*.pdf")}

    added = present = nopdf = refused = 0
    print(f"{'slug':<18} {'action':<12} tag")
    print("-" * 84)

    for paper in d["papers"]:
        slug = paper["slug"]
        f = PUBLIC / f"{slug}.html"
        if not f.exists():
            print(f"{slug:<18} MISSING"); refused += 1; continue

        pdf = paper.get("pdf_file")
        if not pdf or pdf not in on_disk:
            print(f"{slug:<18} no pdf       (skipped — a tag pointing at a 404 is worse than none)")
            nopdf += 1
            continue

        s = f.read_text(encoding="utf-8")
        if 'name="citation_pdf_url"' in s:
            print(f"{slug:<18} present      {pdf}")
            present += 1
            continue

        m = next((a.search(s) for a in ANCHORS if a.search(s)), None)
        if not m:
            print(f"{slug:<18} REFUSE       no citation_* block found — not touching")
            refused += 1
            continue

        tag = f'\n  <meta name="citation_pdf_url" content="{BASE}/pdf/{pdf}">'
        out = s[:m.end()] + tag + s[m.end():]
        print(f"{slug:<18} ADD          {pdf}")
        added += 1
        if apply:
            f.with_suffix(".html.bak").write_text(s, encoding="utf-8")
            f.write_text(out, encoding="utf-8")

    print(f"\n  add {added}   already present {present}   no pdf {nopdf}   refused {refused}")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
