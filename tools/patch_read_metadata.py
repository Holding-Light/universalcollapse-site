#!/usr/bin/env python3
"""
patch_read_metadata.py — items 1 + 2 + 3, one pass.

Run once, from repo root:

    python3 tools/patch_read_metadata.py

Patches two files:

  tools/uct-paper.html   Scholar citation meta block + schema.org JSON-LD.
                         Deletes the stale comment describing a design that was
                         abandoned (it said canonical points at the landing page;
                         the code has always self-canonicalled).

  tools/build_paper.sh   Three lint guards: JSON-LD must exist, must parse, and
                         must not carry U+FFFD.

Option A, decided: canonical stays self, citation_public_url points at the
landing. The read page is the retrieval surface — 11.8k words of full text —
and pointing canonical at the abstract would tell every crawler the abstract is
the real one. Scholar dedupes on citation_doi, which both pages now carry.

The U+FFFD check exists because a non-UTF-8 locale turns every em-dash into
three replacement characters AND STILL PRODUCES VALID JSON. A json.loads() test
passes on that. Verified: 18 replacement chars, JSON parses, lint catches it.

Guards, in the build_paper.sh idiom:
  - refuses unless both inputs match their pinned hash
  - refuses unless every anchor is found exactly once
  - writes nothing unless both files patch cleanly
"""
import hashlib
import shutil
import sys
from pathlib import Path

TPL = Path("tools/uct-paper.html")
SH = Path("tools/build_paper.sh")
TPL_SHA = "b98b08cdee84371157d336e67e2f47a8e0c3bba83aa1d1dfd16ec2e2c12649e0"
SH_SHA = "08ae121b7db1d9c00108d16e178c64f8fef2c7542fddf277709553d133626148"

TPL_OLD = '''  <!-- Full-text reading copy. The citable record is the landing page;
       canonical points there so Scholar and search consolidate on one URL. -->
  <link rel="canonical" href="$public_url$">

  <meta property="og:type" content="article">
  <meta property="og:title" content="$title$ — Universal Collapse Theory">
  <meta property="og:description" content="$description$">
  <meta property="og:url" content="$public_url$">
  <meta property="og:site_name" content="Universal Collapse Theory">
'''

TPL_NEW = '''  <link rel="canonical" href="$public_url$">

  <meta name="citation_title" content="$citation_title$">
  <meta name="citation_author" content="Jones, Jeremy C.">
  <meta name="citation_publication_date" content="$citation_date$">
  <meta name="citation_doi" content="$citation_doi$">
  <meta name="citation_public_url" content="$landing_url$">
  <meta name="citation_technical_report_institution" content="HoldingLight LLC">
  <meta name="citation_fulltext_world_readable" content="">
  <meta name="citation_pdf_url" content="$citation_pdf_url$">

  <meta property="og:type" content="article">
  <meta property="og:title" content="$title$ — Universal Collapse Theory">
  <meta property="og:description" content="$description$">
  <meta property="og:url" content="$public_url$">
  <meta property="og:site_name" content="Universal Collapse Theory">

  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "@id": "https://doi.org/$citation_doi$",
  "url": "$public_url$",
  "mainEntityOfPage": "$landing_url$",
  "name": "$citation_title$",
  "description": "$description$",
  "datePublished": "$citation_date$",
  "inLanguage": "en",
  "isAccessibleForFree": true,
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "DOI",
    "value": "$citation_doi$"
  },
  "sameAs": "https://doi.org/$citation_doi$",
  "author": {
    "@type": "Person",
    "@id": "https://orcid.org/0009-0007-2515-3774",
    "name": "Jeremy C. Jones",
    "sameAs": "https://orcid.org/0009-0007-2515-3774",
    "affiliation": {
      "@type": "Organization",
      "name": "HoldingLight LLC"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "HoldingLight LLC",
    "url": "https://universalcollapse.com"
  },
  "isPartOf": {
    "@type": "CreativeWork",
    "name": "Universal Collapse Theory",
    "url": "https://universalcollapse.com"
  }
}
  </script>
'''

SH_OLD = '''import sys, re
out = sys.argv[1]
h = open(out, encoding="utf-8").read()
fail = 0'''

SH_NEW = '''import sys, re, json
out = sys.argv[1]
h = open(out, encoding="utf-8").read()
fail = 0'''

SH_OLD2 = '''# Required tags
for tag in ('rel="canonical"',):
    if tag not in h:
        print(f"  FAIL  missing: {tag}"); fail = 1'''

SH_NEW2 = '''# Required tags
for tag in ('rel="canonical"', 'name="citation_doi"', 'name="citation_title"'):
    if tag not in h:
        print(f"  FAIL  missing: {tag}"); fail = 1

# JSON-LD must exist and must parse. This is the attribution surface: a model
# that retrieves the full text reads this to learn whose work it is.
m = re.search(r'<script type="application/ld\\+json">(.*?)</script>', h, re.S)
if not m:
    print("  FAIL  missing JSON-LD block"); fail = 1
else:
    try:
        json.loads(m.group(1))
    except Exception as e:
        print(f"  FAIL  JSON-LD does not parse: {e}"); fail = 1

# A non-UTF-8 locale turns every em-dash into three U+FFFD and STILL emits valid
# JSON. json.loads() passes on that. This is the only check that catches it.
if "\\ufffd" in h:
    n = h.count("\\ufffd")
    print(f"  FAIL  U+FFFD replacement char x{n} — pandoc ran without a UTF-8 locale"); fail = 1'''


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
            f"      The repo moved. Adjudicate before patching. Do not override."
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
    tpl_src = check(TPL, TPL_SHA)
    sh_src = check(SH, SH_SHA)

    tpl_out = apply(tpl_src, [(TPL_OLD, TPL_NEW)], "uct-paper.html")
    sh_out = apply(sh_src, [(SH_OLD, SH_NEW), (SH_OLD2, SH_NEW2)], "build_paper.sh")

    if "citable record is the landing page" in tpl_out:
        sys.exit("FAIL  stale comment survived the patch")

    shutil.copy2(TPL, TPL.with_suffix(".html.pre_meta"))
    shutil.copy2(SH, SH.with_suffix(".sh.pre_meta"))
    TPL.write_text(tpl_out, encoding="utf-8")
    SH.write_text(sh_out, encoding="utf-8")

    print("✓ tools/uct-paper.html   — 8 citation tags + JSON-LD, stale comment removed")
    print("✓ tools/build_paper.sh   — JSON-LD parse guard + U+FFFD guard")
    print()
    print("Backups written as *.pre_meta — gitignored, delete after you verify.")
    print()
    print("Next: rebuild ONE paper and read it before touching the other 37.")
    print("  ./tools/build_paper.sh tools/wp01.env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
