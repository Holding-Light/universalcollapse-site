#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_homepage_restructure.py - Phase 3 of the 2026-07-27 site overhaul.

Publication wall -> four entrances + four bounded domain cards + two strips;
book invitation rehomed below the open-access entrance; WP01 and the
architecture map given a link row at the tail of #framework.

Touches ONE file: public/index.html (authored surface).
Never touches: public/architecture.html (build output), public/read/*,
sitemap.xml / llms.txt / library.json (generated), tools/site_data.yaml.
No page added, no URL moved. Counts must not move: 4 / 44 / 41 / 90,
backlog 6, 88 pages - 0 errors, 6 warnings.

Every anchor, line number, and fingerprint below was harvested from the
operator's repo at 931f1ce on 2026-07-27. The 179-line wall is replaced by
RANGE with a slice fingerprint rather than by exact-match anchor, so the
operator's prose never had to be pasted into a chat session to be edited.

Usage
  python3 tools/patch_homepage_restructure.py                    # dry run (default)
  python3 tools/patch_homepage_restructure.py --apply            # write
  python3 tools/patch_homepage_restructure.py --ignore-fingerprints
Exit codes: 0 ok / nothing to do . 2 gate failure . 3 fingerprint drift
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

INDEX = "public/index.html"
AMZ = "https://www.amazon.com/Universal-Collapse-Jeremy-C-Jones-ebook/dp/B0FJLY71PV"

# Marker of the applied state - present only after this patcher has run.
APPLIED_MARKER = 'class="strip reveal"'

FORBIDDEN = ("C_K", "C<sub>K", "C\u2096")

# ---------------------------------------------------------------- new markup

CSS_BLOCK = """    .card-links {
      display: flex;
      flex-wrap: wrap;
      gap: 1.25rem;
      margin-top: 0.9rem;
    }

    .card-links a {
      font-family: var(--mono);
      font-size: 0.7rem;
      font-weight: 400;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      text-decoration: none;
      color: var(--accent);
      border-bottom: 1px solid var(--rule);
      padding-bottom: 0.2rem;
      transition: border-color 0.3s ease, color 0.3s ease;
    }

    .card-links a:hover {
      border-color: var(--accent);
      color: var(--text-primary);
    }

    .paper-card.is-static {
      cursor: default;
    }

    .paper-card.is-static:hover {
      background: var(--bg-deep);
    }

    .strip {
      font-family: var(--mono);
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-tertiary);
      margin-top: 1.75rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.9rem;
      align-items: baseline;
    }

    .strip a {
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid var(--rule);
      transition: border-color 0.3s ease, color 0.3s ease;
    }

    .strip a:hover {
      border-color: var(--accent);
      color: var(--text-primary);
    }

"""


def entrance(num: str, href: str, title: str, desc: str) -> str:
    return (
        '        <a href="%s" class="paper-card">\n'
        '          <span class="paper-number">%s</span>\n'
        '          <div class="paper-info">\n'
        '            <span class="paper-title">%s</span>\n'
        '            <span class="paper-desc">%s</span>\n'
        '          </div>\n'
        '          <span class="paper-arrow">\u2192</span>\n'
        '        </a>\n\n' % (href, num, title, desc)
    )


def domain(num: str, title: str, desc: str, links: list) -> str:
    rows = "".join('            <a href="%s">%s</a>\n' % (h, lab) for h, lab in links)
    return (
        '        <div class="paper-card is-static">\n'
        '          <span class="paper-number">%s</span>\n'
        '          <div class="paper-info">\n'
        '            <span class="paper-title">%s</span>\n'
        '            <span class="paper-desc">%s</span>\n'
        '            <div class="card-links">\n'
        '%s'
        '            </div>\n'
        '          </div>\n'
        '        </div>\n\n' % (num, title, desc, rows)
    )


NEW_PAPERS = (
    '  <section id="papers">\n'
    '    <div class="container">\n'
    '      <div class="reveal">\n'
    '        <div class="section-label">The Corpus</div>\n'
    '        <h2 class="section-heading">Published Work</h2>\n'
    '        <p class="section-text">\n'
    '          Four entrances into the program, then the work itself, grouped by the\n'
    '          domain it addresses. Every paper is open access and carries a permanent\n'
    '          DOI; the full corpus lives in the Library.\n'
    '        </p>\n'
    '      </div>\n\n'
    '      <div class="papers-grid reveal">\n\n'
    + entrance("01", "/kernel_first", "Start Here",
               "Kernel First: what UCT is and is not, before the white papers &mdash; "
               "collapse as constrained actualization rather than substance.")
    + entrance("02", "#framework", "Understand the Framework",
               "The claim in one screen: the loop under test, and what the program "
               "declines to claim about it.")
    + entrance("03", "/falsification_standards", "Evidence &amp; Status",
               "Failure modes and falsification standards &mdash; the conditions under "
               "which each claim would be abandoned, stated in advance.")
    + entrance("04", "/library", "Explore the Library",
               "The whole corpus with DOIs, reading order, and the relation graph that "
               "connects it.")
    + '      </div>\n\n'
    '      <div class="strip reveal">Also in the gateway arc: '
    '<a href="/faith_without_fideism">Faith Without Fideism \u2192</a></div>\n\n'
    '      <div class="papers-grid reveal" style="margin-top: 3rem;">\n\n'
    + domain("I", "Physics",
             "Constraint shapes how possibility resolves into matter, and what resolves "
             "leaves records that condition what comes next.",
             [("/wp02", "WP02 &mdash; Collapse in Physics"),
              ("/collapse_reframed", "Collapse Reframed"),
              ("/entropy_as_record", "Entropy as Record")])
    + domain("II", "Biology",
             "Living systems resolve under constraint with a memory: records accumulate, "
             "and the accumulated record is what makes the next resolution different.",
             [("/wp03", "WP03 &mdash; Biological Collapse"),
              ("/bfs", "Biological Faith Systems"),
              ("/rice", "Bio Constraint Sweep &mdash; Rice")])
    + domain("III", "Mind",
             "Minds resolve under constraint and write records; the self is what that "
             "record layer builds, not what authors it.",
             [("/self_ego", "Self, the Ego Did Not Build"),
              ("/how_minds_resolve", "How Minds Resolve"),
              ("/cogitate", "COGITATE &mdash; Perceptual Resolution")])
    + domain("IV", "Artificial Intelligence",
             "UCT wasn't built to explain AI. AI is the recursive phase of mind's "
             "externalized record layer &mdash; and the place the kernel's signatures can "
             "be tested directly.",
             [("/cim_foundational", "Consciousness-Induced Material"),
              ("/ai_meaning_layer", "AI in the Meaning Layer"),
              ("/ai_sig_deployed", "S1&ndash;S3 in Deployed AI Systems")])
    + '      </div>\n\n'
    '      <div class="strip reveal">Held to standards: '
    '<a href="/records">Records</a> &middot; '
    '<a href="/soe">Structuralization of Empiricism</a> &middot; '
    '<a href="/uis">Update Integrity</a></div>\n\n'
    '      <div class="card-links reveal" style="margin-top: 3rem;">\n'
    '        <a href="/library">Full library \u2192</a>\n'
    '        <a href="/roadmap/">Reading roadmap \u2192</a>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
)

BOOK_SECTION = (
    '  <!-- The Book -->\n'
    '  <section id="book">\n'
    '    <div class="container">\n'
    '      <div class="reveal">\n'
    '        <div class="section-label">The Book</div>\n'
    '        <h2 class="section-heading">The same framework, as one continuous read.</h2>\n'
    '        <p class="section-text">\n'
    '          The papers above are open access and permanently archived &mdash; that is\n'
    '          where the program lives. <em>Universal Collapse</em> is the book-length\n'
    '          treatment for anyone who would rather have it start to finish, in a single\n'
    '          volume, than paper by paper.\n'
    '        </p>\n'
    '      </div>\n'
    '      <div class="card-links" style="margin-top: 2.5rem;">\n'
    '        <a href="' + AMZ + '" target="_blank" rel="noopener">Get the book \u2192</a>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
    '\n'
    '  <div class="container"><hr class="section-rule"></div>\n'
    '\n'
)

# ---------------------------------------------------------------- edit tables

# Line-range replacements, guarded by slice fingerprint + boundary byte-match.
RANGES = [
    dict(
        id="R1-papers-wall",
        start=569, end=747,
        sha="80cf9ee2b079fa23ae4d514dabb5d3dc90b0f3e3e3e2573cfc1e4378abaeec48",
        first='  <section id="papers">\n',
        last='  </section>\n',
        must_contain=[('<span class="paper-number">BOOK</span>', 1),
                      ('class="paper-card"', 18)],
        new=NEW_PAPERS,
        why="the 179-line publication wall -> entrances + domains + strips",
    ),
]

# Exact-match string edits, applied after the range (anchors are position-free).
EDITS = [
    dict(
        id="E1-hero-cta",
        why="Amazon link leaves the hero (rehomed to #book); label -> Start Here",
        old=('        <a href="' + AMZ + '" target="_blank" rel="noopener">Get the Book</a>\n'
             '        <a href="#papers">Read the Papers</a>\n'),
        new='        <a href="#papers">Start Here</a>\n',
    ),
    dict(
        id="E2-framework-links",
        why="WP01 keeps its homepage link; architecture map keeps its presence",
        old=("recurs across scales usually studied in isolation.\n"
             "        </p>\n"
             "      </div>\n"
             "    </div>\n"
             "  </section>"),
        new=("recurs across scales usually studied in isolation.\n"
             "        </p>\n"
             "      </div>\n"
             '      <div class="card-links" style="margin-top: 2.5rem;">\n'
             '        <a href="/wp01">Formalized in WP01 \u2192</a>\n'
             '        <a href="/architecture">Full program architecture \u2192</a>\n'
             "      </div>\n"
             "    </div>\n"
             "  </section>"),
    ),
    dict(
        id="E3-book-section",
        why="book invitation below the open-access entrance, not above it",
        old="  <!-- About -->\n",
        marker='<section id="book">',
        new=BOOK_SECTION + "  <!-- About -->\n",
    ),
    dict(
        id="E4-css",
        why="card-links / strip / is-static - the only new CSS",
        old=("    .paper-card:hover .paper-arrow {\n"
             "      color: var(--accent);\n"
             "      transform: translateX(4px);\n"
             "    }\n"
             "\n"
             "    /* --- About --- */"),
        new=("    .paper-card:hover .paper-arrow {\n"
             "      color: var(--accent);\n"
             "      transform: translateX(4px);\n"
             "    }\n"
             "\n"
             + CSS_BLOCK
             + "    /* --- About --- */"),
    ),
]

KEEP = ["/kernel_first", "/faith_without_fideism", "/falsification_standards", "/wp01",
        "/wp02", "/collapse_reframed", "/entropy_as_record", "/wp03", "/bfs", "/rice",
        "/self_ego", "/how_minds_resolve", "/cogitate", "/cim_foundational",
        "/ai_meaning_layer", "/ai_sig_deployed", "/records", "/soe", "/uis",
        "/library", "/roadmap/", "/architecture"]

DROP = ["/schrodinger", "/ai_synthetic", "/soai"]

POST = [
    ('id="papers"', "==", 1),
    ('<section id="book">', "==", 1),
    ("<!-- About -->", "==", 1),
    ('class="paper-card"', "==", 4),          # the four entrances
    ('class="paper-card is-static"', "==", 4),  # the four domains
    ('<span class="paper-number">BOOK</span>', "==", 0),
    (">Get the Book</a>", "==", 0),
    (AMZ, "==", 1),
    ('<a href="#papers">', ">=", 1),
    ('class="papers-grid', "==", 2),
    ("A Coherence-First Research Program", "==", 2),  # Phase 1 must survive
]


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def die(code, msg, remedy):
    print("\n  GATE FAILED: " + msg)
    print("  REMEDY: " + remedy + "\n")
    sys.exit(code)


def clip(s, n=110):
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + " ..."


def main():
    ap = argparse.ArgumentParser(description="Phase 3 homepage restructure (dry run by default).")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--ignore-fingerprints", action="store_true",
                    help="proceed despite a slice fingerprint mismatch (do not default to this)")
    args = ap.parse_args()

    print("patch_homepage_restructure - " + ("APPLY" if args.apply else "DRY RUN"))
    print("=" * 72)

    if not Path("tools").is_dir() or not Path(INDEX).exists():
        die(2, "not at repo root", "cd ~/universalcollapse-site && python3 tools/patch_homepage_restructure.py")

    for blob in [NEW_PAPERS, BOOK_SECTION, CSS_BLOCK] + [e["new"] for e in EDITS]:
        for bad in FORBIDDEN:
            if bad in blob:
                die(2, "new markup contains forbidden notation %r" % bad,
                    "the collapse operator is C^K_t; see CLAUDE.md Sec 3")
    print("self-check      : new markup clean, %d range(s) + %d edit(s)" % (len(RANGES), len(EDITS)))

    text = read(INDEX)

    if APPLIED_MARKER in text:
        print("-" * 72)
        print("nothing to do - already applied (%r present). No write." % APPLIED_MARKER)
        sys.exit(0)

    lines = text.splitlines(keepends=True)
    print("file            : %d lines" % len(lines))

    # --- gate: range fingerprints + boundary byte-match --------------------
    for r in RANGES:
        if len(lines) < r["end"]:
            die(2, "file is shorter than range %s" % r["id"], "re-harvest the line map")
        sl = "".join(lines[r["start"] - 1:r["end"]])
        got = hashlib.sha256(sl.encode("utf-8")).hexdigest()
        okfirst = lines[r["start"] - 1] == r["first"]
        oklast = lines[r["end"] - 1] == r["last"]
        print("range %-14s %d-%d  sha %s  bounds %s/%s"
              % (r["id"], r["start"], r["end"],
                 "match" if got == r["sha"] else "DRIFT",
                 "ok" if okfirst else "BAD", "ok" if oklast else "BAD"))
        if not (okfirst and oklast):
            print("    line %d = %r" % (r["start"], clip(lines[r["start"] - 1])))
            print("    line %d = %r" % (r["end"], clip(lines[r["end"] - 1])))
            die(2, "range boundary does not byte-match the harvest",
                "re-run the N3 harvest and rebuild this patcher from the pasted bytes")
        if got != r["sha"]:
            print("    harvested %s\n    on disk   %s" % (r["sha"], got))
            if not args.ignore_fingerprints:
                die(3, "the slice changed since the 2026-07-27 harvest",
                    "re-harvest: sed -n '%d,%dp' %s | shasum -a 256"
                    % (r["start"], r["end"], INDEX))
        for needle, n in r["must_contain"]:
            c = sl.count(needle)
            print("    contains %-42s %d (want %d)" % (clip(needle, 42), c, n))
            if c != n:
                die(2, "range %s content check failed" % r["id"],
                    "the slice is not the wall this patcher was built for; re-harvest")

    # --- gate: every string anchor resolves exactly once -------------------
    print("-" * 72)
    for e in EDITS:
        c = text.count(e["old"])
        print("%-18s anchors=%d  %s" % (e["id"], c, e["why"]))
        if c != 1:
            die(2, "anchor for %s resolves %d times, want 1" % (e["id"], c),
                "re-harvest that anchor and rebuild from the pasted bytes; do not force")

    if not args.apply:
        print("-" * 72)
        print("DRY RUN - nothing written. Re-run with --apply when the prose is approved.")
        sys.exit(0)

    # --- apply: ranges first (line-indexed), then anchors ------------------
    for r in sorted(RANGES, key=lambda x: -x["start"]):
        lines = lines[:r["start"] - 1] + [r["new"]] + lines[r["end"]:]
    out = "".join(lines)

    for e in EDITS:
        if out.count(e["old"]) != 1:
            die(2, "anchor count changed mid-run for %s" % e["id"],
                "git checkout -- " + INDEX)
        out = out.replace(e["old"], e["new"], 1)

    write(INDEX, out)
    print("wrote           : " + INDEX)

    # --- post-conditions ---------------------------------------------------
    after = read(INDEX)
    fails = []
    for needle, op, n in POST:
        got = after.count(needle)
        if not ((got == n) if op == "==" else (got >= n)):
            fails.append("%r %s %d, got %d" % (clip(needle, 46), op, n, got))
    for slug in KEEP:
        if ('href="%s"' % slug) not in after:
            fails.append("lost link: %s" % slug)
    for slug in DROP:
        if ('href="%s"' % slug) in after:
            fails.append("should have dropped: %s" % slug)
    for bad in FORBIDDEN:
        if bad in after and bad not in text:
            fails.append("introduced forbidden notation %r" % bad)
    if after.count("<section") != after.count("</section>"):
        fails.append("section tags unbalanced: %d open, %d close"
                     % (after.count("<section"), after.count("</section>")))

    if fails:
        for f in fails:
            print("  POST FAIL  " + f)
        die(2, "%d post-condition(s) failed - file written but unverified" % len(fails),
            "git checkout -- " + INDEX + "   (git is the backup)")

    kept = sum(1 for s in KEEP if ('href="%s"' % s) in after)
    print("post-conditions : %d checks pass; %d/%d links kept, %d dropped as approved"
          % (len(POST) + len(KEEP) + len(DROP) + 2, kept, len(KEEP), len(DROP)))
    print("=" * 72)
    print("Next: build_site_meta --check, lint_doi_shadow, uct_lint_html (full form),")
    print("render-verify the page, then commit + push. Counts must not move.")


if __name__ == "__main__":
    main()
