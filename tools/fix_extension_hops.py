#!/usr/bin/env python3
"""
fix_extension_hops.py — internal links must use the canonical extensionless URL.

All 41 landings carry href="/library.html" while the page's canonical (and the
sitemap loc) is /library. Both resolve on this host — which is exactly why the
hop survives: it works, so nothing fails. But every internal .html link names a
second URL for one page and contradicts the canonical the site itself declares.

Rewrites any internal href="/X.html" (including "/read/X.html") to the
extensionless form WHEN that extensionless path appears in public/sitemap.xml.
Assets, off-site links, and pages not in the sitemap are left alone.

Repeatable; dry-run by default; --apply writes. No backups — git is the backup.

    python3 tools/fix_extension_hops.py
    python3 tools/fix_extension_hops.py --apply
"""
import re
import sys
from pathlib import Path

PUB = Path("public")
RE_HREF = re.compile(r'href="(/[A-Za-z0-9_/\-]+)\.html"')


def sitemap_paths():
    sm = PUB / "sitemap.xml"
    if not sm.exists():
        sys.exit("FAIL  public/sitemap.xml not found — run from repo root")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm.read_text())
    return {re.sub(r"^https?://[^/]+", "", u).rstrip("/") or "/" for u in locs}


def main():
    apply = "--apply" in sys.argv
    canon = sitemap_paths()
    total, files = 0, 0
    for f in sorted(PUB.rglob("*.html")):
        html = f.read_text(encoding="utf-8")
        hits = []

        def sub(m):
            path = m.group(1)
            if path in canon:
                hits.append(path)
                return f'href="{path}"'
            return m.group(0)

        out = RE_HREF.sub(sub, html)
        if hits:
            files += 1
            total += len(hits)
            print(f"  {f}: {len(hits)} hop(s) -> {sorted(set(hits))}")
            if apply:
                f.write_text(out, encoding="utf-8")
    mode = "FIXED" if apply else "DRY-RUN (use --apply)"
    print(f"{mode}: {total} hop(s) in {files} file(s)")
    if apply and total:
        # verify: a second scan must find zero
        remaining = 0
        for f in PUB.rglob("*.html"):
            for m in RE_HREF.finditer(f.read_text(encoding="utf-8")):
                if m.group(1) in canon:
                    remaining += 1
        if remaining:
            sys.exit(f"FAIL  {remaining} hop(s) survived the rewrite — investigate")
        print("verified: zero canonical-shadowing .html hrefs remain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
