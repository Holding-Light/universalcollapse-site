#!/usr/bin/env python3
"""
add_methods_tn_papers.py — register the Methods S1-S3 + TN S1-S3 landings.

Six deposits, OSF-only, no PhilArchive. This is the layer the site already leans
on and never linked: Methods-S1 (`7U8SK`) is cited by the CMB paper and by the
site's own handoff discipline, and had no readable web surface.

All fields read off the landing pages (citation_title, citation_doi, description,
paper-sub, paper-eyebrow) — not recalled. pdf_file keeps the FULL published stem
(..._v1_0_2026_05.pdf) rather than the shortened form the earlier papers use,
because import_pdfs matches on the docx stem and these are the names on disk.
If the published files are named differently, import_pdfs will report `missing`
rather than grab a near-match — check its output before assuming.

    python3 tools/add_methods_tn_papers.py            # dry run
    python3 tools/add_methods_tn_papers.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")
REQUIRED = ["slug", "title", "doi", "lastmod", "priority", "built", "read"]

BLOCKS = [
    ("methods_s1", '''  - slug: methods_s1
    src_file: "UCT_Methods_S1_Auditing_Independence_v1_0_2026_05.docx"
    pdf_file: "UCT_Methods_S1_Auditing_Independence_v1_0_2026_05.pdf"
    title: "Auditing Independence in Multi-Channel Measurement"
    subtitle: "An Agreement-Curve Diagnostic for Genuine versus Correlated Redundancy"
    doi: "7U8SK"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "How to test independence rather than assume it — an agreement-curve audit separating genuine redundancy from channels that share upstream structure."
    built: true
    read: false
    pdf: false'''),
    ("methods_s2", '''  - slug: methods_s2
    src_file: "UCT_Methods_S2_Auditing_Constraint_Asymmetry_v1_0_2026_05.docx"
    pdf_file: "UCT_Methods_S2_Auditing_Constraint_Asymmetry_v1_0_2026_05.pdf"
    title: "Auditing Constraint Asymmetry in Latency-Based Resolution Tests"
    subtitle: "A Latency-Curve Diagnostic for Neutrality versus Confound-Induced Delay"
    doi: "HRKWT"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "How to tell neutrality-induced delay from confound-induced delay — a five-axis latency-curve audit that catches the circular-fit failure mode by design."
    built: true
    read: false
    pdf: false'''),
    ("methods_s3", '''  - slug: methods_s3
    src_file: "UCT_Methods_S3_Auditing_Record_State_v1_0_2026_05.docx"
    pdf_file: "UCT_Methods_S3_Auditing_Record_State_v1_0_2026_05.pdf"
    title: "Auditing Record State in Constraint-Sweep Hysteresis Tests"
    subtitle: "A Loop-Scaling Diagnostic for Record-Driven versus Confound-Induced Path Dependence"
    doi: "CQGTD"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "How to tell record-driven path dependence from rate lag — a loop-scaling audit against an independently measured record state."
    built: true
    read: false
    pdf: false'''),
    ("tn_s1", '''  - slug: tn_s1
    src_file: "UCT_TN_S1_Objectivity_from_Records_v1_0_2026_05.docx"
    pdf_file: "UCT_TN_S1_Objectivity_from_Records_v1_0_2026_05.pdf"
    title: "Objectivity from Records: An Exponential Consensus Bound"
    subtitle: "A Technical Note on the S1 Signature"
    doi: "6M7N3"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "The S1 bound, proved: when an outcome is redundantly recorded in conditionally independent fragments, observers converge exponentially in the number of fragments read."
    built: true
    read: false
    pdf: false'''),
    ("tn_s2", '''  - slug: tn_s2
    src_file: "UCT_TN_S2_Neutrality_Delays_Resolution_v1_0_2026_05.docx"
    pdf_file: "UCT_TN_S2_Neutrality_Delays_Resolution_v1_0_2026_05.pdf"
    title: "Neutrality Delays Resolution: An Expected Resolution-Time Bound"
    subtitle: "A Technical Note on the S2 Signature"
    doi: "6WRQV"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "The S2 bound, proved: expected resolution time is strictly maximized at zero bias and falls monotonically as constraint asymmetry grows, in closed form."
    built: true
    read: false
    pdf: false'''),
    ("tn_s3", '''  - slug: tn_s3
    src_file: "UCT_TN_S3_Records_Amplify_Hysteresis_v1_0_2026_05.docx"
    pdf_file: "UCT_TN_S3_Records_Amplify_Hysteresis_v1_0_2026_05.pdf"
    title: "Records Amplify Hysteresis: A Loop-Area Lemma"
    subtitle: "A Technical Note on the S3 Signature"
    doi: "QJMSZ"
    tier: "Methods & Theoretical Notes"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.7"
    desc: "The S3 lemma, proved: hysteresis loop area grows linearly with accumulated record state — and its sharpest point is what it denies."
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
        missing = [f for f in REQUIRED if f"    {f}:" not in block and f"- {f}:" not in block]
        if missing:
            sys.exit(f"  REFUSE — {slug} missing {missing} (build_site_meta would KeyError)")
        print(f"  ADD   {slug}")
        todo.append(block)

    if not todo:
        print("\n  nothing to add")
        return 0

    m = None
    for mm in re.finditer(r"^  - slug: ", s, re.M):
        m = mm
    if not m:
        sys.exit("  REFUSE — no existing paper entries; not guessing where to insert")
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
    print("  next:  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
