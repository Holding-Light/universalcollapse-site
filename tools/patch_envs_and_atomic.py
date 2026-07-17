#!/usr/bin/env python3
"""
patch_envs_and_atomic.py — unblock the 38-paper rebuild, safely.

    python3 tools/patch_envs_and_atomic.py            (dry run, writes nothing)
    python3 tools/patch_envs_and_atomic.py --apply

Does two things.

1. PDF_URL into every .env, read off site_data.yaml's pdf_file.

   PDF_URL has never been set in any env. The template's only consumer was
   $if(citation_pdf_url)$...$endif$ — a guarded display link that renders
   nothing on an empty var and exits 0. So all 38 read pages have shipped
   without a PDF button since the day they were built, silently, and nothing
   in the stack could report it. Removing that guard from the meta tag is
   what finally made it speak.

2. build_paper.sh writes atomically.

   Today it runs `pandoc -o "$OUT"` and lints afterward. A failed lint exits 1
   with the broken file already on disk. Across a 38-paper loop that leaves
   broken pages sitting in public/ for `git add -A` to sweep up — which is
   exactly how the .bak and .orig files got committed. This builds to
   "$OUT.building", lints that, and only moves it into place on a clean lint.

Never overwrites a PDF_URL that disagrees with site_data. Reports and refuses.
"""
import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  pip install pyyaml --break-system-packages")

DATA = Path("tools/site_data.yaml")
SH = Path("tools/build_paper.sh")
SH_SHA = "41a8471087d604ce2d98e380ead5e7a72187fea2aac918226b709cbcfa6fa114"
BASE = "https://universalcollapse.com"

SH_OLD = '''pandoc "$SRC" \\
  --from "$FROM" \\'''
SH_NEW = '''# ---- atomic write ---------------------------------------------------------
# Build to a scratch path and only move it into place on a clean lint. A failed
# lint used to leave the broken file on disk for `git add -A` to find.
FINAL="$OUT"
OUT="${OUT}.building"
trap 'rm -f "$OUT"' EXIT

pandoc "$SRC" \\
  --from "$FROM" \\'''

SH_OLD2 = '''echo "✓ $OUT  ($(wc -c < "$OUT") bytes)"'''
SH_NEW2 = '''mv "$OUT" "$FINAL"
echo "✓ $FINAL  ($(wc -c < "$FINAL") bytes)"'''


def patch_envs(d, apply):
    rows, problems = [], []
    for p in d.get("papers", []):
        slug, pdf_file = p["slug"], p.get("pdf_file")
        if not p.get("read"):
            continue
        env = Path("tools") / f"{slug}.env"
        if not env.exists():
            problems.append(f"  {slug}: read page exists but {env} does not")
            continue
        if not pdf_file:
            problems.append(f"  {slug}: read page exists but no pdf_file declared")
            continue

        want = f"{BASE}/pdf/{pdf_file}"
        text = env.read_text(encoding="utf-8")
        m = re.search(r'^PDF_URL=.*$', text, re.M)
        if m:
            cur = m.group(0).split("=", 1)[1].strip().strip('"').strip("'")
            if cur == want:
                continue
            if cur:
                problems.append(f"  {slug}: PDF_URL disagrees with site_data\n"
                                f"      env:       {cur}\n"
                                f"      site_data: {want}")
                continue
            new = re.sub(r'^PDF_URL=.*$', f'PDF_URL="{want}"', text, count=1, flags=re.M)
            rows.append((slug, "replace empty", pdf_file))
        else:
            new = text if text.endswith("\n") else text + "\n"
            new += f'PDF_URL="{want}"\n'
            rows.append((slug, "append", pdf_file))
        if apply:
            env.write_text(new, encoding="utf-8")
    return rows, problems


def patch_sh(apply):
    if not SH.exists():
        sys.exit(f"FAIL  {SH} not found. Run from repo root.")
    src = SH.read_text(encoding="utf-8")
    actual = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if actual != SH_SHA:
        sys.exit(
            f"FAIL  source hash mismatch on {SH}\n"
            f"      expected {SH_SHA}  (build_paper.sh AFTER patch_read_metadata.py)\n"
            f"      actual   {actual}\n"
            f"      Run patch_read_metadata.py first, or adjudicate. Do not override."
        )
    out = src
    for old, new in ((SH_OLD, SH_NEW), (SH_OLD2, SH_NEW2)):
        n = out.count(old)
        if n != 1:
            sys.exit(f"FAIL  build_paper.sh anchor found {n}× (need 1): {old[:50]!r}")
        out = out.replace(old, new, 1)
    if apply:
        shutil.copy2(SH, SH.with_suffix(".sh.pre_atomic"))
        SH.write_text(out, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write. Default is a dry run.")
    a = ap.parse_args()

    if not DATA.exists():
        sys.exit(f"FAIL  {DATA} not found. Run from repo root.")
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))

    rows, problems = patch_envs(d, a.apply)
    patch_sh(a.apply)

    verb = "SET" if a.apply else "WOULD SET"
    print(f"{verb} PDF_URL in {len(rows)} env(s):")
    for slug, how, pdf in rows[:6]:
        print(f"  {slug:26s} {how:14s} {pdf}")
    if len(rows) > 6:
        print(f"  … and {len(rows) - 6} more")

    if problems:
        print(f"\nPROBLEMS ({len(problems)}) — adjudicate, nothing written for these:")
        for x in problems:
            print(x)

    print(f"\n{verb} atomic write in build_paper.sh (build to .building, mv on clean lint)")

    if not a.apply:
        print("\nDry run. Nothing written. Re-run with --apply.")
        return 0

    print("\n✓ applied")
    print("\nNext, one paper:")
    print("  ./tools/build_paper.sh tools/wp01.env")
    print("  expect: lint clean, and a PDF link in the paper head")
    return 0


if __name__ == "__main__":
    sys.exit(main())
