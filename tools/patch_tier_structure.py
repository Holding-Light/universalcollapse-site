#!/usr/bin/env python3
"""
patch_tier_structure.py — the code half. Tier becomes structure, not decoration.

    python3 tools/patch_tier_structure.py

Run fix_tiers.py --apply FIRST. An unescaped "&mdash;" inside JSON-LD becomes
"&amp;mdash;" and the parse lint rejects the page.

Two patches:

  build_site_meta.py   Kills the "Other" bucket. Every tier gets its own section
                       under its real name, and every paper gets its DOI and
                       full-text marker.

                       The bug: two loops. The tier loop emitted {desc}{full}{doi}.
                       The leftover loop, twelve lines down, emitted {desc}. Any
                       paper whose tier wasn't in TIER_ORDER fell through and lost
                       its citation — 19 of 41.

                       TIER_ORDER stops being a gate. It's now an optional
                       sequence override; unlisted tiers follow in site_data order.

  uct-paper.html       Tier into the JSON-LD as a nested CreativeWorkSeries:
                       paper -> tier -> program.

                       This is the one that matters. A model answering a cold
                       prompt retrieves /read/pr02_chaos directly and never opens
                       llms.txt. Before this, the tier existed only as a markdown
                       header in a file that retrieval never reads.
"""
import hashlib
import shutil
import sys
from pathlib import Path

META = Path("tools/build_site_meta.py")
TPL = Path("tools/uct-paper.html")
META_SHA = "fab16d45ce935338a597e868dd1b32939f9e15154f422b76e263757102329d4f"
TPL_SHA = "b3f4d198eecc2c17cdf06c5c8fac73c32800f1e069b11d8324f23e8726dc5e8f"

META_OLD = '''def built_papers(d):
    return [p for p in d.get("papers", []) if p.get("built")]
'''

META_NEW = '''def built_papers(d):
    return [p for p in d.get("papers", []) if p.get("built")]


def tier_sequence(papers):
    """Every tier, in order. TIER_ORDER first; unlisted tiers follow in site_data order.

    TIER_ORDER used to be a gate: a tier not named there dumped its papers into
    an "Other" bucket that emitted no DOI. It is now a sequence override only.
    A paper with no tier cannot be placed and is reported rather than dropped.
    """
    missing = [p["slug"] for p in papers if not p.get("tier")]
    if missing:
        sys.exit(
            f"FAIL  papers with no tier: {', '.join(missing)}\\n"
            f"      A paper with no tier cannot be placed in llms.txt.\\n"
            f"      Adjudicate. Do not default."
        )
    seq = [t for t in TIER_ORDER if any(p.get("tier") == t for p in papers)]
    for p in papers:
        if p["tier"] not in seq:
            seq.append(p["tier"])
    return seq


def paper_line(p, base):
    """One paper, one line, always with its DOI. The single emit path."""
    target = f"{base}/read/{p['slug']}" if p.get("read") else f"{base}/{p['slug']}"
    desc = " ".join(p["desc"].split())
    full = " Full text." if p.get("read") else " Abstract; full text via DOI."
    doi = f" DOI 10.17605/OSF.IO/{p['doi']}"
    return f"- [{p['title']}]({target}): {desc}{full}{doi}"
'''

META_OLD2 = '''    # Group papers by tier, in reading order
    seen = set()
    for tier in TIER_ORDER:
        group = [p for p in papers if p.get("tier") == tier]
        if not group:
            continue
        seen.add(tier)
        L.append(f"## {tier}")
        L.append("")
        for p in group:
            target = f"{base}/read/{p['slug']}" if p.get("read") else f"{base}/{p['slug']}"
            desc = " ".join(p["desc"].split())
            doi = f" DOI 10.17605/OSF.IO/{p['doi']}"
            full = " Full text." if p.get("read") else " Abstract; full text via DOI."
            L.append(f"- [{p['title']}]({target}): {desc}{full}{doi}")
        L.append("")

    leftover = [p for p in papers if p.get("tier") not in seen]
    if leftover:
        L.append("## Other")
        L.append("")
        for p in leftover:
            target = f"{base}/read/{p['slug']}" if p.get("read") else f"{base}/{p['slug']}"
            L.append(f"- [{p['title']}]({target}): {' '.join(p['desc'].split())}")
        L.append("")
'''

META_NEW2 = '''    # Every tier, its own section, one emit path. No leftover bucket.
    for tier in tier_sequence(papers):
        group = [p for p in papers if p.get("tier") == tier]
        L.append(f"## {tier}")
        L.append("")
        for p in group:
            L.append(paper_line(p, base))
        L.append("")
'''

TPL_OLD = '''  "isPartOf": {
    "@type": "CreativeWork",
    "name": "Universal Collapse Theory",
    "url": "https://universalcollapse.com"
  }'''

TPL_NEW = '''  "isPartOf": {
    "@type": "CreativeWorkSeries",
    "name": "$tier$",
    "isPartOf": {
      "@type": "CreativeWorkSeries",
      "@id": "https://universalcollapse.com/#program",
      "name": "Universal Collapse Theory",
      "url": "https://universalcollapse.com"
    }
  }'''


def check(path, sha):
    if not path.exists():
        sys.exit(f"FAIL  {path} not found. Run from repo root.")
    src = path.read_text(encoding="utf-8")
    actual = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if actual != sha:
        sys.exit(
            f"FAIL  source hash mismatch on {path}\n"
            f"      expected {sha}\n"
            f"      actual   {actual}\n"
            f"      Adjudicate before patching. Do not override."
        )
    print(f"  {path.name} pinned: {actual[:16]}…")
    return src


def apply(src, edits, name):
    out = src
    for old, new in edits:
        n = out.count(old)
        if n != 1:
            sys.exit(f"FAIL  {name}: anchor found {n}× (need exactly 1):\n      {old[:70]!r}")
        out = out.replace(old, new, 1)
    return out


def main():
    meta_src = check(META, META_SHA)
    tpl_src = check(TPL, TPL_SHA)

    meta_out = apply(meta_src, [(META_OLD, META_NEW), (META_OLD2, META_NEW2)], "build_site_meta.py")
    tpl_out = apply(tpl_src, [(TPL_OLD, TPL_NEW)], "uct-paper.html")

    try:
        compile(meta_out, str(META), "exec")
    except SyntaxError as e:
        sys.exit(f"FAIL  build_site_meta.py does not compile: {e}")

    if '"## Other"' in meta_out:
        sys.exit("FAIL  the Other bucket survived the patch")

    shutil.copy2(META, META.with_suffix(".py.pre_tier"))
    shutil.copy2(TPL, TPL.with_suffix(".html.pre_tier"))
    META.write_text(meta_out, encoding="utf-8")
    TPL.write_text(tpl_out, encoding="utf-8")

    print("✓ tools/build_site_meta.py — Other bucket removed, single emit path, DOI on every paper")
    print("✓ tools/uct-paper.html     — tier into JSON-LD as nested CreativeWorkSeries")
    print()
    print("Next, in order:")
    print("  python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check")
    print("  expect: no 'Other' section, every paper carrying a DOI")
    print("  ./tools/build_paper.sh tools/wp01.env")
    print("  expect: lint clean, and the badge reading 'Tier 1 — White Papers'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
