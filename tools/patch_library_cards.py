#!/usr/bin/env python3
"""
patch_library_cards.py — add the 5 deposits that are absent from the library.

FOUND BY status.py, not by memory: the backlog lists 27 DOIs, the library routes
only 20 off-site, and 5 live deposits have no card at ALL — no link, no mention.
Four of the five are T1.6. The library's empirical section shows 4 entries; there
are 8 deposits. The empirical wing was half-invisible on its own site.

  92RQ5  How Minds Resolve                       -> Tier 1.5
  2RC4D  Entropy as Record                       -> Tier 1.6
  PNF89  Redundant Record Consensus (Planck PR3)  -> Tier 1.6   (docx says T15; registry
                                                                 says T1.6 — registry wins;
                                                                 the file predates the tier)
  5TG3P  F2 — Training-Layer Positive Control    -> Tier 1.6
  JAEZQ  S3 Positive-Control Calibration         -> Tier 1.6

Card structure copied verbatim from the Rice card. Note the pattern it reveals:
`href` is the destination, `paper-venue` is a LABEL. Rice points at /rice while
still displaying its DOI. So these cards show the DOI and point off-site until a
landing exists; flipping one later is a one-attribute edit.

Descriptions are written from each paper's own abstract, not from recall.

SAFETY: dry-run default; --apply writes .bak; idempotent (skips a DOI already
present); refuses if a section or its grid can't be located.

    python3 tools/patch_library_cards.py
    python3 tools/patch_library_cards.py --apply
"""
import re
import sys
from pathlib import Path

LIB = Path("public/library.html")

CARDS = {
    "Tier 1.5": [
        dict(
            doi="92RQ5", num="T1.5",
            title="How Minds Resolve: The Faith–Reason–Logic–Belief Cycle",
            desc="The mind&rsquo;s resolution loop specified: faith as the opening constraint that "
                 "lets inquiry start, reason as recursive refiner, logic as their lawful union, and "
                 "belief as the stabilized record that feeds the next cycle. Names the failure mode "
                 "too &mdash; when belief supplants faith, the loop closes and no new collapse occurs.",
        ),
    ],
    "Tier 1.6": [
        dict(
            doi="2RC4D", num="T1.6",
            title="Entropy as Record",
            desc="A pre-specified shape test on compiled cosmic entropy estimates: does the total "
                 "entropy curve look like smooth, monotone record-accumulation, or does it demand "
                 "multi-kink complexity? Reported as a shape-consistency finding rather than a "
                 "discriminating test &mdash; and one pre-specified criterion fails, and is reported "
                 "as a failure.",
        ),
        dict(
            doi="PNF89", num="T1.6",
            title="Redundant Record Consensus in Planck PR3 CMB Component Maps",
            desc="The S&#8321; signature against real cosmology: treat four independently "
                 "reconstructed CMB maps as redundant record channels and measure how fast "
                 "disagreement shrinks under aggregation. Convergence is strong and stable across "
                 "seeds &mdash; and is reported explicitly as a record-consensus demonstration, not "
                 "a completed independence audit.",
        ),
        dict(
            doi="5TG3P", num="T1.6",
            title="F2 &mdash; Training-Layer Positive Control",
            desc="Sensitivity, where the negative controls establish specificity. A structural "
                 "grammar is installed into a model by fine-tuning, then counter-trained away under "
                 "matched budget: install &ne; remove. The differential is positive on every seed, "
                 "against a potency-matched content control whose loop spans zero.",
        ),
        dict(
            doi="JAEZQ", num="T1.6",
            title="S&#8323; Positive-Control Calibration",
            desc="The in-session arm of the positive-control family &mdash; planting a record state "
                 "of known ground truth in the channel the operator controls, and measuring "
                 "detection. Companion to F2 at the training layer and S3-RAG-01 at retrieval.",
        ),
    ],
}


def render(c, blank_attrs):
    return f'''
        <a href="https://doi.org/10.17605/OSF.IO/{c['doi']}"{blank_attrs} class="paper-card">
          <span class="paper-number">{c['num']}</span>
          <div class="paper-info">
            <span class="paper-title">{c['title']}</span>
            <span class="paper-desc">{c['desc']}</span>
            <span class="paper-venue">OSF &middot; DOI 10.17605/OSF.IO/{c['doi']}</span>
          </div>
          <span class="paper-arrow">&rarr;</span>
        </a>
'''


def main():
    apply = "--apply" in sys.argv
    if not LIB.exists():
        sys.exit("public/library.html not found — run from the repo root")
    h = LIB.read_text(encoding="utf-8")
    orig = h

    # match the pattern the existing off-site cards use, rather than assume one
    m = re.search(r'<a href="https://doi\.org/[^"]*"([^>]*?)class="paper-card"', h)
    blank_attrs = ""
    if m and "_blank" in m.group(1):
        blank_attrs = ' target="_blank" rel="noopener"'
    print(f"  existing off-site cards use target=_blank: {'yes' if blank_attrs else 'no'} "
          f"— matching that\n")

    added = skipped = 0
    for tier, cards in CARDS.items():
        # locate the section by its label, and bound it at the next section-label
        lab = re.search(rf'<div class="section-label">{re.escape(tier)}[^<]*</div>', h)
        if not lab:
            print(f"  REFUSE  section '{tier}' not found"); return 1
        nxt = re.search(r'<div class="section-label">', h[lab.end():])
        end = lab.end() + (nxt.start() if nxt else len(h) - lab.end())
        section = h[lab.start():end]

        # insert after the LAST card in this section
        last = None
        for mm in re.finditer(r'</a>', section):
            last = mm
        if not last:
            print(f"  REFUSE  no cards found in '{tier}'"); return 1

        ins = ""
        for c in cards:
            if c["doi"] in h:
                print(f"  skip    {c['doi']:<7} {c['title'][:52]} — already present")
                skipped += 1
                continue
            print(f"  ADD     {c['doi']:<7} {c['title'][:52]}  -> {tier}")
            ins += render(c, blank_attrs)
            added += 1
        if ins:
            at = lab.start() + last.end()
            h = h[:at] + ins.rstrip("\n") + h[at:]

    print(f"\n  add {added}   already present {skipped}")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
        return 0
    LIB.with_suffix(".html.bak").write_text(orig, encoding="utf-8")
    LIB.write_text(h, encoding="utf-8")
    print(f"  wrote {LIB}  (.bak beside it)")
    print("  verify:  python3 tools/status.py --library")
    return 0


if __name__ == "__main__":
    sys.exit(main())
