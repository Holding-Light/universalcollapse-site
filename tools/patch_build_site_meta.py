#!/usr/bin/env python3
"""
patch_build_site_meta.py — make `read` and `pdf` derived, not declared.

Run once, from repo root:

    python3 tools/patch_build_site_meta.py

Why: site_data.yaml declared `read: true` for 17 papers while 38 read pages sat
on disk, and `pdf: true` for 2 while 38 PDFs sat on disk. build_site_meta.py
faithfully emitted what the yaml declared, so 21 live full-text papers were
absent from sitemap.xml and llms.txt announced "17 of 41". The generator was
never wrong. The declaration was.

A fact about the filesystem should be read off the filesystem.

Guards, in the build_paper.sh idiom:
  - refuses unless the input matches the pinned hash
  - refuses unless every anchor is found exactly once
  - round-trips the result through compile() before writing
  - writes nothing on any failure
"""
import hashlib
import shutil
import sys
from pathlib import Path

EXPECTED_SHA = "f979822cf54f1b391c4a6c3772e15fa532ac6f91715d61493e812269c57fc805"
TARGET = Path("tools/build_site_meta.py")

NEW_FUNCS = '''

def resolve_state(d, out_root):
    """`read` and `pdf` are facts about the filesystem, not declarations.

    Derive them from disk, report every drift, and never fill in a declared
    artifact that is absent. A stale flag is how 21 live papers went dark.
    """
    root = Path(out_root)
    drift = []
    for p in d.get("papers", []):
        slug = p["slug"]

        on_disk = (root / "read" / f"{slug}.html").is_file()
        if p.get("read") != on_disk:
            drift.append(f"  read  {slug:26s} yaml={str(p.get('read')):5s} -> disk={on_disk}")
        p["read"] = on_disk

        pdf_file = p.get("pdf_file")
        if pdf_file:
            on_disk = (root / "pdf" / pdf_file).is_file()
            if not on_disk:
                sys.exit(
                    f"FAIL  {slug}: declares pdf_file '{pdf_file}'\\n"
                    f"      not on disk at {root / 'pdf' / pdf_file}\\n"
                    f"      A declared artifact that is absent is a defect, not a false flag.\\n"
                    f"      Adjudicate. Do not override."
                )
        else:
            on_disk = False
        if p.get("pdf") != on_disk:
            drift.append(f"  pdf   {slug:26s} yaml={str(p.get('pdf')):5s} -> disk={on_disk}")
        p["pdf"] = on_disk
    return drift


def live_backlog(d):
    """Deposited DOIs with no entry built yet. Auto-prunes when a paper ships."""
    shipped = {p.get("doi") for p in built_papers(d)}
    return [doi for doi in d.get("backlog", []) if doi not in shipped]


def sync_flags(path, d):
    """Line-level flag write-back. A pyyaml round-trip would eat the Sync Law comment."""
    lines = Path(path).read_text(encoding="utf-8").split("\\n")
    want = {p["slug"]: {"read": p["read"], "pdf": p["pdf"]} for p in d.get("papers", [])}
    cur, n = None, 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\\s*-\\s+slug:\\s*(\\S+)\\s*$", ln)
        if m:
            cur = m.group(1)
            continue
        if cur not in want:
            continue
        for field in ("read", "pdf"):
            m2 = re.match(r"^(\\s*)" + field + r":\\s*(true|false)\\s*$", ln)
            if m2:
                new = "true" if want[cur][field] else "false"
                if m2.group(2) != new:
                    lines[i] = f"{m2.group(1)}{field}: {new}"
                    n += 1
    Path(path).write_text("\\n".join(lines), encoding="utf-8")
    return n
'''

EDITS = [
    (
        "import argparse\nimport sys\nfrom pathlib import Path",
        "import argparse\nimport re\nimport sys\nfrom pathlib import Path",
    ),
    (
        'def built_papers(d):\n    return [p for p in d.get("papers", []) if p.get("built")]\n',
        'def built_papers(d):\n    return [p for p in d.get("papers", []) if p.get("built")]\n'
        + NEW_FUNCS,
    ),
    (
        '    ap.add_argument("--check", action="store_true",\n'
        '                    help="Print outputs and a summary; write nothing.")',
        '    ap.add_argument("--check", action="store_true",\n'
        '                    help="Print outputs and a summary; write nothing. Wins over --sync-flags.")\n'
        '    ap.add_argument("--sync-flags", action="store_true",\n'
        '                    help="Persist derived read/pdf flags back into the yaml.")',
    ),
    (
        "    d = load(a.data)\n    sm = build_sitemap(d)",
        "    d = load(a.data)\n\n"
        "    drift = resolve_state(d, a.out)\n"
        "    if drift:\n"
        '        print(f"flag drift — disk is authoritative ({len(drift)} corrected):")\n'
        "        for line in drift:\n"
        "            print(line)\n"
        "        print()\n\n"
        "    sm = build_sitemap(d)",
    ),
    (
        "    print(f\"phase-1 backlog: {len(d.get('backlog', []))} live DOIs with no page yet\")",
        '    print(f"phase-1 backlog: {len(live_backlog(d))} live DOIs with no page yet")',
    ),
    (
        "    if a.check:\n        return 0",
        "    if a.check:\n"
        "        if a.sync_flags and drift:\n"
        '            print(f"\\n--check wins: would sync {len(drift)} flag(s), wrote nothing")\n'
        "        return 0\n\n"
        "    if a.sync_flags:\n"
        "        n = sync_flags(a.data, d)\n"
        '        print(f"synced {n} flag(s) into {a.data}")',
    ),
]


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL  {TARGET} not found. Run from repo root.")

    src = TARGET.read_text(encoding="utf-8")
    actual = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if actual != EXPECTED_SHA:
        sys.exit(
            f"FAIL  source hash mismatch — this is not the file the patch was written against.\n"
            f"      expected {EXPECTED_SHA}\n"
            f"      actual   {actual}\n"
            f"      The repo moved. Adjudicate before patching. Do not override."
        )
    print(f"  source pinned: {actual[:16]}…")

    out = src
    for old, new in EDITS:
        n = out.count(old)
        if n != 1:
            sys.exit(f"FAIL  anchor found {n}× (need exactly 1):\n      {old[:70]!r}")
        out = out.replace(old, new, 1)

    try:
        compile(out, str(TARGET), "exec")
    except SyntaxError as e:
        sys.exit(f"FAIL  patched file does not compile: {e}")

    shutil.copy2(TARGET, TARGET.with_suffix(".py.orig"))
    TARGET.write_text(out, encoding="utf-8")
    print(f"  backup: {TARGET.with_suffix('.py.orig')}")
    print(f"✓ patched {TARGET} ({len(EDITS)} edits, compiles clean)")
    print()
    print("Next, in order:")
    print("  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check")
    print("  expect: read pages 38, sitemap URLs 83, and a drift block listing 57 corrections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
