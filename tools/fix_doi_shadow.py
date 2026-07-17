#!/usr/bin/env python3
"""
fix_doi_shadow.py — point the six nav links at the pages they shadow.

    python3 tools/fix_doi_shadow.py            (dry run, writes nothing)
    python3 tools/fix_doi_shadow.py --apply

Companion to lint_doi_shadow.py, same rule, same exclusions:

  - never touches a DOI inside <article> — that is a bibliography, and a
    reference list must cite the DOI
  - never touches a page's own DOI (the "Cite as" line)
  - never touches a DOI with no local page (a bundle or a backlog deposit)

For each remaining link it does three things:

  href="https://doi.org/10.17605/OSF.IO/XXXXX"  ->  href="/slug"
  target="_blank"                                ->  removed
  rel="noopener"                                 ->  removed

The last two matter. These anchors were built as deliberate off-site links back
when the papers had no local page. Swapping the href alone leaves an internal
link that opens a new tab — which the site's own housekeeping already cleaned up
once. rel="noopener" is only meaningful alongside target="_blank"; without it,
it is noise.

Off-site links that are genuinely off-site — Amazon, PhilPeople, Stripe — keep
their target="_blank". Only the rewritten anchors are touched.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  pip install pyyaml --break-system-packages")

DATA = Path("tools/site_data.yaml")
ROOT = Path("public")
TAG_RE = re.compile(
    r'<a\s+((?:[^>]*?\s)?href="https://doi\.org/(10\.17605/OSF\.IO/([A-Z0-9]+))"(?:\s[^>]*?)?)>'
)
OWN_RE = re.compile(r'name="citation_doi"\s+content="10\.17605/OSF\.IO/([A-Z0-9]+)"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write. Default is a dry run.")
    a = ap.parse_args()

    if not DATA.exists():
        sys.exit(f"FAIL  {DATA} not found. Run from repo root.")
    d = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    local = {p["doi"]: p["slug"] for p in d.get("papers", []) if p.get("built") and p.get("doi")}

    rows, skipped = [], []
    for f in sorted(ROOT.rglob("*.html")):
        text = f.read_text(encoding="utf-8", errors="replace")
        own = OWN_RE.search(text)
        own_doi = own.group(1) if own else None
        art = [(m.start(), m.end())
               for m in re.finditer(r"<article[^>]*>.*?</article>", text, re.S)]

        out, last, changed = [], 0, 0
        for m in TAG_RE.finditer(text):
            suffix = m.group(3)
            inside = any(s <= m.start() < e for s, e in art)
            if suffix == own_doi or inside:
                continue
            if suffix not in local:
                line = text[: m.start()].count("\n") + 1
                skipped.append((f, line, suffix, "no local page — bundle or backlog"))
                continue

            slug = local[suffix]
            attrs = m.group(1)
            attrs = attrs.replace(f'href="https://doi.org/{m.group(2)}"', f'href="/{slug}"')
            attrs = re.sub(r'\s*target="_blank"', "", attrs)
            attrs = re.sub(r'\s*rel="noopener[^"]*"', "", attrs)
            attrs = re.sub(r"\s+", " ", attrs).strip()
            new_tag = f"<a {attrs}>"

            out.append(text[last:m.start()])
            out.append(new_tag)
            last = m.end()
            changed += 1

            line = text[: m.start()].count("\n") + 1
            body = text[m.end():m.end() + 400]
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body.split("</a>")[0])).strip()
            rows.append((f, line, suffix, slug, label[:64], m.group(0), new_tag))

        if changed and a.apply:
            out.append(text[last:])
            f.write_text("".join(out), encoding="utf-8")

    verb = "REWROTE" if a.apply else "WOULD REWRITE"
    print(f"{verb} {len(rows)} navigation link(s):\n")
    for f, line, doi, slug, label, old, new in rows:
        print(f"  {f}:{line}   {doi} -> /{slug}")
        print(f"    card : {label}")
        print(f"    from : {old}")
        print(f"    to   : {new}")
        print()

    if skipped:
        print(f"LEFT ALONE ({len(skipped)}) — correct as-is:")
        for f, line, doi, why in skipped:
            print(f"  {f}:{line}   {doi}   {why}")
        print()

    if not a.apply:
        print("Dry run. Nothing written. Re-run with --apply.")
        return 0

    print("✓ applied. Verify with:  python3 tools/lint_doi_shadow.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
