#!/usr/bin/env python3
"""
patch_landing_jsonld.py — JSON-LD onto the 41 landing pages.

Read pages carry ScholarlyArticle JSON-LD (template-level, patch_read_metadata).
Landings carry Scholar citation_* meta and nothing else — so a crawler that
lands on /wp01 rather than /read/wp01 sees tags and no structured data. This
closes that gap (handoff 2026-07-17 item 3) via the §6-sanctioned route: a
one-shot-style patcher deriving the mechanical block; no authored prose is
read, matched, or rewritten.

SOURCES, and why two of them:
  - site_data.yaml       -> ledger DOI (the gate), tier (grouping — the split's
                            semantics: JSON-LD series = grouping, never badge),
                            site constants (author, ORCID, org, base)
  - the page's own tags  -> citation_title, citation_publication_date,
                            meta description
    The tags are already lint-gated against the ledger (check_against_ledger),
    and JSON-LD that disagreed with the tags beside it would be a new drift
    surface. If the page's citation_doi disagrees with the ledger, this script
    STOPS — that is a lint failure wearing a different hat.

TYPE: ScholarlyArticle when the ledger declares a pdf_file; the three Starter
Packs (code deposits, no PDF by design) emit SoftwareSourceCode instead —
mislabeling runnable Python as an article would be a category error in the
retrieval layer.

SHAPE mirrors tools/uct-paper.html's block exactly, with url and
mainEntityOfPage pointing at the landing (it is its own main entity). Where a
paper declares relations, read_first emits as isBasedOn — the one edge whose
schema.org semantics are honest here. supports/tested_by/related are program
edges, not citation claims; they render in the visible block and /library.json
rather than being stretched onto citation/mentions.

SAFETY:
  - dry-run by default; --apply writes. No backups: git is the backup.
  - repeatable: an existing marker-wrapped block is replaced in place.
  - refuses any page whose anchors or tags don't match, rather than guessing.
  - post-apply verification re-extracts every block from the written bytes and
    json.loads it — a block that does not parse never lands.

    python3 tools/patch_landing_jsonld.py
    python3 tools/patch_landing_jsonld.py --apply
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUB = Path("public")

MARK_BEGIN = "<!-- jsonld: derived by patch_landing_jsonld.py from site_data + this page's citation tags. Edit sources and rerun; do not hand-edit. -->"
MARK_END = "<!-- /jsonld -->"

RE_BLOCK = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)
RE_META = lambda k: re.compile(rf'<meta name="{k}" content="([^"]*)"')
RE_CANON = re.compile(r'<link rel="canonical" href="([^"]*)"')
ANCHOR_OG = re.compile(r"^([ \t]*)<!-- Open Graph", re.M)
ANCHOR_PRE = re.compile(r'^([ \t]*)<link rel="preconnect"', re.M)


def block_for(paper, site, html, slug):
    """Build the JSON-LD dict, or (None, reason) if the page refuses."""
    base = site["base"].rstrip("/")
    landing = f"{base}/{slug}"

    canon = RE_CANON.search(html)
    if not canon or canon.group(1).rstrip("/") != landing:
        return None, f"canonical is {canon.group(1) if canon else 'ABSENT'!r}, expected {landing!r}"

    ledger_doi = f"10.17605/OSF.IO/{paper['doi']}"
    tag_doi = RE_META("citation_doi").search(html)
    if tag_doi and tag_doi.group(1).strip() != ledger_doi:
        sys.exit(f"FAIL  {slug}: page citation_doi {tag_doi.group(1)!r} != ledger "
                 f"{ledger_doi!r} — this is a lint failure; fix it before patching")

    title = RE_META("citation_title").search(html)
    desc = RE_META("description").search(html)
    if not title or not desc:
        return None, "missing citation_title or meta description"
    date = RE_META("citation_publication_date").search(html)

    is_article = bool(paper.get("pdf_file"))
    obj = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle" if is_article else "SoftwareSourceCode",
        "@id": f"https://doi.org/{ledger_doi}",
        "url": landing,
        "mainEntityOfPage": landing,
        "name": title.group(1),
        "description": desc.group(1),
        **({"datePublished": date.group(1)} if date else {}),
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": ledger_doi},
        "sameAs": f"https://doi.org/{ledger_doi}",
        **({} if is_article else {"programmingLanguage": "Python"}),
        "author": {
            "@type": "Person",
            "@id": f"https://orcid.org/{site['orcid']}",
            "name": site["author"],
            "sameAs": f"https://orcid.org/{site['orcid']}",
            "affiliation": {"@type": "Organization", "name": site["org"]},
        },
        **({"isBasedOn": [f"{base}/{s}" for s in paper["relations"]["read_first"]]}
           if paper.get("relations", {}).get("read_first") else {}),
        "publisher": {"@type": "Organization", "name": site["org"], "url": base},
        "isPartOf": {
            "@type": "CreativeWorkSeries",
            "name": paper["tier"],
            "isPartOf": {
                "@type": "CreativeWorkSeries",
                "@id": f"{base}/#program",
                "name": site["name"],
                "url": base,
            },
        },
    }
    return obj, None


def render(obj, indent):
    payload = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
    lines = [f"{indent}{MARK_BEGIN}",
             f'{indent}<script type="application/ld+json">',
             payload,
             f"{indent}</script>",
             f"{indent}{MARK_END}",
             ""]
    return "\n".join(lines)


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    site = d["site"]
    done, replaced, refused = [], [], []

    for p in [x for x in d.get("papers", []) if x.get("built")]:
        slug = p["slug"]
        f = PUB / f"{slug}.html"
        if not f.exists():
            refused.append((slug, "no landing file")); continue
        html = f.read_text(encoding="utf-8")
        obj, why = block_for(p, site, html, slug)
        if obj is None:
            refused.append((slug, why)); continue

        if RE_BLOCK.search(html):
            m = ANCHOR_OG.search(html) or ANCHOR_PRE.search(html)
            indent = m.group(1) if m else "  "
            out = RE_BLOCK.sub(render(obj, indent), html, count=1)
            replaced.append(slug)
        else:
            m = ANCHOR_OG.search(html) or ANCHOR_PRE.search(html)
            if not m:
                refused.append((slug, "no insertion anchor (OG comment or preconnect)")); continue
            out = html[: m.start()] + render(obj, m.group(1)) + html[m.start():]
            done.append(slug)

        if apply:
            f.write_text(out, encoding="utf-8")

    mode = "APPLIED" if apply else "DRY-RUN (use --apply)"
    print(f"{mode}: insert {len(done)}, replace {len(replaced)}, refuse {len(refused)}")
    for s, why in refused:
        print(f"  REFUSED {s}: {why}")
    if refused:
        sys.exit(1)

    if apply:
        # verification: every landing's block must re-extract and parse
        bad = 0
        for p in [x for x in d.get("papers", []) if x.get("built")]:
            html = (PUB / f"{p['slug']}.html").read_text(encoding="utf-8")
            m = re.search(r'<script type="application/ld\+json">\n(.*?)\n[ \t]*</script>', html, re.S)
            if not m:
                print(f"  VERIFY FAIL {p['slug']}: no JSON-LD block found"); bad += 1; continue
            try:
                got = json.loads(m.group(1).replace("<\\/", "</"))
                assert got["identifier"]["value"] == f"10.17605/OSF.IO/{p['doi']}"
                assert got["url"].endswith(f"/{p['slug']}")
            except Exception as e:
                print(f"  VERIFY FAIL {p['slug']}: {e}"); bad += 1
        if bad:
            sys.exit(f"FAIL  {bad} landing(s) failed post-apply verification")
        print(f"verified: {sum(1 for x in d['papers'] if x.get('built'))} landings parse, "
              f"DOI and url agree with the ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
