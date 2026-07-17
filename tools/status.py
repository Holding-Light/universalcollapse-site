#!/usr/bin/env python3
"""
status.py — where the site actually is, generated from the files themselves.

The Ledger Rule turned on the build process: never hand-write a status, generate
it. Every column below is read off disk or off the page — nothing is recalled,
nothing is asserted.

Answers, in one command:
  - which papers have a landing / read page / PDF / citation tag
  - what every library card links to, and whether a local page exists for it
  - what's in the DOI backlog with no page at all

    python3 tools/status.py
    python3 tools/status.py --library     # link audit only
    python3 tools/status.py --queue       # just what's next
"""
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

# One backlog definition. status.py showed 27 across twenty-four shipped papers
# because it read the yaml's declared list; live_backlog prunes every DOI that
# appears in a built paper, so it self-corrects on every ship.
from build_site_meta import live_backlog

DATA = Path("tools/site_data.yaml")
PUB = Path("public")


def papers_state(d):
    pdfs = {p.name for p in (PUB / "pdf").glob("*.pdf")}
    rows = []
    for p in d.get("papers", []):
        slug = p["slug"]
        land = PUB / f"{slug}.html"
        read = PUB / "read" / f"{slug}.html"
        has_land = land.exists()
        has_read = read.exists()
        pdf = p.get("pdf_file")
        has_pdf = bool(pdf and pdf in pdfs)
        has_tag = has_land and 'name="citation_pdf_url"' in land.read_text(
            encoding="utf-8", errors="replace")
        has_sha = bool(p.get("pdf_sha256"))
        rows.append((slug, p.get("doi", "?"), has_land, has_read, has_pdf, has_tag, has_sha))
    return rows


def library_links():
    f = PUB / "library.html"
    if not f.exists():
        return None, []
    h = f.read_text(encoding="utf-8")
    # The real markup is  <a href="..." ... class="paper-card">  — href BEFORE class.
    # An earlier version of this function looked for class-before-href, fell through to
    # a fallback that grabbed the NEXT card's href, and reported every card's neighbour.
    # Off-by-one that looked plausible because cards cluster by tier. Match both orders.
    cards = re.findall(r'<a\s+href="([^"]+)"[^>]*\bclass="[^"]*\bpaper-card\b', h)
    cards += re.findall(r'<a\s[^>]*\bclass="[^"]*\bpaper-card\b[^>]*\shref="([^"]+)"', h)
    return h, cards


def classify(u):
    if "philarchive" in u:
        return "PhilArchive"
    if "osf.io" in u:
        return "OSF"
    if "doi.org" in u:
        return "doi.org"
    if "amazon" in u:
        return "Amazon"
    if u.startswith("/read/"):
        return "local /read/"
    if u.startswith("/pdf/"):
        return "local /pdf/"
    if u.startswith("/"):
        return "local landing"
    if u.startswith("#"):
        return "anchor"
    return "other"


def main():
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    only = sys.argv[1] if len(sys.argv) > 1 else None

    if only in (None, "--queue"):
        rows = papers_state(d)
        print("=" * 74)
        print("PAPERS  (landing / read page / pdf on disk / citation tag / pdf sha)")
        print("=" * 74)
        print(f"{'slug':<20}{'doi':<8}{'land':<6}{'read':<6}{'pdf':<6}{'tag':<6}{'sha':<5}")
        print("-" * 74)
        for slug, doi, l, r, p, t, s in rows:
            m = lambda b: " ok  " if b else "  .  "
            print(f"{slug:<20}{doi:<8}{m(l)}{m(r)}{m(p)}{m(t)}{m(s)}")
        n = len(rows)
        print(f"\n  {n} papers | "
              f"landing {sum(r[2] for r in rows)}/{n} | read {sum(r[3] for r in rows)}/{n} | "
              f"pdf {sum(r[4] for r in rows)}/{n} | tag {sum(r[5] for r in rows)}/{n} | "
              f"sha {sum(r[6] for r in rows)}/{n}")
        gaps = [r[0] for r in rows if not all(r[2:])]
        if gaps:
            print(f"  incomplete: {', '.join(gaps)}")

    if only in (None, "--library"):
        h, cards = library_links()
        print()
        print("=" * 74)
        print("LIBRARY  — what every card links to")
        print("=" * 74)
        if h is None:
            print("  public/library.html not found")
        else:
            c = Counter(classify(u) for u in cards)
            for k, v in sorted(c.items(), key=lambda x: -x[1]):
                print(f"  {k:<18} {v:>3}")
            print(f"  {'TOTAL CARDS':<18} {len(cards):>3}")

            slugs = {p["slug"] for p in d.get("papers", [])}
            off = [u for u in cards if classify(u) in ("PhilArchive", "OSF", "doi.org")]
            if off:
                print(f"\n  {len(off)} card(s) still routing off-site — these are the")
                print("  entries with no local page yet (the backlog, made visible):")
                for u in off:
                    print(f"    {u}")

    if only in (None, "--queue"):
        bl = live_backlog(d)
        if bl:
            print()
            print("=" * 74)
            print(f"BACKLOG — {len(bl)} live DOI(s) with no page")
            print("=" * 74)
            for b in bl:
                print(f"  {b}")

    print()
    print("  NOTE: a library card routing off-site is not debt — it points at the")
    print("  archival copy because no local page exists yet. Each paper added flips")
    print("  one card from off-site to local. Nothing else in the library changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
