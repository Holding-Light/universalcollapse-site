#!/usr/bin/env python3
"""
import_pdfs.py — copy published PDFs into public/pdf/ under their web names.

The PDFs already exist at ~/Desktop/Papers/Published pdf/. They carry the SAME
STEM as their docx (UCT_T15_Collapse_Reframed_v1.0_2026-02-12.pdf), while the web
copies are shortened (UCT_T0_Kernel_First_v1.0.pdf). So:

    site_data src_file  ->  stem  ->  "{stem}.pdf" in the published folder
                        ->  copied to public/pdf/{pdf_file}

MATCHING IS EXACT ON STEM. Never fuzzy. The published folder contains the same
class of decoys as the docx library — Rice.pdf beside Rice_FINAL.pdf,
Self_the_Ego_..._PsyArXiv copy.pdf beside the real one. A wrong PDF under a live
DOI is unrecoverable once Scholar indexes it.

Also records pdf_sha256 in site_data. The read pages are hash-pinned by
build_paper.sh; the PDF path has had NO guard at all. This closes that.

    python3 tools/import_pdfs.py                 # propose. copies nothing.
    python3 tools/import_pdfs.py --apply
    python3 tools/import_pdfs.py --verify        # re-hash public/pdf against site_data
"""
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = Path("tools/site_data.yaml")
DEST = Path("public/pdf")
SRC_DIR = Path(os.path.expanduser("~/Desktop/Papers/Published pdf"))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def verify(d):
    bad = 0
    for p in d["papers"]:
        f = DEST / (p.get("pdf_file") or "")
        want = p.get("pdf_sha256")
        if not p.get("pdf_file"):
            continue
        if not f.exists():
            print(f"  absent   {p['slug']:<18} {p['pdf_file']}")
            continue
        if not want:
            print(f"  no sha   {p['slug']:<18} {sha256(f)[:16]}… (record it)")
            continue
        got = sha256(f)
        ok = got == want
        print(f"  {'ok      ' if ok else 'MISMATCH'} {p['slug']:<18} {got[:16]}…")
        bad += (not ok)
    print(f"\n  {bad} mismatch(es)")
    return 1 if bad else 0


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))

    if "--verify" in sys.argv:
        return verify(d)

    if not SRC_DIR.exists():
        sys.exit(f"not found: {SRC_DIR}")
    pool = {p.name: p for p in SRC_DIR.glob("*.pdf")}

    print(f"published folder: {len(pool)} pdf(s)")
    print(f"{'slug':<18} {'status':<10} source → web name")
    print("-" * 92)

    found = missing = already = 0
    updates = {}
    for p in d["papers"]:
        slug, web = p["slug"], p.get("pdf_file")
        if not web:
            print(f"{slug:<18} NO NAME    (pdf_file unset in site_data)"); continue
        if (DEST / web).exists():
            print(f"{slug:<18} on site    {web}")
            already += 1
            continue

        src = p.get("src_file", "")
        stem = re.sub(r"\.docx$", "", src)
        cand = f"{stem}.pdf"
        if cand in pool:
            print(f"{slug:<18} FOUND      {cand}")
            print(f"{'':<18}            → {web}")
            found += 1
            if apply:
                shutil.copy2(pool[cand], DEST / web)
                updates[slug] = sha256(DEST / web)
        else:
            print(f"{slug:<18} missing    no '{cand[:58]}'")
            missing += 1

    print(f"\n  found {found}   already on site {already}   missing {missing}")

    if apply and updates:
        lines = DATA.read_text(encoding="utf-8").split("\n")
        out = []
        for l in lines:
            out.append(l)
            m = re.match(r"^  - slug: (\S+)\s*$", l)
            if m and m.group(1) in updates:
                out.append(f'    pdf_sha256: "{updates[m.group(1)]}"')
        DATA.write_text("\n".join(out), encoding="utf-8")
        print(f"  copied {len(updates)}; recorded pdf_sha256 for each")
        print("  next:  python3 tools/patch_pdf_button.py --apply")
    elif not apply:
        print("  proposal only — nothing copied. Re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
