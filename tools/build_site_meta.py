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
import re
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


def tier_sequence(papers):
    """Every tier, in order. TIER_ORDER first; unlisted tiers follow in site_data order.

    TIER_ORDER used to be a gate: a tier not named there dumped its papers into
    an "Other" bucket that emitted no DOI. It is now a sequence override only.
    A paper with no tier cannot be placed and is reported rather than dropped.
    """
    missing = [p["slug"] for p in papers if not p.get("tier")]
    if missing:
        sys.exit(
            f"FAIL  papers with no tier: {', '.join(missing)}\n"
            f"      A paper with no tier cannot be placed in llms.txt.\n"
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
                    f"FAIL  {slug}: declares pdf_file '{pdf_file}'\n"
                    f"      not on disk at {root / 'pdf' / pdf_file}\n"
                    f"      A declared artifact that is absent is a defect, not a false flag.\n"
                    f"      Adjudicate. Do not override."
                )
        else:
            on_disk = False
        if p.get("pdf") != on_disk:
            drift.append(f"  pdf   {slug:26s} yaml={str(p.get('pdf')):5s} -> disk={on_disk}")
        p["pdf"] = on_disk
    return drift


def live_backlog(d):
    """Deposited DOIs with no entry built yet. Auto-prunes when a paper ships.

    Backlog entries may be a bare DOI string or a mapping carrying one. Anything
    else is reported, not guessed — a wrong count here is how this sat at 27
    across twenty-four shipped papers.
    """
    shipped = {p.get("doi") for p in built_papers(d)}
    out = []
    for item in d.get("backlog", []):
        if isinstance(item, str):
            doi = item
        elif isinstance(item, dict) and "doi" in item:
            doi = item["doi"]
        else:
            sys.exit(
                f"FAIL  backlog entry shape not recognized: {item!r}\n"
                f"      Expected a DOI string, or a mapping with a 'doi' key.\n"
                f"      Paste the backlog block rather than widening this guess."
            )
        if doi not in shipped:
            out.append(doi)
    return out


RE_ENV_TIER = re.compile(r'^TIER="([^"]*)"', re.M)


def check_tier_envs(d):
    """One paper's tier is written in up to three places: site_data `tier`
    (grouping — llms.txt section, JSON-LD series), site_data `tier_label`
    (display badge, OPTIONAL, defaults to tier), and the env's TIER (what the
    read-page build actually renders). They are different facts that must
    agree by rule: env TIER == tier_label-or-tier, and a tier_label must share
    tier's leading "Tier N" token. This is the drift class that cost
    how_minds_resolve its DOI in llms.txt for weeks — one field, two jobs,
    nothing comparing them. Fail loud; adjudicate; do not default."""
    errs = []
    for p in built_papers(d):
        tier = p.get("tier", "")
        label = p.get("tier_label", tier)
        if p.get("tier_label"):
            t_tok = " ".join(tier.split()[:2])
            l_tok = " ".join(label.split()[:2])
            if t_tok != l_tok:
                errs.append(f"{p['slug']}: tier_label {label!r} does not share "
                            f"tier's leading token {t_tok!r}")
        env = Path(f"tools/{p['slug']}.env")
        if not env.exists():
            continue
        m = RE_ENV_TIER.search(env.read_text())
        if not m:
            errs.append(f"{p['slug']}: env exists but declares no TIER")
        elif m.group(1) != label:
            errs.append(f"{p['slug']}: env TIER {m.group(1)!r} != site_data "
                        f"tier_label-or-tier {label!r}")
    if errs:
        sys.exit("FAIL  tier records disagree:\n      "
                 + "\n      ".join(errs)
                 + "\n      Edit site_data (the source), then sync the env to match."
                 + "\n      Do not default.")


def sync_flags(path, d):
    """Line-level flag write-back. A pyyaml round-trip would eat the Sync Law comment."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    want = {p["slug"]: {"read": p["read"], "pdf": p["pdf"]} for p in d.get("papers", [])}
    cur, n = None, 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*-\s+slug:\s*(\S+)\s*$", ln)
        if m:
            cur = m.group(1)
            continue
        if cur not in want:
            continue
        for field in ("read", "pdf"):
            m2 = re.match(r"^(\s*)" + field + r":\s*(true|false)\s*$", ln)
            if m2:
                new = "true" if want[cur][field] else "false"
                if m2.group(2) != new:
                    lines[i] = f"{m2.group(1)}{field}: {new}"
                    n += 1
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return n


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

    # Every tier, its own section, one emit path. No leftover bucket.
    for tier in tier_sequence(papers):
        group = [p for p in papers if p.get("tier") == tier]
        L.append(f"## {tier}")
        L.append("")
        for p in group:
            L.append(paper_line(p, base))
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
                    help="Print outputs and a summary; write nothing. Wins over --sync-flags.")
    ap.add_argument("--sync-flags", action="store_true",
                    help="Persist derived read/pdf flags back into the yaml.")
    a = ap.parse_args()

    d = load(a.data)

    check_tier_envs(d)
    drift = resolve_state(d, a.out)
    if drift:
        print(f"flag drift — disk is authoritative ({len(drift)} corrected):")
        for line in drift:
            print(line)
        print()

    sm = build_sitemap(d)
    lm = build_llms(d)

    papers = built_papers(d)
    reads = [p for p in papers if p.get("read")]
    n_urls = len(d.get("pages", [])) + len(papers) + len(reads)

    print(f"pages          : {len(d.get('pages', []))}")
    print(f"papers built   : {len(papers)}")
    print(f"read pages     : {len(reads)}")
    print(f"sitemap URLs   : {n_urls}")
    print(f"phase-1 backlog: {len(live_backlog(d))} live DOIs with no page yet")

    if a.check:
        if a.sync_flags and drift:
            print(f"\n--check wins: would sync {len(drift)} flag(s), wrote nothing")
        return 0

    if a.sync_flags:
        n = sync_flags(a.data, d)
        print(f"synced {n} flag(s) into {a.data}")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sitemap.xml").write_text(sm, encoding="utf-8")
    (out / "llms.txt").write_text(lm, encoding="utf-8")
    print(f"\nwrote {out/'sitemap.xml'}  ({n_urls} URLs)")
    print(f"wrote {out/'llms.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
