#!/usr/bin/env python3
"""
patch_library_links.py — flip a library card from its DOI to the local landing,
once that landing exists.

This is the recurring operation of the whole backlog. Registry v2.4's routing
principle states it:

    Website → paper links                 -> local /read/{slug} + same-origin /pdf/
    Website → paper links (no landing yet) -> DOI (falls back to OSF)

So an off-site card is not debt — it is the specified behaviour for a paper with
no local page. When the landing ships, the card flips. One card, one attribute.
Doing that by hand ~20 times is how a DOI gets mistyped into a link.

A card is flipped only when ALL of:
  - site_data has the paper, with a doi
  - public/{slug}.html actually exists on disk
  - the library has a card whose href is that paper's doi.org URL

The `paper-venue` line is left alone: it displays the DOI as a LABEL, and every
existing local card keeps it (Rice points at /rice and still shows KZ8TP). The
DOI stays visible; only the destination changes.

SAFETY: dry-run default; --apply writes .bak; idempotent; never invents a card.

    python3 tools/patch_library_links.py
    python3 tools/patch_library_links.py --apply
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

LIB = Path("public/library.html")
DATA = Path("tools/site_data.yaml")
PUB = Path("public")


def main():
    apply = "--apply" in sys.argv
    if not LIB.exists():
        sys.exit("public/library.html not found — run from the repo root")
    h = LIB.read_text(encoding="utf-8")
    orig = h
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))

    flipped = nolanding = notfound = already = 0
    print(f"{'slug':<24}{'doi':<8}action")
    print("-" * 68)

    for p in d.get("papers", []):
        slug, doi = p["slug"], p.get("doi")
        if not doi:
            continue
        landing = PUB / f"{slug}.html"

        # already local?
        if re.search(rf'<a\s+href="/{re.escape(slug)}"[^>]*class="[^"]*paper-card', h):
            already += 1
            continue

        # A card may point at EITHER the DOI or PhilArchive. The Primes are
        # PhilArchive-carded; everything else is doi.org. An earlier version of this
        # script matched doi.org only, so it silently found nothing on the Primes and
        # reported "no card" — the failure looked like success.
        candidates = [f"https://doi.org/10.17605/OSF.IO/{doi}"]
        if p.get("philarchive"):
            candidates.append(f"https://philarchive.org/rec/{p['philarchive']}")
        m = None
        for u in candidates:
            pat = re.compile(
                rf'<a\s+href="{re.escape(u)}"((?:[^>]*?))class="([^"]*paper-card[^"]*)"')
            m = pat.search(h)
            if m:
                break
        if not m:
            print(f"{slug:<24}{doi:<8}no DOI card in library (nothing to flip)")
            notfound += 1
            continue
        if not landing.exists():
            print(f"{slug:<24}{doi:<8}holding — no local landing yet (correct per v2.4)")
            nolanding += 1
            continue

        # flip: local href, drop target=_blank (internal link now)
        attrs = re.sub(r'\s*target="_blank"|\s*rel="noopener"', "", m.group(1))
        attrs = " " if not attrs.strip() else attrs
        new = f'<a href="/{slug}"{attrs}class="{m.group(2)}"'
        h = h[:m.start()] + new + h[m.end():]
        print(f"{slug:<24}{doi:<8}FLIP  doi.org -> /{slug}")
        flipped += 1

    print(f"\n  flip {flipped}   holding (no landing) {nolanding}   "
          f"already local {already}   no card {notfound}")
    if not flipped:
        print("  nothing to do")
        return 0
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
        return 0
    LIB.with_suffix(".html.bak").write_text(orig, encoding="utf-8")
    LIB.write_text(h, encoding="utf-8")
    print(f"  wrote {LIB} (.bak beside it)")
    print("  verify:  python3 tools/status.py --library")
    return 0


if __name__ == "__main__":
    sys.exit(main())
