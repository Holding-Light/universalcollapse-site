#!/usr/bin/env python3
"""
add_ag_papers.py — insert the three Architecture & Governance papers into site_data.

Every field below was read off the landing pages themselves (citation_title,
citation_doi, description, paper-sub) — not recalled. The landings already shipped
to public/ and pass lint; this registers them in the ledger so the sitemap,
llms.txt, status.py and the library flip all see them.

Run once, from the repo root:

    python3 tools/add_ag_papers.py            # dry run
    python3 tools/add_ag_papers.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")

BLOCKS = [
    ("program_map", '''  - slug: program_map
    src_file: "UCT_AG_Program_Map_v1_0_2026_06.docx"
    pdf_file: "UCT_AG_Program_Map_v1.0.pdf"
    title: "Program Map: Universal Collapse Theory as a Coherence-First Research Program"
    subtitle: "Architecture, Claims, and Falsification"
    doi: "CFASB"
    tier: "Architecture &mdash; Governance"
    version: "1.0"
    philarchive: null
    desc: "What the program is — every layer placed, claim levels stated, falsification entry points identified. Read after Kernel First."
    built: true
    read: false'''),
    ("falsification_standards", '''  - slug: falsification_standards
    src_file: "UCT_AG_Falsification_Standards_v1_0_2026_06.docx"
    pdf_file: "UCT_AG_Falsification_Standards_v1.0.pdf"
    title: "Failure Modes and Falsification Standards for Universal Collapse Theory"
    subtitle: "Where the Program Can Fail — Per Claim, Per Layer, and as a Whole"
    doi: "TN7Z3"
    tier: "Architecture &mdash; Governance"
    version: "1.0"
    philarchive: null
    desc: "Where the program can fail — per claim, per layer, and as a whole. The consolidated falsification standard for Universal Collapse Theory."
    built: true
    read: false'''),
    ("worked_demonstrations", '''  - slug: worked_demonstrations
    src_file: "UCT_AG_Two_Worked_Demonstrations_v1_0_2026_06.docx"
    pdf_file: "UCT_AG_Two_Worked_Demonstrations_v1.0.pdf"
    title: "Two Worked Demonstrations: The Research Stack and the Applied Stack"
    subtitle: "The Research Stack and the Applied Stack, Worked — and the Line Between Them"
    doi: "Z7HY2"
    tier: "Architecture &mdash; Governance"
    version: "1.0"
    philarchive: null
    desc: "One research-stack vertical — S2 from proved bound to live run, including a recorded failure — and one applied-stack reverse-audit, with the firewall between them stated."
    built: true
    read: false'''),
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
        else:
            print(f"  ADD   {slug}")
            todo.append(block)

    if not todo:
        print("\n  nothing to add")
        return 0

    # append after the last paper entry, before any top-level key that follows
    m = None
    for mm in re.finditer(r"^  - slug: ", s, re.M):
        m = mm
    if not m:
        sys.exit("  REFUSE — no existing paper entries found; not guessing where to insert")
    nxt = re.search(r"^[a-z_]+:", s[m.end():], re.M)
    at = m.end() + (nxt.start() if nxt else len(s) - m.end())
    ins = "\n" + "\n\n".join(todo) + "\n"
    out = s[:at].rstrip("\n") + "\n" + ins + s[at:]

    print(f"\n  add {len(todo)} paper(s)")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
        return 0

    DATA.with_suffix(".yaml.bak").write_text(s, encoding="utf-8")
    DATA.write_text(out, encoding="utf-8")
    try:
        import yaml
        d = yaml.safe_load(out)
        print(f"  wrote {DATA} — parses clean, {len(d['papers'])} papers")
    except Exception as e:
        DATA.write_text(s, encoding="utf-8")
        sys.exit(f"  REVERTED — yaml would not parse: {e}")
    print("  next:  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
