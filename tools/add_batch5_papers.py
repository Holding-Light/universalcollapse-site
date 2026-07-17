#!/usr/bin/env python3
"""
add_batch5_papers.py — register sbom + how_minds_resolve.

Two papers, two different situations:

  sbom (CPKNX)              — Structural Biology Operating Manual, Tier 2, OSF-only.
                              Carded to doi.org; the flip is routine.
  how_minds_resolve (92RQ5) — the FRLB paper. PhilArchive JONHMR. Its card may
                              already exist from an earlier session; patch_library_links
                              matches PhilArchive as well as doi.org now, so it flips
                              either way. If the card was added under a different slug,
                              the script reports "no card" rather than inventing one.

All fields read off the landing pages, not recalled.

    python3 tools/add_batch5_papers.py            # dry run
    python3 tools/add_batch5_papers.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")
REQUIRED = ["slug", "title", "doi", "lastmod", "priority", "built", "read"]

BLOCKS = [
    ("sbom", '''  - slug: sbom
    src_file: "UCT_T20_Structural_Biology_Operating_Manual_v1_0_2026_05.docx"
    pdf_file: "UCT_T20_Structural_Biology_Operating_Manual_v1_0_2026_05.pdf"
    title: "Structural Biology: Operating Manual"
    subtitle: "Domain Companion to UCT WP03 (Biological Collapse)"
    doi: "CPKNX"
    tier: "Tier 2 — Operating Manuals"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "The biology layer made usable — postulates, protocols, a reporting standard, and worked examples from glucose regulation to evolutionary scaffolding."
    built: true
    read: false
    pdf: false'''),
    ("how_minds_resolve", '''  - slug: how_minds_resolve
    src_file: "UCT_T15_How_Minds_Resolve_v1_0_2026_07.docx"
    pdf_file: "UCT_T15_How_Minds_Resolve_v1_0_2026_07.pdf"
    title: "How Minds Resolve: The Faith-Reason-Logic-Belief Cycle"
    subtitle: "The Faith-Reason-Logic-Belief Cycle"
    doi: "92RQ5"
    tier: "Tier 1.5 — Bridges"
    version: "1.0"
    philarchive: "JONHMR"
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "The operative layer most frameworks leave unstated — how an individual mind enters a framework, tests it under feedback, and stabilizes a position into the next cycle."
    built: true
    read: false
    pdf: false'''),
]


def main():
    apply = "--apply" in sys.argv
    if not DATA.exists():
        sys.exit("tools/site_data.yaml not found — run from the repo root")
    s = DATA.read_text(encoding="utf-8")
    todo = []
    for slug, block in BLOCKS:
        if re.search(rf"^  - slug: {re.escape(slug)}\s*$", s, re.M):
            print(f"  skip  {slug} — already in site_data")
            continue
        # `slug` is "  - slug:", the rest are "    field:" — accept both forms.
        missing = [f for f in REQUIRED
                   if f"    {f}:" not in block and f"- {f}:" not in block]
        if missing:
            sys.exit(f"  REFUSE — {slug} missing {missing}")
        print(f"  ADD   {slug}")
        todo.append(block)
    if not todo:
        print("\n  nothing to add")
        return 0
    m = None
    for mm in re.finditer(r"^  - slug: ", s, re.M):
        m = mm
    if not m:
        sys.exit("  REFUSE — no existing entries; not guessing where to insert")
    nxt = re.search(r"^[a-z_]+:", s[m.end():], re.M)
    at = m.end() + (nxt.start() if nxt else len(s) - m.end())
    out = s[:at].rstrip("\n") + "\n\n" + "\n\n".join(todo) + "\n" + s[at:]
    print(f"\n  add {len(todo)} paper(s)")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
        return 0
    DATA.write_text(out, encoding="utf-8")
    try:
        import yaml
        d = yaml.safe_load(out)
        bad = [p["slug"] for p in d["papers"]
               if any(f not in p for f in ("lastmod", "priority"))]
        if bad:
            DATA.write_text(s, encoding="utf-8")
            sys.exit(f"  REVERTED — would crash build_site_meta: {bad}")
        print(f"  wrote {DATA} — parses clean, {len(d['papers'])} papers")
    except SystemExit:
        raise
    except Exception as e:
        DATA.write_text(s, encoding="utf-8")
        sys.exit(f"  REVERTED — yaml would not parse: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
