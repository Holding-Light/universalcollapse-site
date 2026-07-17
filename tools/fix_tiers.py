#!/usr/bin/env python3
"""
fix_tiers.py — the data half. Entities out, typo out.

    python3 tools/fix_tiers.py            (dry run, writes nothing)
    python3 tools/fix_tiers.py --apply

Three data repairs, no editorial decisions:

1. Unescape TIER in tools/*.env
   26 of 38 read pages render a literal "&mdash;" in the tier badge. A raw "&"
   is fine — pandoc escapes it to &amp; and the browser renders "&". A
   PRE-ENCODED entity is not: "&mdash;" becomes "&amp;mdash;" and the browser
   shows the literal text. Someone hand-encoded for HTML, then pandoc encoded
   it again. This is also what blocks tier from entering the JSON-LD, where
   "&amp;mdash;" would fail the parse lint.

2. Unescape tier in site_data.yaml
   llms.txt is plain text. "## Architecture &mdash; Governance" as a section
   header shows the entity literally. Only affects the 3 AG papers; every other
   tier already uses a real em-dash.

3. how_minds_resolve: "Tier 1.5 — Bridges" -> "Tier 1.5 — Interpretive Bridges"
   Four siblings carry the longer string; this one is four words short and
   therefore falls out of its own section into a leftover bucket that emits no
   DOI. It is a typo, not a choice — the siblings settle it.

html.unescape is idempotent: running twice changes nothing the second time.
Never touches a raw "&" that isn't part of a valid entity.
"""
import argparse
import html
import re
import sys
from pathlib import Path

DATA = Path("tools/site_data.yaml")
TYPO = ("Tier 1.5 — Bridges", "Tier 1.5 — Interpretive Bridges")
TYPO_SLUG = "how_minds_resolve"


def fix_envs(apply):
    rows = []
    for env in sorted(Path("tools").glob("*.env")):
        text = env.read_text(encoding="utf-8")
        m = re.search(r'^TIER=(.*)$', text, re.M)
        if not m:
            continue
        raw = m.group(1).strip()
        q = raw[0] if raw[:1] in ('"', "'") else ""
        val = raw.strip('"').strip("'")
        new_val = html.unescape(val)
        # The typo is a typo in both places. Four siblings carry the longer
        # string; fixing site_data alone would leave the badge and the JSON-LD
        # disagreeing with llms.txt.
        if env.stem == TYPO_SLUG and new_val == TYPO[0]:
            new_val = TYPO[1]
        if new_val == val:
            continue
        new_line = f'TIER={q}{new_val}{q}'
        rows.append((env.stem, val, new_val))
        if apply:
            env.write_text(re.sub(r'^TIER=.*$', new_line.replace('\\', '\\\\'),
                                  text, count=1, flags=re.M), encoding="utf-8")
    return rows


def fix_site_data(apply):
    if not DATA.exists():
        sys.exit(f"FAIL  {DATA} not found. Run from repo root.")
    lines = DATA.read_text(encoding="utf-8").split("\n")
    rows, cur = [], None
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*-\s+slug:\s*(\S+)\s*$", ln)
        if m:
            cur = m.group(1)
            continue
        m2 = re.match(r'^(\s*)tier:\s*(.*)$', ln)
        if not m2:
            continue
        indent, raw = m2.group(1), m2.group(2).strip()
        q = raw[0] if raw[:1] in ('"', "'") else ""
        val = raw.strip('"').strip("'")
        new_val = html.unescape(val)
        if cur == TYPO_SLUG and new_val == TYPO[0]:
            new_val = TYPO[1]
        if new_val == val:
            continue
        lines[i] = f'{indent}tier: {q}{new_val}{q}' if q else f'{indent}tier: {new_val}'
        rows.append((cur, val, new_val))
    if apply:
        DATA.write_text("\n".join(lines), encoding="utf-8")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write. Default is a dry run.")
    a = ap.parse_args()

    envs = fix_envs(a.apply)
    sd = fix_site_data(a.apply)
    verb = "FIXED" if a.apply else "WOULD FIX"

    print(f"{verb} TIER in {len(envs)} env(s):")
    seen = {}
    for slug, old, new in envs:
        seen.setdefault((old, new), []).append(slug)
    for (old, new), slugs in seen.items():
        print(f"  {len(slugs):2d} x  {old}")
        print(f"        -> {new}")

    print(f"\n{verb} tier in site_data.yaml for {len(sd)} paper(s):")
    for slug, old, new in sd:
        note = "  <- TYPO, not encoding" if old.replace("&mdash;", "—") == TYPO[0] or new == TYPO[1] else ""
        print(f"  {slug}{note}")
        print(f"    {old}")
        print(f"    -> {new}")

    if not a.apply:
        print("\nDry run. Nothing written. Re-run with --apply.")
        return 0

    print("\n✓ applied")
    print("\nNext:")
    print("  python3 tools/patch_tier_structure.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
