#!/usr/bin/env python3
"""
add_t16_papers.py — register the five T1.6 landings in site_data.

Every field read off the landing pages themselves (citation_title, citation_doi,
description, paper-sub) — not recalled. Closes T1.6 at 8/8 local.

Fixes the defect in add_ag_papers.py: that script omitted `lastmod` and `priority`,
build_site_meta.py threw KeyError, and the sitemap silently never rebuilt while the
commit message claimed it had. This one asserts every required field is present
before writing, and reverts if the YAML won't parse.

    python3 tools/add_t16_papers.py            # dry run
    python3 tools/add_t16_papers.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")

# fields build_site_meta.py indexes into directly — a missing one is a hard crash
REQUIRED = ["slug", "title", "doi", "lastmod", "priority", "built", "read"]

BLOCKS = [
    ("entropy_as_record", '''  - slug: entropy_as_record
    src_file: "UCT_T16_Entropy_as_Record_v1_0_2026_07.docx"
    pdf_file: "UCT_T16_Entropy_as_Record_v1.0.pdf"
    title: "Entropy as Record: A Locked-Source Shape Test of an SMBH-Dominated Cosmic Entropy Ledger Across Redshift"
    subtitle: "A Locked-Source Shape Test of an SMBH-Dominated Cosmic Entropy Ledger Across Redshift"
    doi: "2RC4D"
    tier: "Tier 1.6 — Empirical Demonstrations"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "Physics wing of the T1.6 corpus — does the assembled cosmic entropy ledger grow the way a record-accumulation reading expects? A locked-source, pre-specified shape test."
    built: true
    read: false
    pdf: false'''),
    ("cmb_records", '''  - slug: cmb_records
    src_file: "UCT_T16_CMB_Record_Consensus_v1_0_2026_07.docx"
    pdf_file: "UCT_T16_CMB_Record_Consensus_v1.0.pdf"
    title: "CMB Record Consensus"
    subtitle: "A Record-Consensus Diagnostic on the Planck PR3 Component-Separated Maps"
    doi: "PNF89"
    tier: "Tier 1.6 — Empirical Demonstrations"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "How quickly disagreement shrinks when redundant record channels are averaged — a reproducible consensus diagnostic on Planck PR3, stating exactly what the agreement licenses."
    built: true
    read: false
    pdf: false'''),
    ("f2_positive_control", '''  - slug: f2_positive_control
    src_file: "UCT_T16_F2_Training_Layer_Positive_Control_v1_0_2026_07.docx"
    pdf_file: "UCT_T16_F2_Training_Layer_Positive_Control_v1.0.pdf"
    title: "F2 — Training-Layer Positive Control: Install–Remove Hysteresis of a Fine-Tuned Structural Grammar at K_train"
    subtitle: "Install–Remove Hysteresis of a Fine-Tuned Structural Grammar at K_train"
    doi: "5TG3P"
    tier: "Tier 1.6 — Empirical Demonstrations"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "The training-layer arm of the T1.6 positive controls — a structural grammar installed by LoRA fine-tuning, counter-trained back, and measured for install–remove hysteresis at K_train."
    built: true
    read: false
    pdf: false'''),
    ("s3_calibration", '''  - slug: s3_calibration
    src_file: "UCT_T16_S3_Positive_Control_Calibration_v1_0_2026_07.docx"
    pdf_file: "UCT_T16_S3_Positive_Control_Calibration_v1.0.pdf"
    title: "Calibrating the S₃ Detector: A Positive-Control Study of Constraint-Reinstatement Detection in a Frontier Language Model"
    subtitle: "A Positive-Control Study of Constraint-Reinstatement Detection in a Frontier Language Model"
    doi: "JAEZQ"
    tier: "Tier 1.6 — Empirical Demonstrations"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "The missing positive control for the S₃ detector — planted constraint-reinstatement events of pre-registered intensity, recovered by a frozen instrument at characterized sensitivity and specificity."
    built: true
    read: false
    pdf: false'''),
    # s3_rag: src_file/pdf_file deliberately OMITTED — the docx behind 5QMVS was not
    # identified. make_envs and import_pdfs both skip papers without them, so the
    # landing works and simply never gets a read page until the source is named.
    # Guessing here would be how the wrong bytes end up under a live DOI.
    ("s3_rag", '''  - slug: s3_rag
    title: "S₃ Retrieval-Channel Hysteresis — A Controlled RAG Test (S3-RAG-01)"
    subtitle: "A Controlled RAG Test (S3-RAG-01)"
    doi: "5QMVS"
    tier: "Tier 1.6 — Empirical Demonstrations"
    version: "1.0"
    philarchive: null
    lastmod: "2026-07-16"
    priority: "0.8"
    desc: "The retrieval-channel companion — S₃ hysteresis tested on a search-grounded RAG system under controlled pack-swap conditions, reporting a bounded clean-record result."
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
        else:
            missing = [f for f in REQUIRED if f"    {f}:" not in block and f"- {f}:" not in block]
            if missing:
                sys.exit(f"  REFUSE — {slug} block is missing {missing} "
                         f"(build_site_meta.py would KeyError)")
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
        bad = [p["slug"] for p in d["papers"]
               if any(f not in p for f in ("lastmod", "priority"))]
        if bad:
            DATA.write_text(s, encoding="utf-8")
            sys.exit(f"  REVERTED — these would crash build_site_meta: {bad}")
        print(f"  wrote {DATA} — parses clean, {len(d['papers'])} papers, "
              f"all carry lastmod+priority")
    except SystemExit:
        raise
    except Exception as e:
        DATA.write_text(s, encoding="utf-8")
        sys.exit(f"  REVERTED — yaml would not parse: {e}")
    print("  next:  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
