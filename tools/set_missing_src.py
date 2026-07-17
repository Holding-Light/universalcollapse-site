#!/usr/bin/env python3
"""
set_missing_src.py — fill in src_file/pdf_file for sbom and s3_rag.

Both filenames were READ OFF DISK (find, 2026-07-17), not guessed:

    sbom    UCT_T20_Structural_Biology_Operating_Manual_v1.0_2026_05.docx   <- DOTS
    s3_rag  UCT_T16_S3RAG_Phase_D_Findings_v1_0_2026_05.docx                <- UNDERSCORES

Note the separators differ between the two. That is the known corpus inconsistency
(12 papers use v1.0, 3 use v1_0) and is exactly why these are copied from `find`
output rather than reconstructed from a pattern.

s3_rag: Jeremy identified UCT_T16_S3RAG_Phase_D_Findings as the deposit behind DOI
5QMVS. It had been deliberately left blank since an earlier session could not confirm
it. He is the adjudicator; this records his call.

Also REJECTS make_envs' suggestion that starter_mind -> Structural_Mind_v1_2.docx.
That is the T20 Structural Mind paper, a different work entirely. The Mind Starter
Pack is runnable Python with no docx. A fuzzy match on the word "mind" would have put
the wrong document under DOI A25CV.

    python3 tools/set_missing_src.py
    python3 tools/set_missing_src.py --apply
"""
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")

FIX = {
    "sbom": ("UCT_T20_Structural_Biology_Operating_Manual_v1.0_2026_05.docx",
             "UCT_T20_Structural_Biology_Operating_Manual_v1.0_2026_05.pdf"),
    "s3_rag": ("UCT_T16_S3RAG_Phase_D_Findings_v1_0_2026_05.docx",
               "UCT_T16_S3RAG_Phase_D_Findings_v1_0_2026_05.pdf"),
}


def main():
    apply = "--apply" in sys.argv
    if not DATA.exists():
        sys.exit("tools/site_data.yaml not found — run from the repo root")
    s = DATA.read_text(encoding="utf-8")
    orig = s

    for slug, (src, pdf) in FIX.items():
        m = re.search(rf"^  - slug: {re.escape(slug)}\s*$", s, re.M)
        if not m:
            sys.exit(f"  REFUSE — {slug} not in site_data")
        # bound this paper's block: from its slug line to the next "  - slug:" or EOF
        nxt = re.search(r"^  - slug: ", s[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(s) - m.end())
        block = s[m.end():end]

        if "src_file:" in block:
            cur = re.search(r'src_file: "([^"]*)"', block)
            if cur and cur.group(1) == src:
                print(f"  skip  {slug} — src_file already correct")
                continue
            print(f"  FIX   {slug}")
            print(f"          was: {cur.group(1) if cur else '?'}")
            print(f"          now: {src}")
            nb = re.sub(r'src_file: "[^"]*"', f'src_file: "{src}"', block)
            nb = re.sub(r'pdf_file: "[^"]*"', f'pdf_file: "{pdf}"', nb)
        else:
            print(f"  ADD   {slug} src_file + pdf_file")
            print(f"          {src}")
            nb = f'\n    src_file: "{src}"\n    pdf_file: "{pdf}"' + block
        s = s[:m.end()] + nb + s[end:]

    if s == orig:
        print("\n  nothing to change")
        return 0
    if not apply:
        print("\n  dry run — nothing written. Re-run with --apply")
        return 0

    DATA.write_text(s, encoding="utf-8")
    try:
        import yaml
        d = yaml.safe_load(s)
        for slug, (src, _) in FIX.items():
            p = next(x for x in d["papers"] if x["slug"] == slug)
            if p.get("src_file") != src:
                DATA.write_text(orig, encoding="utf-8")
                sys.exit(f"  REVERTED — {slug} src_file did not take")
        print(f"\n  wrote {DATA} — parses clean, {len(d['papers'])} papers")
    except SystemExit:
        raise
    except Exception as e:
        DATA.write_text(orig, encoding="utf-8")
        sys.exit(f"  REVERTED — yaml would not parse: {e}")
    print("  next:  python3 tools/make_envs.py --inventory   # want 21 confident")
    return 0


if __name__ == "__main__":
    sys.exit(main())
