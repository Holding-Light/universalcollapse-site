#!/usr/bin/env python3
"""
patch_landings.py — bring the 16 older landings up to the kernel_first pattern.

WHAT CHANGES, per landing:
  1. CTA row: the single off-site button becomes
        Read →            -> /read/{slug}          (local; the page built this session)
        Download PDF      -> /pdf/{file}           (only where the PDF actually exists)
  2. The PhilArchive link is NOT deleted — it moves down into the cite-box as an
     "Archival record: PhilArchive · OSF" line, matching kernel_first exactly.
  3. target="_blank" drops off the CTA (internal link now).

WHY: kernel_first is the only landing built to the current model. The other 16
predate the read pages and send readers off-site as their primary action. The
registry's routing principle ("website -> PhilArchive") was written when local
read pages did not exist; kernel_first already departs from it.

SAFETY:
  - dry-run by default; --apply writes and leaves .bak files
  - idempotent: any page already carrying a /read/ CTA is skipped
  - refuses a page whose structure doesn't match, rather than guessing
  - touches ONLY the cta-row and the cite-box. The authored prose is not read,
    not matched, not rewritten.

    python3 tools/patch_landings.py
    python3 tools/patch_landings.py --apply
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUBLIC = Path("public")

RE_CTA = re.compile(r'<div class="cta-row">.*?</div>', re.S)
# insertion point: end of the paragraph carrying the DOI link inside the cite-box
RE_DOI_P = re.compile(
    r'(<a class="cite-doi" href="https://doi\.org/[^"]*"[^>]*>.*?</a>\s*</p>)', re.S)
RE_ARCHIVAL = re.compile(r'<p class="cite-text"[^>]*>Archival record:', re.S)


def pdf_for(slug, pdfs):
    """Match a PDF to a slug conservatively. Only 2 exist today."""
    keys = {"kernel_first": "Kernel_First", "wp01": "WP01"}
    k = keys.get(slug)
    if not k:
        return None
    for p in pdfs:
        if k.lower() in p.lower():
            return p
    return None


def build_cta(slug, pdf):
    lines = [f'      <div class="cta-row">',
             f'        <a class="cta cta-primary" href="/read/{slug}">Read &rarr;</a>']
    if pdf:
        lines.append(f'        <a class="cta cta-secondary" href="/pdf/{pdf}">Download PDF</a>')
    lines.append(f'      </div>')
    return "\n".join(lines)


def build_archival(paper):
    doi = paper["doi"]
    parts = []
    if paper.get("philarchive"):
        parts.append(f'<a class="cite-doi" href="https://philarchive.org/rec/'
                     f'{paper["philarchive"]}" target="_blank" rel="noopener">PhilArchive</a>')
    parts.append(f'<a class="cite-doi" href="https://osf.io/{doi.lower()}/" '
                 f'target="_blank" rel="noopener">OSF</a>')
    return ('<p class="cite-text" style="margin-top:0.75rem;">Archival record: '
            + " &middot; ".join(parts) + '</p>')


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    pdfs = sorted(p.name for p in (PUBLIC / "pdf").glob("*.pdf"))

    changed = skipped = refused = 0
    for paper in d["papers"]:
        slug = paper["slug"]
        f = PUBLIC / f"{slug}.html"
        if not f.exists():
            print(f"  MISSING  {slug}.html"); refused += 1; continue

        s = f.read_text(encoding="utf-8")
        m_cta = RE_CTA.search(s)
        if not m_cta:
            print(f"  REFUSE   {slug:<18} no cta-row found — structure differs, not touching")
            refused += 1
            continue
        if f'/read/{slug}' in m_cta.group(0):
            print(f"  skip     {slug:<18} already has a local Read link")
            skipped += 1
            continue

        old_cta = m_cta.group(0)
        pdf = pdf_for(slug, pdfs)
        new_cta = build_cta(slug, pdf)
        out = s[:m_cta.start()] + new_cta + s[m_cta.end():]

        # move the archival links into the cite-box, if not already there
        note = ""
        if RE_ARCHIVAL.search(out):
            note = " (archival line already present)"
        else:
            m_doi = RE_DOI_P.search(out)
            if not m_doi:
                print(f"  REFUSE   {slug:<18} cite-box DOI paragraph not found — not touching")
                refused += 1
                continue
            arch = build_archival(paper)
            out = out[:m_doi.end()] + "\n        " + arch + out[m_doi.end():]

        lost = re.findall(r'href="(https://philarchive[^"]*)"', old_cta)
        kept = all(l in out for l in lost)
        if not kept:
            print(f"  REFUSE   {slug:<18} would drop {lost} — not touching")
            refused += 1
            continue

        pdfnote = f" +PDF" if pdf else ""
        print(f"  patch    {slug:<18} Read →{pdfnote}{note}")
        changed += 1
        if apply:
            f.with_suffix(".html.bak").write_text(s, encoding="utf-8")
            f.write_text(out, encoding="utf-8")

    print(f"\n  {changed} to patch, {skipped} already done, {refused} refused")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
    else:
        print("  .bak files written beside each patched page")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
