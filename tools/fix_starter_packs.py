#!/usr/bin/env python3
"""
fix_starter_packs.py — rebuild the Starter Packs section of the library.

This is not a routing flip. All four existing cards carry DOIs that no longer
resolve to the current deposits:

    UWRS3  bundle   -> no longer exists; card removed
    XRE7B  physics  -> now ADM6U
    M8S39  biology  -> now F7NBY
    QCWN8  mind     -> now A25CV

The stale DOI appears twice per card: in the href AND in the visible paper-venue
label. So the library has been displaying wrong DOIs, not just linking wrong.
patch_library_links could not fix this — it looks up the card BY the site_data DOI,
so it would search for ADM6U, find a card carrying XRE7B, and report "no card":
a silent no-op that reads as a clean run.

Structure and wording preserved exactly from the existing markup (read from
public/library.html at line 700-750, not reconstructed). Only the hrefs, the DOI
labels, and the descriptions change, and the bundle card is dropped.

SAFETY: dry-run default; --apply writes .bak; verifies the section is found before
touching anything; refuses if the grid can't be located unambiguously.

    python3 tools/fix_starter_packs.py
    python3 tools/fix_starter_packs.py --apply
"""
import re
import sys
from pathlib import Path

LIB = Path("public/library.html")

PACKS = [
    ("PHYSICS", "starter_physics", "Physics Starter Pack", "ADM6U",
     "Run the three portable signatures yourself in about a minute — physics framing, "
     "same engine as the other two packs. Built to fail visibly if the predictions are wrong."),
    ("BIOLOGY", "starter_biology", "Biology Starter Pack", "F7NBY",
     "Run the three portable signatures yourself in about a minute — biology framing, "
     "same engine as the other two packs. Built to fail visibly if the predictions are wrong."),
    ("MIND", "starter_mind", "Mind Starter Pack", "A25CV",
     "Run the three portable signatures yourself in about a minute — mind framing, "
     "same engine as the other two packs. Built to fail visibly if the predictions are wrong."),
]

CARD = '''        <a href="/{slug}" class="paper-card">
          <span class="paper-number">{num}</span>
          <div class="paper-info">
            <span class="paper-title">{title}</span>
            <span class="paper-desc">{desc}</span>
            <span class="paper-venue">OSF &middot; DOI 10.17605/OSF.IO/{doi}</span>
          </div>
          <span class="paper-arrow">&rarr;</span>
        </a>'''


def main():
    apply = "--apply" in sys.argv
    if not LIB.exists():
        sys.exit("public/library.html not found — run from the repo root")
    h = LIB.read_text(encoding="utf-8")
    orig = h

    # locate the Starter Packs grid: from its section-label to the grid's close.
    anchor = h.find('<div class="section-label">Starter Packs</div>')
    if anchor == -1:
        sys.exit("  REFUSE — Starter Packs section-label not found; not guessing")
    gs = h.find('<div class="papers-grid">', anchor)
    ge = h.find("\n      </div>", gs)
    if gs == -1 or ge == -1:
        sys.exit("  REFUSE — could not bound the papers-grid; not guessing")

    old = h[gs:ge]
    stale = re.findall(r"OSF\.IO/([A-Z0-9]{5})", old)
    print(f"  found grid: {len(re.findall(r'<a href=', old))} card(s), "
          f"DOIs {sorted(set(stale))}")
    for d in ("UWRS3", "XRE7B", "M8S39", "QCWN8"):
        if d in old:
            print(f"    stale: {d}")

    cards = "\n\n".join(
        CARD.format(num=n, slug=s, title=t, doi=d, desc=x) for n, s, t, d, x in PACKS)
    new = '<div class="papers-grid">\n\n' + cards + "\n"
    h = h[:gs] + new + h[ge:]

    print(f"\n  replace 4 cards -> 3 (bundle UWRS3 dropped)")
    for n, s, t, d, x in PACKS:
        print(f"    {t:<24} -> /{s}  (DOI {d})")

    if not apply:
        print("\n  dry run — nothing written. Re-run with --apply")
        return 0

    # verify before committing to disk
    for _, s, _, d, _ in PACKS:
        if f'href="/{s}"' not in h:
            sys.exit(f"  REFUSE — /{s} missing from result; not writing")
        if d not in h:
            sys.exit(f"  REFUSE — DOI {d} missing from result; not writing")
    for d in ("UWRS3", "XRE7B", "M8S39", "QCWN8"):
        if d in h:
            sys.exit(f"  REFUSE — stale DOI {d} still present; not writing")

    LIB.with_suffix(".html.bak").write_text(orig, encoding="utf-8")
    LIB.write_text(h, encoding="utf-8")
    print(f"\n  wrote {LIB} (.bak beside it)")
    print("  verify:  grep -c 'OSF.IO/UWRS3\\|OSF.IO/XRE7B' public/library.html   # want 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
