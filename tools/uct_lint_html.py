#!/usr/bin/env python3
"""uct_lint_html.py — Rule 4 gate for generated HTML (web sibling of uct_lint.py).

The docx→HTML batch conversion is where notation silently degrades and encoding
artifacts enter. uct_lint.py guards the docx sources; nothing guarded the output.
This does.

Enforces:
  1. NOTATION LAW  — C^K_t (K superscript, t subscript). Forbidden in rendered HTML:
       "C_K" / "C_{K}" literal                         -> ERROR
       "CKt" / "CK_t" (mangled sub/sup collapse)       -> ERROR
       C + U+2096 (subscript-k char), "C_k"            -> WARN
     Legitimate: Cᴷ (U+1D30), <sup>K</sup>, MathML msubsup. Never flagged.

  2. ENCODING     — U+FFFD replacement chars, mojibake (Â, â€™, Ã—)   -> ERROR
     One live instance today: "Tier 0 �� Gateway" on /read/kernel_first.

  3. CANONICAL    — every page declares rel=canonical                 -> ERROR if absent
     --self-canonical: canonical must equal the page's own URL        -> ERROR if not
     (Read pages canonicalising to their landing tell crawlers to treat the
      full text as a duplicate — the opposite of what the retrieval layer is for.)

  4. CITATION TAGS— on landing pages: citation_title, citation_author,
     citation_doi, citation_publication_date, citation_public_url  -> ERROR if absent
     citation_pdf_url                                              -> WARN if absent
     (pdf_url is what lets Scholar index the full text. 2/17 have it today.)

  5. SITEMAP AGREEMENT (--sitemap) — canonical URLs and sitemap <loc> must match
     exactly: no .html in one and not the other, no trailing-slash drift.

Usage:
  python3 uct_lint_html.py public/**/*.html
  python3 uct_lint_html.py --url https://universalcollapse.com/read/kernel_first
  python3 uct_lint_html.py --sitemap public/sitemap.xml public/*.html
  python3 uct_lint_html.py --url ... --self-canonical --landing

Exit: 0 = PASS (warnings ok), 1 = FAIL (errors), 2 = usage/IO.
"""
import argparse
import re
import sys
import subprocess
from pathlib import Path

# --- notation ---------------------------------------------------------------
RE_CK_UPPER = re.compile(r"C_\{?K\}?")
RE_CK_MANGLED = re.compile(r"\bCK_?t\b")
RE_CK_LOWER = re.compile(r"C_\{?k\}?|C\u2096")

# --- encoding ---------------------------------------------------------------
RE_FFFD = re.compile(r"\uFFFD")
RE_MOJIBAKE = re.compile(r"Ã[©¨¤¶±—–]|â€[™œ\x9d“”]|Â[·«»°]|Ã—")

# --- head tags --------------------------------------------------------------
RE_CANONICAL = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
RE_CANONICAL_ALT = re.compile(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', re.I)
RE_CITATION = re.compile(r'<meta[^>]+name=["\']citation_([a-z_]+)["\']', re.I)

REQUIRED_CITATION = ["title", "author", "doi", "publication_date", "public_url"]
WARN_CITATION = ["pdf_url"]

# strip tags/script/style before notation+encoding scan (avoid false hits in JS/CSS)
RE_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
RE_TAG = re.compile(r"<[^>]+>")


def visible_text(html):
    t = RE_SCRIPT.sub(" ", html)
    t = RE_TAG.sub(" ", t)
    return t


def snippet(text, m, width=64):
    i = max(0, m.start() - 24)
    s = " ".join(text[i:i + width].split())
    return ("…" if i else "") + s + "…"


def fetch(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "25", url],
                       capture_output=True, timeout=40)
    return r.stdout.decode("utf-8", errors="replace")


def norm(u):
    """Normalise a URL for comparison: drop scheme-host case, trailing slash (except root)."""
    u = u.strip()
    if u.endswith("/") and u.count("/") > 3:
        u = u[:-1]
    return u


def lint(name, html, args, sitemap_locs=None):
    errors, warns = [], []
    vis = visible_text(html)

    # 1 — notation
    for m in RE_CK_UPPER.finditer(vis):
        errors.append(f"NOTATION: forbidden C_K form — {snippet(vis, m)}")
    for m in RE_CK_MANGLED.finditer(vis):
        errors.append(f"NOTATION: mangled operator (sub/sup lost) — {snippet(vis, m)}")
    for m in RE_CK_LOWER.finditer(vis):
        warns.append(f"NOTATION: lowercase C_k variant — {snippet(vis, m)}")

    # 2 — encoding
    n_fffd = len(RE_FFFD.findall(html))
    if n_fffd:
        m = RE_FFFD.search(vis) or RE_FFFD.search(html)
        errors.append(f"ENCODING: {n_fffd}× U+FFFD replacement char — {snippet(vis, m) if m else ''}")
    for m in RE_MOJIBAKE.finditer(html):
        errors.append(f"ENCODING: mojibake — {snippet(html, m)}")
        break

    # 3 — canonical
    cm = RE_CANONICAL.search(html) or RE_CANONICAL_ALT.search(html)
    canonical = cm.group(1) if cm else None
    if not canonical:
        errors.append("CANONICAL: no rel=canonical declared")
    elif args.self_canonical and args.url:
        if norm(canonical) != norm(args.url):
            errors.append(
                f"CANONICAL: not self-referential — declares {canonical} "
                f"but page is {args.url} (crawlers will treat this page as a duplicate)"
            )

    # 4 — citation tags
    if args.landing:
        found = {m.group(1).lower() for m in RE_CITATION.finditer(html)}
        for req in REQUIRED_CITATION:
            if req not in found:
                errors.append(f"CITATION: missing required citation_{req}")
        for w in WARN_CITATION:
            if w not in found:
                warns.append(f"CITATION: missing citation_{w} (Scholar full-text indexing)")

    # 5 — sitemap agreement
    if sitemap_locs is not None and canonical:
        if norm(canonical) not in {norm(x) for x in sitemap_locs}:
            errors.append(f"SITEMAP: canonical {canonical} absent from sitemap")
        if ".html" in canonical:
            errors.append(f"SITEMAP: canonical carries .html extension — {canonical}")

    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="local HTML files")
    ap.add_argument("--url", action="append", default=[], help="fetch and lint a live URL")
    ap.add_argument("--sitemap", help="sitemap.xml to check canonical agreement against")
    ap.add_argument("--self-canonical", action="store_true",
                    help="require canonical == page's own URL (use with --url)")
    ap.add_argument("--landing", action="store_true",
                    help="apply Scholar citation-tag checks (landing pages)")
    a = ap.parse_args()

    if not a.files and not a.url:
        ap.print_help()
        return 2

    locs = None
    if a.sitemap:
        locs = re.findall(r"<loc>([^<]+)</loc>", Path(a.sitemap).read_text())

    total_e = total_w = 0
    targets = [(f, Path(f).read_text(encoding="utf-8", errors="replace"), None) for f in a.files]
    for u in a.url:
        targets.append((u, fetch(u), u))

    for name, html, url in targets:
        a.url = url
        e, w = lint(name, html, a, locs)
        total_e += len(e); total_w += len(w)
        status = "FAIL" if e else ("WARN" if w else "PASS")
        print(f"[{status}] {name}")
        for x in e:
            print(f"    ERROR  {x}")
        for x in w:
            print(f"    warn   {x}")

    print(f"\n{len(targets)} page(s) — {total_e} error(s), {total_w} warning(s)")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main())
