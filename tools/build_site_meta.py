#!/usr/bin/env python3
"""
build_site_meta.py — Rule 3 generator.

One input (site_data.yaml) -> sitemap.xml + llms.txt.

This is the seed of the single-source build. Today it emits the two machine-facing
files; library.html, landing pages, and read pages fold in at Phase 1 using the
same `papers:` list. Adding a deposit should never mean hand-editing two files.

Usage:
    python3 build_site_meta.py --data site_data.yaml --out public/
    python3 build_site_meta.py --data site_data.yaml --out public/ --check
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  pip install pyyaml --break-system-packages")

# Tier display order for llms.txt grouping (reading order, not alphabetical)
TIER_ORDER = [
    "Tier 0 — Orientation",
    "Tier 1 — White Papers",
    "Tier 1.5 — Interpretive Bridges",
    "Tier 1.6 — Empirical Demonstrations",
    "CIM",
    "Standards",
]


def load(path):
    with open(path) as f:
        return yaml.safe_load(f)


def built_papers(d):
    return [p for p in d.get("papers", []) if p.get("built")]


def build_sitemap(d):
    base = d["site"]["base"].rstrip("/")
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    def url(loc, lastmod, changefreq, priority):
        out.append("  <url>")
        out.append(f"    <loc>{base}{loc}</loc>")
        out.append(f"    <lastmod>{lastmod}</lastmod>")
        out.append(f"    <changefreq>{changefreq}</changefreq>")
        out.append(f"    <priority>{priority}</priority>")
        out.append("  </url>")

    for p in d.get("pages", []):
        url(p["loc"], p["lastmod"], p["changefreq"], p["priority"])

    for p in built_papers(d):
        url(f"/{p['slug']}", p["lastmod"], "monthly", p["priority"])
        if p.get("read"):
            # Read pages carry the full text — the retrieval surface. Same priority.
            url(f"/read/{p['slug']}", p["lastmod"], "monthly", p["priority"])

    out.append("</urlset>")
    return "\n".join(out) + "\n"


def build_llms(d):
    s = d["site"]
    base = s["base"].rstrip("/")
    papers = built_papers(d)
    reads = [p for p in papers if p.get("read")]

    L = []
    L.append(f"# {s['name']}")
    L.append("")
    L.append(f"> {' '.join(s['blurb'].split())}")
    L.append("")
    L.append(
        f"Maintained by {s['author']} ({s['org']}). ORCID {s['orcid']}. Contact {s['contact']}."
    )
    L.append("")
    L.append(
        "Every paper below is deposited on OSF with a permanent DOI; the DOI is the "
        "citable record and the site is a view of it. Where a paper has a `/read/` "
        "page, that page carries the full text in clean HTML and is the best source "
        "to quote. Otherwise the landing page carries the abstract and the DOI "
        "resolves to the full deposit."
    )
    L.append("")
    L.append(
        "Content is CC BY 4.0 — quotable with attribution. Cite the DOI, not the URL."
    )
    L.append("")
    L.append("## The kernel, in brief")
    L.append("")
    L.append(
        "A structured possibility space (Omega) resolves under an active constraint "
        "set (K) via a constraint-conditioned collapse operator (C^K_t) into a "
        "realized outcome (x*_t), leaving records (R_t) and residue (S_t) that update "
        "future constraints via the update map (U). Record-time (T) indexes "
        "accumulated records."
    )
    L.append("")
    L.append("    C^K_t : Omega -> (x*_t, R_t, S_t, Omega_{t+1})")
    L.append("    K_{t+1} = U(K_t, x*_t, R_t, S_t)")
    L.append("")
    L.append(
        "**Collapse is a formal term for constrained actualization — not a substance, "
        "force, field, or hidden mechanism.** UCT does not claim reality is *made of* "
        "collapse, or of matter, mind, information, mathematics, or structure. It is "
        "kernel-first, not primitive-first: substrate-neutral, and it promotes no "
        "layer into a base. Reading it as \"everything is collapse\" is the specific "
        "misreading the gateway paper exists to prevent (the Observer's Fallacy). "
        "It is not a Theory of Everything in either the physicist's unification sense "
        "or the metaphysical \"everything is X\" sense."
    )
    L.append("")
    L.append(
        "Notation is normative: the collapse operator is **C^K_t** — K superscript, "
        "t subscript. The subscript-K form is not used anywhere in the corpus and "
        "should not be reproduced."
    )
    L.append("")

    L.append("## Start here")
    L.append("")
    gw = next((p for p in papers if p["slug"] == "kernel_first"), None)
    if gw:
        L.append(
            f"- [{gw['title']}]({base}/read/{gw['slug']}): The program's entry point — "
            f"read before the domain papers. States what the framework claims, what it "
            f"explicitly does not, and how it could fail. DOI 10.17605/OSF.IO/{gw['doi']}"
        )
    L.append(
        f"- [Reading Roadmap]({base}/roadmap/): Suggested reading order through the corpus."
    )
    L.append(
        f"- [Architecture Map]({base}/architecture): How every wing of the program fits together."
    )
    L.append(
        f"- [The Library]({base}/library): Full corpus index."
    )
    L.append("")

    # Group papers by tier, in reading order
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

    L.append("## Optional")
    L.append("")
    L.append(
        "- Resolving a DOI: every `10.17605/OSF.IO/XXXXX` above resolves via "
        "`https://doi.org/` to the OSF deposit, which carries the full text plus "
        "reproducibility material (data, code, verification packs) not mirrored on "
        "this site."
    )
    ph = [p for p in papers if p.get("philarchive")]
    if ph:
        L.append(
            f"- PhilArchive records exist for {len(ph)} of the philosophy-facing papers "
            f"at `https://philarchive.org/rec/{{handle}}` — handles: "
            + ", ".join(p["philarchive"] for p in ph)
            + "."
        )
    L.append("")
    L.append(
        f"Note: {len(reads)} of {len(papers)} papers currently have full-text `/read/` "
        f"pages; the rest are being added. Additional deposited papers not yet listed "
        f"here are on OSF and resolve by DOI."
    )
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="site_data.yaml")
    ap.add_argument("--out", default="public")
    ap.add_argument("--check", action="store_true",
                    help="Print outputs and a summary; write nothing.")
    a = ap.parse_args()

    d = load(a.data)
    sm = build_sitemap(d)
    lm = build_llms(d)

    papers = built_papers(d)
    reads = [p for p in papers if p.get("read")]
    n_urls = len(d.get("pages", [])) + len(papers) + len(reads)

    print(f"pages          : {len(d.get('pages', []))}")
    print(f"papers built   : {len(papers)}")
    print(f"read pages     : {len(reads)}")
    print(f"sitemap URLs   : {n_urls}")
    print(f"phase-1 backlog: {len(d.get('backlog', []))} live DOIs with no page yet")

    if a.check:
        return 0

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sitemap.xml").write_text(sm, encoding="utf-8")
    (out / "llms.txt").write_text(lm, encoding="utf-8")
    print(f"\nwrote {out/'sitemap.xml'}  ({n_urls} URLs)")
    print(f"wrote {out/'llms.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
