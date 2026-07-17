#!/usr/bin/env python3
"""
add_starter_packs.py — register the three Starter Pack landings.

Deliberately WITHOUT src_file / pdf_file. The packs are runnable Python, not
documents: three scripts around a byte-identical uct_signatures.py engine, deposited
on OSF as code. There is no docx to build a read page from and no PDF to import, so
make_envs, import_pdfs and patch_citation_pdf all skip them — correctly. Their CTA
points at OSF because that is where the artifact lives; that is the pack being code,
not a routing failure.

The bundle (UWRS3) is gone — three packs now, not four. Their DOIs were re-minted:
XRE7B->ADM6U, M8S39->F7NBY, QCWN8->A25CV. fix_starter_packs.py corrected the library
cards, which had been displaying the dead DOIs in both href and visible label.

    python3 tools/add_starter_packs.py            # dry run
    python3 tools/add_starter_packs.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")
REQUIRED = ["slug", "title", "doi", "lastmod", "priority", "built", "read"]

BLOCKS = [
    ("starter_physics", '''  - slug: starter_physics
    title: "Universal Collapse Theory — Physics Starter Pack"
    subtitle: "A runnable on-ramp — three portable signatures, one shared engine"
    doi: "ADM6U"
    tier: "Starter Pack — Physics"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Run the three portable signatures yourself in about a minute — physics framing, same engine as the other two packs. Built to fail visibly if the predictions are wrong."
    built: true
    read: false
    pdf: false'''),
    ("starter_biology", '''  - slug: starter_biology
    title: "Universal Collapse Theory — Biology Starter Pack"
    subtitle: "A runnable on-ramp — three portable signatures, one shared engine"
    doi: "F7NBY"
    tier: "Starter Pack — Biology"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Run the three portable signatures yourself in about a minute — biology framing, same engine as the other two packs. Built to fail visibly if the predictions are wrong."
    built: true
    read: false
    pdf: false'''),
    ("starter_mind", '''  - slug: starter_mind
    title: "Universal Collapse Theory — Mind Starter Pack"
    subtitle: "A runnable on-ramp — three portable signatures, one shared engine"
    doi: "A25CV"
    tier: "Starter Pack — Mind"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Run the three portable signatures yourself in about a minute — mind framing, same engine as the other two packs. Built to fail visibly if the predictions are wrong."
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
        missing = [f for f in REQUIRED
                   if f"    {f}:" not in block and f"- {f}:" not in block]
        if missing:
            sys.exit(f"  REFUSE — {slug} missing {missing}")
        print(f"  ADD   {slug}  (code deposit — no src_file/pdf_file by design)")
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
