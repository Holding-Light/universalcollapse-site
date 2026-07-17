#!/usr/bin/env python3
"""
add_primes_papers.py — register the five Tier 30 Primes landings.

The Primes are the only batch carded to PhilArchive rather than doi.org, so they
also required a fix to patch_library_links.py: it matched doi.org URLs only, and
would have reported "no card" on all five — a silent nothing that reads as success.

All fields read off the landing pages, not recalled.

    python3 tools/add_primes_papers.py            # dry run
    python3 tools/add_primes_papers.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")
REQUIRED = ["slug", "title", "doi", "lastmod", "priority", "built", "read"]

BLOCKS = [
    ("pr00_coherence", '''  - slug: pr00_coherence
    src_file: "UCT_T30_PR00_Prime_Coherence_v1_0_2026_06.docx"
    pdf_file: "UCT_T30_PR00_Prime_Coherence_v1_0_2026_06.pdf"
    title: "Order as the Default Outcome Under Constraint"
    subtitle: "Coherence as Constraint-Visible Structure"
    doi: "J2XSQ"
    tier: "Tier 30 — Primes"
    version: "1.0"
    philarchive: "JONOAT-4"
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Coherence is not something added by intelligence, teleology, or luck — it is what typically falls out of constraint. The positive ground of the Primes series."
    built: true
    read: false
    pdf: false'''),
    ("pr01_randomness", '''  - slug: pr01_randomness
    src_file: "UCT_T30_PR01_Prime_Randomness_v1_0_2026_06.docx"
    pdf_file: "UCT_T30_PR01_Prime_Randomness_v1_0_2026_06.pdf"
    title: "Against Randomness-First"
    subtitle: "Randomness as a Provisional Label for Unmodeled Structure"
    doi: "Y678R"
    tier: "Tier 30 — Primes"
    version: "1.0"
    philarchive: "JONARP"
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "'Random' is a scoped residual label, not an ontological primitive — refutable by one discovered regularity, and never certifiable by any finite search."
    built: true
    read: false
    pdf: false'''),
    ("pr02_chaos", '''  - slug: pr02_chaos
    src_file: "UCT_T30_PR02_Prime_Chaos_v1_0_2026_06.docx"
    pdf_file: "UCT_T30_PR02_Prime_Chaos_v1_0_2026_06.pdf"
    title: "Against Chaos-First"
    subtitle: "Chaos as Structured Unpredictability (Not Disorder)"
    doi: "A6EJN"
    tier: "Tier 30 — Primes"
    version: "1.0"
    philarchive: "JONACW-6"
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Chaos is structured unpredictability, not disorder — a reason to change what you predict and report the horizon, not to declare structure absent."
    built: true
    read: false
    pdf: false'''),
    ("pr03_intelligence", '''  - slug: pr03_intelligence
    src_file: "UCT_T30_PR03_Prime_Intelligence_v1_0_2026_06.docx"
    pdf_file: "UCT_T30_PR03_Prime_Intelligence_v1_0_2026_06.pdf"
    title: "Against Intelligence-First"
    subtitle: "Intelligence as Plastic Feedback and Constraint Navigation (Not Mystical Agency)"
    doi: "RN3TH"
    tier: "Tier 30 — Primes"
    version: "1.0"
    philarchive: "JONAIX"
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Intelligence is an endogenous plastic update loop, measurable against a non-learning baseline — not a primitive essence, and possible without consciousness."
    built: true
    read: false
    pdf: false'''),
    ("pr04_nothingness", '''  - slug: pr04_nothingness
    src_file: "UCT_T30_PR04_Prime_Nothingness_v1_0_2026_06.docx"
    pdf_file: "UCT_T30_PR04_Prime_Nothingness_v1_0_2026_06.pdf"
    title: "Against Nothingness-First"
    subtitle: "Vacuum Is Not Nothing (Ground Hygiene for Coherence-First Reasoning)"
    doi: "YHQ5F"
    tier: "Tier 30 — Primes"
    version: "1.0"
    philarchive: "JONANH-2"
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "Vacuum is not nothing. 'Nothing' cannot serve as an explanatory ground — if it has a rule, it is not nothing; if it has no rule, it explains nothing."
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
            print(f"  skip  {slug} — already in site_data"); continue
        # `slug` appears as "  - slug:", not "    slug:" — the list-item marker.
        # Checking only the 4-space form makes this guard refuse every valid block.
        missing = [f for f in REQUIRED
                   if f"    {f}:" not in block and f"- {f}:" not in block]
        if missing:
            sys.exit(f"  REFUSE — {slug} missing {missing}")
        print(f"  ADD   {slug}")
        todo.append(block)
    if not todo:
        print("\n  nothing to add"); return 0
    m = None
    for mm in re.finditer(r"^  - slug: ", s, re.M):
        m = mm
    nxt = re.search(r"^[a-z_]+:", s[m.end():], re.M)
    at = m.end() + (nxt.start() if nxt else len(s) - m.end())
    out = s[:at].rstrip("\n") + "\n\n" + "\n\n".join(todo) + "\n" + s[at:]
    print(f"\n  add {len(todo)} paper(s)")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply"); return 0
    DATA.write_text(out, encoding="utf-8")
    try:
        import yaml
        d = yaml.safe_load(out)
        bad = [p["slug"] for p in d["papers"] if any(f not in p for f in ("lastmod", "priority"))]
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
