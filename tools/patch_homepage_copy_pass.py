#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_homepage_copy_pass.py - the COPY commit of the 2026-07-27 section pass.

Prose only. Hero, framework, book, about, and the meta description. Leaves the
corpus block and the AI section untouched - those are the structure commit,
which re-harvests fingerprints after this one lands.

Touches ONE file: public/index.html.
Never touches: public/architecture.html, public/read/*, sitemap/llms/library.json,
site_data.yaml. No page added, no URL moved, no link added or removed.
Counts must not move: 4 / 44 / 41 / 90, backlog 6, 88 pages - 0 errors, 6 warnings.

Anchors harvested at 044faa6 on 2026-07-27. The About block is replaced by
RANGE against a slice fingerprint, so the operator's prose never entered chat.

Usage
  python3 tools/patch_homepage_copy_pass.py            # dry run (default)
  python3 tools/patch_homepage_copy_pass.py --apply
  python3 tools/patch_homepage_copy_pass.py --ignore-fingerprints
Exit codes: 0 ok / nothing to do . 2 gate failure . 3 fingerprint drift
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

INDEX = "public/index.html"
APPLIED_MARKER = '<div class="hero-kernel">'
FORBIDDEN = ("C_K", "C<sub>K", "C\u2096")
TRIPLET = ("Constraint shapes collapse. Collapse writes records. "
           "Records update constraints.")

CSS_HERO = """    .hero-kernel {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-family: var(--serif);
      font-size: 1.15rem;
      line-height: 1.5;
      color: var(--text-primary);
      margin: 0 0 1.5rem;
    }

"""

CARD_LINKS_ANCHOR = """    .card-links {
      display: flex;
      flex-wrap: wrap;
      gap: 1.25rem;
      margin-top: 0.9rem;
    }
"""

ABOUT_BLOCK = (
    '  <!-- About -->\n'
    '  <section id="about">\n'
    '    <div class="container">\n'
    '      <div class="reveal">\n'
    '        <div class="section-label">About</div>\n'
    '        <h2 class="section-heading">The Project</h2>\n'
    '        <div class="about-content">\n'
    '          <p class="section-text">\n'
    '            Universal Collapse Theory investigates whether physics, biology, and\n'
    '            mind share one structural relation \u2014 constraints narrow what can\n'
    '            happen, what happens leaves a record, and those records shift the\n'
    '            constraints on what happens next \u2014 without reducing any of them to the\n'
    '            others. It is an independent research program developed by Jeremy C.\n'
    '            Jones and published through HoldingLight LLC.\n'
    '          </p>\n'
    '          <p class="section-text">\n'
    '            The project began as a philosophical inquiry into the limits of what an\n'
    '            observer can claim about reality. From that starting point, it grew into\n'
    '            a layered, open-access body of work rather than a single text.\n'
    '            Foundational papers define and formalize the kernel; interpretive and\n'
    '            domain papers develop its implications; empirical studies test selected\n'
    '            signatures; and program standards govern how claims are recorded,\n'
    '            challenged, revised, or retired.\n'
    '          </p>\n'
    '          <p class="section-text">\n'
    '            UCT remains unfinished by design. Its definitions, claims, and\n'
    '            architecture are expected to change when evidence or argument requires\n'
    '            it. The program is built to be tested, not only argued for.\n'
    '          </p>\n'
    '          <p class="section-text">\n'
    '            This is open, living scholarship. Critique, replication, and\n'
    '            disagreement are welcome \u2014 the falsification standards exist so that\n'
    '            disagreement has somewhere specific to land.\n'
    '          </p>\n'
    '        </div>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
    '\n'
    '  <div class="container"><hr class="section-rule"></div>\n'
    '\n'
)

RANGES = [
    dict(
        id="R1-about",
        start=772, end=800,
        sha="fafd96f3cc78b50180a0d1ac964f1b240a331706404363546b8c7d8a431cf513",
        first="  <!-- About -->\n",
        last="\n",
        must_contain=[('<section id="about">', 1),
                      ('<div class="section-label">About</div>', 1),
                      ('The Project', 1),
                      ('about-content', 1),
                      ('href=', 0)],
        new=ABOUT_BLOCK,
        why="About rewritten: program speaks first, kernel described not named",
    ),
]

EDITS = [
    dict(
        id="E1-meta-description",
        why="retrieval surface must not drift from the hero",
        old=('content="Universal Collapse Theory \u2014 a coherence-first structural framework '
             'for a reality that is still resolving. ' + TRIPLET + '"'),
        new=('content="Universal Collapse Theory \u2014 a coherence-first research program. '
             'An attempt to understand a reality that is still resolving. ' + TRIPLET + '"'),
    ),
    dict(
        id="E2-hero-css",
        why="the only new CSS: stacked kernel lines",
        old=CARD_LINKS_ANCHOR,
        new=CSS_HERO + CARD_LINKS_ANCHOR,
    ),
    dict(
        id="E3-hero-copy",
        why="subtitle, triplet split to three lines, closer",
        old=("        A coherence-first structural framework for a reality that is still "
             "resolving. " + TRIPLET + " Whether that pattern holds everywhere structure "
             "emerges is what this program is built to test."),
        new=("        An attempt to understand a reality that is still resolving.\n"
             "      </p>\n"
             '      <div class="hero-kernel">\n'
             "        <span>Constraint shapes collapse.</span>\n"
             "        <span>Collapse writes records.</span>\n"
             "        <span>Records update constraints.</span>\n"
             "      </div>\n"
             '      <p class="hero-subtitle">\n'
             "        UCT is built to test whether this pattern recurs wherever structure "
             "emerges \u2014 where it holds, where it fails, and where its reach ends."),
    ),
    dict(
        id="E4-framework-p1a",
        why="Law of Coherence dropped from the opening; 'every domain' overreach removed",
        old=("begins with a single structural proposal \u2014 the Law of Coherence \u2014 and "
             "follows its implications across every domain of inquiry."),
        new="begins with a single structural proposal and follows it as far as it will go.",
    ),
    dict(
        id="E5-framework-p1b",
        why="loop stated plainly here; the hero states it formally",
        old=("constraint shapes how possibility collapses into form, collapse writes "
             "records, and those records update the constraints that govern what happens "
             "next."),
        new=("constraints narrow what can happen, what actually happens leaves a record, "
             "and those records shift the constraints on what happens next."),
    ),
    dict(
        id="E6-framework-p2",
        why="three conditions named and glossed; the awarded name removed",
        old=(" That loop is the proposal under test, from quantum measurement to cellular "
             "regulation to conscious experience. The question is whether it is portable, "
             "discriminating, and corrigible enough to warrant treatment as a Law of "
             "Coherence."),
        new=("\n        </p>\n"
             '        <p class="section-text">\n'
             "          That loop is what's under test, from quantum measurement to "
             "cellular regulation to conscious experience. The test has three conditions: "
             "portable enough to cross domains without being retuned for each one, "
             "discriminating enough to rule cases out, and corrigible enough to be "
             "corrected by what it gets wrong."),
    ),
    dict(
        id="E7-framework-p3",
        why="'seeing why' presupposed the recurrence that is the open question",
        old=("a way of seeing why the same pattern of collapse, persistence, and renewal "
             "recurs across scales usually studied in isolation."),
        new=("a way of asking whether the same pattern of collapse, persistence, and "
             "renewal recurs across scales usually studied in isolation, and where it "
             "does, why."),
    ),
    dict(
        id="E8-book-heading",
        why="the book is the origin, not a repackaging",
        old='<h2 class="section-heading">The same framework, as one continuous read.</h2>',
        new='<h2 class="section-heading">The originating vision, as one continuous read.</h2>',
    ),
    dict(
        id="E9-book-copy",
        why="provenance corrected; the program grew out of the book",
        old=("          The papers above are open access and permanently archived &mdash; that is\n"
             "          where the program lives. <em>Universal Collapse</em> is the book-length\n"
             "          treatment for anyone who would rather have it start to finish, in a single\n"
             "          volume, than paper by paper."),
        new=("          <em>Universal Collapse</em> is the book-length presentation from which\n"
             "          the formal research program grew. Written for the general reader, it\n"
             "          follows the ideas across cosmos, life, mind, meaning, and faith."),
    ),
]

POST = [
    ("A Coherence-First Research Program", "==", 2),
    ("not a Theory of Everything", "==", 1),
    ("a way of asking whether", "==", 1),
    (TRIPLET, "==", 1),
    ('class="strip reveal"', "==", 2),
    ("Law of Coherence", "==", 0),
    ("An attempt to understand a reality that is still resolving.", "==", 2),
    ('<div class="hero-kernel">', "==", 1),
    ("<span>Constraint shapes collapse.</span>", "==", 1),
    ('<p class="hero-subtitle">', "==", 2),
    ("The originating vision, as one continuous read.", "==", 1),
    ("the falsification standards exist so that", "==", 1),
    ('id="papers"', "==", 1),
    ('id="about"', "==", 1),
    ('class="paper-card"', "==", 4),
    ('class="paper-card is-static"', "==", 4),
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


def clip(s, n=104):
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + " ..."


def main():
    ap = argparse.ArgumentParser(description="Copy commit (dry run by default).")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ignore-fingerprints", action="store_true")
    args = ap.parse_args()

    print("patch_homepage_copy_pass - " + ("APPLY" if args.apply else "DRY RUN"))
    print("=" * 72)

    if not Path("tools").is_dir() or not Path(INDEX).exists():
        die(2, "not at repo root", "cd ~/universalcollapse-site && python3 tools/patch_homepage_copy_pass.py")

    for blob in [ABOUT_BLOCK, CSS_HERO] + [e["new"] for e in EDITS]:
        for bad in FORBIDDEN:
            if bad in blob:
                die(2, "new markup contains forbidden notation %r" % bad, "see CLAUDE.md Sec 3")
    print("self-check      : clean, %d range + %d edits" % (len(RANGES), len(EDITS)))

    text = read(INDEX)
    if APPLIED_MARKER in text:
        print("-" * 72)
        print("nothing to do - already applied. No write.")
        sys.exit(0)

    lines = text.splitlines(keepends=True)
    print("file            : %d lines" % len(lines))

    for r in RANGES:
        if len(lines) < r["end"]:
            die(2, "file shorter than range %s" % r["id"], "re-harvest the line map")
        sl = "".join(lines[r["start"] - 1:r["end"]])
        got = hashlib.sha256(sl.encode("utf-8")).hexdigest()
        okf = lines[r["start"] - 1] == r["first"]
        okl = lines[r["end"] - 1] == r["last"]
        print("range %-10s %d-%d  sha %s  bounds %s/%s"
              % (r["id"], r["start"], r["end"],
                 "match" if got == r["sha"] else "DRIFT",
                 "ok" if okf else "BAD", "ok" if okl else "BAD"))
        if not (okf and okl):
            print("    line %d = %r" % (r["start"], clip(lines[r["start"] - 1])))
            print("    line %d = %r" % (r["end"], clip(lines[r["end"] - 1])))
            die(2, "range boundary mismatch", "re-harvest Q1/Q2 and rebuild")
        if got != r["sha"]:
            print("    harvested %s\n    on disk   %s" % (r["sha"], got))
            if not args.ignore_fingerprints:
                die(3, "About slice changed since harvest",
                    "sed -n '%d,%dp' %s | shasum -a 256" % (r["start"], r["end"], INDEX))
        for needle, n in r["must_contain"]:
            c = sl.count(needle)
            print("    contains %-38s %d (want %d)" % (clip(needle, 38), c, n))
            if c != n:
                die(2, "range %s content check failed" % r["id"],
                    "the slice is not the block this patcher was built for")

    print("-" * 72)
    for e in EDITS:
        c = text.count(e["old"])
        print("%-20s anchors=%d  %s" % (e["id"], c, e["why"]))
        if c != 1:
            die(2, "anchor for %s resolves %d times, want 1" % (e["id"], c),
                "re-harvest that anchor and rebuild; do not force")

    if not args.apply:
        print("-" * 72)
        print("DRY RUN - nothing written. Re-run with --apply.")
        sys.exit(0)

    for r in sorted(RANGES, key=lambda x: -x["start"]):
        lines = lines[:r["start"] - 1] + [r["new"]] + lines[r["end"]:]
    out = "".join(lines)
    for e in EDITS:
        if out.count(e["old"]) != 1:
            die(2, "anchor count changed mid-run for %s" % e["id"], "git checkout -- " + INDEX)
        out = out.replace(e["old"], e["new"], 1)
    write(INDEX, out)
    print("wrote           : " + INDEX)

    after = read(INDEX)
    fails = []
    for needle, op, n in POST:
        got = after.count(needle)
        if not ((got == n) if op == "==" else (got >= n)):
            fails.append("%r %s %d, got %d" % (clip(needle, 44), op, n, got))
    if after.count("<section") != after.count("</section>"):
        fails.append("section tags unbalanced: %d/%d"
                     % (after.count("<section"), after.count("</section>")))
    if after.count("href=") != text.count("href="):
        fails.append("href count moved: %d -> %d (copy commit adds and removes none)"
                     % (text.count("href="), after.count("href=")))
    for bad in FORBIDDEN:
        if bad in after and bad not in text:
            fails.append("introduced forbidden notation %r" % bad)
    if fails:
        for f in fails:
            print("  POST FAIL  " + f)
        die(2, "%d post-condition(s) failed - written but unverified" % len(fails),
            "git checkout -- " + INDEX + "   (git is the backup)")

    print("post-conditions : %d checks pass; hrefs unchanged at %d; sections balanced"
          % (len(POST) + 3, after.count("href=")))
    print("=" * 72)
    print("Next: lint, render-verify, commit, push. Then RE-HARVEST the section")
    print("fingerprints - every line number below the hero has moved.")


if __name__ == "__main__":
    main()
