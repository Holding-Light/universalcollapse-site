#!/usr/bin/env python3
"""
fix_backlog_shape.py — repair live_backlog() in the already-patched build_site_meta.py.

Run once, from repo root, AFTER patch_build_site_meta.py:

    python3 tools/fix_backlog_shape.py

Why: I wrote live_backlog() assuming `backlog:` was a list of DOI strings. It is
a list of mappings. The tool encoded one assumption about a world that has two —
the same failure this whole session has been chasing, except this time the tool
was mine.

It crashed rather than returning a wrong number, which is the only reason this is
a five-minute fix instead of a stuck 27 that nobody notices for another month.

This version accepts a bare DOI string or a mapping carrying a 'doi' key, and
refuses anything else by printing the actual shape. It does not widen to fit.
"""
import hashlib
import shutil
import sys
from pathlib import Path

EXPECTED_SHA = "85e93533fd22d7e8ce978a3822f7da9f8c10be477e151723c7306567a0601a23"
TARGET = Path("tools/build_site_meta.py")

OLD = '''def live_backlog(d):
    """Deposited DOIs with no entry built yet. Auto-prunes when a paper ships."""
    shipped = {p.get("doi") for p in built_papers(d)}
    return [doi for doi in d.get("backlog", []) if doi not in shipped]'''

NEW = '''def live_backlog(d):
    """Deposited DOIs with no entry built yet. Auto-prunes when a paper ships.

    Backlog entries may be a bare DOI string or a mapping carrying one. Anything
    else is reported, not guessed — a wrong count here is how this sat at 27
    across twenty-four shipped papers.
    """
    shipped = {p.get("doi") for p in built_papers(d)}
    out = []
    for item in d.get("backlog", []):
        if isinstance(item, str):
            doi = item
        elif isinstance(item, dict) and "doi" in item:
            doi = item["doi"]
        else:
            sys.exit(
                f"FAIL  backlog entry shape not recognized: {item!r}\\n"
                f"      Expected a DOI string, or a mapping with a 'doi' key.\\n"
                f"      Paste the backlog block rather than widening this guess."
            )
        if doi not in shipped:
            out.append(doi)
    return out'''


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL  {TARGET} not found. Run from repo root.")

    src = TARGET.read_text(encoding="utf-8")
    actual = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if actual != EXPECTED_SHA:
        sys.exit(
            f"FAIL  source hash mismatch — this is not the patched file I expect.\n"
            f"      expected {EXPECTED_SHA}\n"
            f"      actual   {actual}\n"
            f"      Either patch_build_site_meta.py did not run, or the file moved.\n"
            f"      Adjudicate. Do not override."
        )
    print(f"  source pinned: {actual[:16]}…")

    n = src.count(OLD)
    if n != 1:
        sys.exit(f"FAIL  live_backlog anchor found {n}× (need exactly 1)")

    out = src.replace(OLD, NEW, 1)

    try:
        compile(out, str(TARGET), "exec")
    except SyntaxError as e:
        sys.exit(f"FAIL  patched file does not compile: {e}")

    shutil.copy2(TARGET, TARGET.with_suffix(".py.prebacklog"))
    TARGET.write_text(out, encoding="utf-8")
    print(f"  backup: {TARGET.with_suffix('.py.prebacklog')}")
    print("✓ live_backlog now reads both shapes and refuses a third")
    print()
    print("Next:")
    print("  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check")
    print("  expect: read pages 38, sitemap URLs 83, and a backlog count that is no longer 27")
    return 0


if __name__ == "__main__":
    sys.exit(main())
