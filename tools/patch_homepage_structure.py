#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_homepage_structure.py - the STRUCTURE commit of the 2026-07-27 section pass.

Two moves, one file:
  1. The corpus block is rebuilt. Entrances 02/03/04 are cut (all three pointed
     backward or sideways); card 0 is the gateway, numbered for its actual tier.
     Domain cards become open questions rather than restatements of the loop.
     Three strips: orientation, standards, falsification. `/program_map` gains
     its first homepage link.
  2. The AI section moves from position 3 to position 5 - after the corpus,
     before the book - and is rewritten. AIP leaves the homepage entirely.

Touches ONE file: public/index.html.
Never touches: public/architecture.html, public/read/*, sitemap/llms/library.json,
site_data.yaml. No page added, no URL moved.
Counts must not move: 4 / 44 / 41 / 90, backlog 6, 88 pages - 0 errors, 6 warnings.

Line map and fingerprints harvested at e5ae4f4 on 2026-07-27.

Usage
  python3 tools/patch_homepage_structure.py            # dry run (default)
  python3 tools/patch_homepage_structure.py --apply
  python3 tools/patch_homepage_structure.py --ignore-fingerprints
Exit codes: 0 ok / nothing to do . 2 gate failure . 3 fingerprint drift
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

INDEX = "public/index.html"
APPLIED_MARKER = 'Where the loop is being tested.'
FORBIDDEN = ("C_K", "C<sub>K", "C\u2096")
RULE = '  <div class="container"><hr class="section-rule"></div>\n'


def domain(num, title, question, links):
    rows = "".join('              <a href="%s">%s</a>\n' % (h, lab) for h, lab in links)
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
        '        </div>\n\n' % (num, title, question, rows)
    )


NEW_PAPERS = (
    '  <!-- Papers -->\n'
    '  <section id="papers">\n'
    '    <div class="container">\n'
    '      <div class="reveal">\n'
    '        <div class="section-label">The Corpus</div>\n'
    '        <h2 class="section-heading">Where the loop is being tested.</h2>\n'
    '        <p class="section-text">\n'
    '          Each domain card names three papers: an anchor that states the position,\n'
    '          a bridge that carries it into that domain\'s own vocabulary, and an\n'
    '          empirical result that tests it.\n'
    '        </p>\n'
    '      </div>\n\n'
    '      <div class="papers-grid reveal">\n\n'
    '        <a href="/kernel_first" class="paper-card">\n'
    '          <span class="paper-number">0</span>\n'
    '          <div class="paper-info">\n'
    '            <span class="paper-title">Start Here</span>\n'
    '            <span class="paper-desc">Kernel First \u2014 how to read the framework: '
    'what UCT is and is not, before the white papers.</span>\n'
    '          </div>\n'
    '          <span class="paper-arrow">\u2192</span>\n'
    '        </a>\n\n'
    '      </div>\n\n'
    '      <div class="strip reveal">Where to start: '
    '<a href="/roadmap/">Reading Roadmap \u2192</a> &middot; What the program is: '
    '<a href="/program_map">Program Map \u2192</a> &middot; Also in the gateway arc: '
    '<a href="/faith_without_fideism">Faith Without Fideism \u2192</a></div>\n\n'
    '      <div class="papers-grid reveal" style="margin-top: 3rem;">\n\n'
    + domain("I", "Physics",
             "Whether records are physical, and whether a measurement outcome is one.",
             [("/wp02", "WP02 \u2014 Collapse in Physics"),
              ("/collapse_reframed", "Collapse Reframed"),
              ("/entropy_as_record", "Entropy as Record")])
    + domain("II", "Biology",
             "Whether accumulated records, not just present constraints, are what make "
             "the next resolution different.",
             [("/wp03", "WP03 \u2014 Biological Collapse"),
              ("/bfs", "Biological Faith Systems"),
              ("/rice", "Bio Constraint Sweep \u2014 Rice")])
    + domain("III", "Mind",
             "Whether the self is written by the record layer rather than authoring it "
             "\u2014 and what minds build outward, beyond themselves.",
             [("/self_ego", "Self, the Ego Did Not Build"),
              ("/how_minds_resolve", "How Minds Resolve"),
              ("/cogitate", "COGITATE \u2014 Perceptual Resolution")])
    + domain("IV", "Artificial Intelligence",
             "Whether the kernel's signatures appear where machines work that record "
             "layer directly.",
             [("/cim_foundational", "Consciousness-Induced Material"),
              ("/ai_meaning_layer", "AI in the Meaning Layer"),
              ("/ai_sig_deployed", "S1\u2013S3 in Deployed AI Systems")])
    + '      </div>\n\n'
    '      <div class="strip reveal">Held to standards: '
    '<a href="/records">Records</a> &middot; '
    '<a href="/soe">Structuralization of Empiricism</a> &middot; '
    '<a href="/uis">Update Integrity</a></div>\n\n'
    '      <div class="strip reveal">What would prove this wrong: '
    '<a href="/falsification_standards">Failure Modes and Falsification Standards '
    '\u2192</a></div>\n\n'
    '      <div class="card-links reveal" style="margin-top: 3rem;">\n'
    '        <a href="/library">Full library \u2192</a>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
    '\n'
    + RULE +
    '\n'
)

NEW_AI = (
    '  <!-- Where AI Fits -->\n'
    '  <section id="yield">\n'
    '    <div class="container">\n'
    '      <div class="reveal">\n'
    '        <div class="section-label">Where AI Fits</div>\n'
    '        <h2 class="section-heading">UCT wasn\'t built to explain AI. That is '
    'precisely why AI matters as a test of the framework.</h2>\n'
    '        <p class="section-text">\n'
    '          On UCT\'s account, mind does not end at the boundary of the individual.\n'
    '          Minds build outside themselves \u2014 language, mathematics, tools, code,\n'
    '          institutions \u2014 a durable record layer that later minds inherit and add\n'
    '          to. UCT calls that layer Consciousness-Induced Material, or CIM.\n'
    '        </p>\n'
    '        <p class="section-text">\n'
    '          Artificial intelligence becomes structurally significant when\n'
    '          non-biological systems begin operating directly on that record layer and\n'
    '          returning new outputs to it. UCT therefore approaches AI first as a\n'
    '          recursive phase of CIM \u2014 not by assuming or denying machine\n'
    '          consciousness, but by examining what happens when mind\'s accumulated\n'
    '          records are processed back upon themselves by machines.\n'
    '        </p>\n'
    '        <p class="section-text">\n'
    '          The kernel came first. AI is neither UCT\'s foundation nor proof of the\n'
    '          framework. It is a derived case whose fit can be tested.\n'
    '        </p>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
    '\n'
    + RULE +
    '\n'
)

RANGES = [
    dict(
        id="R1-papers-rebuild",
        start=651, end=772,
        sha="0f42662b2bf4bc4beda1c5aaadc5b6cc2396a7af894d398a4de29830d6477cf2",
        first="  <!-- Papers -->\n",
        last="\n",
        must_contain=[('class="paper-card"', 4),
                      ('class="paper-card is-static"', 4),
                      ('class="strip reveal"', 2),
                      ('<span class="paper-number">01</span>', 1),
                      ('section-heading">Published Work', 1)],
        new=NEW_PAPERS,
        why="corpus block rebuilt: card 0, four questions, three strips",
    ),
    dict(
        id="R2-ai-remove",
        start=623, end=650,
        sha="538f4d36ec13203524b5224afc1ed972df7f9b434b23acc774456a02c3566cbc",
        first="  <!-- Where AI Fits -->\n",
        last="\n",
        must_contain=[('<section id="yield">', 1),
                      ('Where AI Fits', 2),
                      ('aiintegrityprotocol', 2),
                      ('section-rule', 1)],
        new="",
        why="AI section lifted from position 3 (reinserted at position 5 by E1)",
    ),
]

EDITS = [
    dict(
        id="E1-ai-reinsert",
        why="AI section lands after the corpus, before the book",
        old="  <!-- The Book -->\n",
        marker="That is precisely why AI matters as a test of the framework.",
        new=NEW_AI + "  <!-- The Book -->\n",
    ),
]

KEEP = ["/kernel_first", "/faith_without_fideism", "/program_map", "/roadmap/",
        "/falsification_standards", "/wp01", "/wp02", "/collapse_reframed",
        "/entropy_as_record", "/wp03", "/bfs", "/rice", "/self_ego",
        "/how_minds_resolve", "/cogitate", "/cim_foundational", "/ai_meaning_layer",
        "/ai_sig_deployed", "/records", "/soe", "/uis", "/library", "/architecture"]

DROP = ["/schrodinger", "/ai_synthetic", "/soai", "#framework"]

POST = [
    ('id="papers"', "==", 1),
    ('id="yield"', "==", 1),
    ('id="book"', "==", 1),
    ('id="about"', "==", 1),
    ('class="paper-card"', "==", 1),
    ('class="paper-card is-static"', "==", 4),
    ('class="strip reveal"', "==", 3),
    ('class="papers-grid', "==", 2),
    ("aiintegrityprotocol", "==", 0),
    ('section-heading">Published Work', "==", 0),
    ("Where the loop is being tested.", "==", 1),
    ("That is precisely why AI matters as a test of the framework.", "==", 1),
    ("Law of Coherence", "==", 0),
    ('<div class="hero-kernel">', "==", 1),
    ("A Coherence-First Research Program", "==", 2),
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
    ap = argparse.ArgumentParser(description="Structure commit (dry run by default).")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ignore-fingerprints", action="store_true")
    args = ap.parse_args()

    print("patch_homepage_structure - " + ("APPLY" if args.apply else "DRY RUN"))
    print("=" * 72)

    if not Path("tools").is_dir() or not Path(INDEX).exists():
        die(2, "not at repo root",
            "cd ~/universalcollapse-site && python3 tools/patch_homepage_structure.py")

    for blob in [NEW_PAPERS, NEW_AI]:
        for bad in FORBIDDEN:
            if bad in blob:
                die(2, "new markup contains forbidden notation %r" % bad, "see CLAUDE.md Sec 3")
    print("self-check      : clean, %d ranges + %d edit" % (len(RANGES), len(EDITS)))

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
        print("range %-18s %d-%d  sha %s  bounds %s/%s"
              % (r["id"], r["start"], r["end"],
                 "match" if got == r["sha"] else "DRIFT",
                 "ok" if okf else "BAD", "ok" if okl else "BAD"))
        if not (okf and okl):
            print("    line %d = %r" % (r["start"], clip(lines[r["start"] - 1])))
            print("    line %d = %r" % (r["end"], clip(lines[r["end"] - 1])))
            die(2, "range boundary mismatch", "re-harvest the section map and rebuild")
        if got != r["sha"]:
            print("    harvested %s\n    on disk   %s" % (r["sha"], got))
            if not args.ignore_fingerprints:
                die(3, "slice changed since harvest",
                    "sed -n '%d,%dp' %s | shasum -a 256" % (r["start"], r["end"], INDEX))
        for needle, n in r["must_contain"]:
            c = sl.count(needle)
            print("    contains %-40s %d (want %d)" % (clip(needle, 40), c, n))
            if c != n:
                die(2, "range %s content check failed" % r["id"],
                    "the slice is not the block this patcher was built for")

    print("-" * 72)
    for e in EDITS:
        c = text.count(e["old"])
        print("%-18s anchors=%d  %s" % (e["id"], c, e["why"]))
        if c != 1:
            die(2, "anchor for %s resolves %d times, want 1" % (e["id"], c),
                "re-harvest and rebuild; do not force")

    if not args.apply:
        print("-" * 72)
        print("DRY RUN - nothing written. Re-run with --apply.")
        sys.exit(0)

    for r in sorted(RANGES, key=lambda x: -x["start"]):
        lines = lines[:r["start"] - 1] + ([r["new"]] if r["new"] else []) + lines[r["end"]:]
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
    for slug in KEEP:
        if ('href="%s"' % slug) not in after:
            fails.append("lost link: %s" % slug)
    for slug in DROP:
        if ('href="%s"' % slug) in after:
            fails.append("should have dropped: %s" % slug)
    if after.count("<section") != after.count("</section>"):
        fails.append("section tags unbalanced: %d/%d"
                     % (after.count("<section"), after.count("</section>")))

    ip, iy, ib = (after.find('<section id="papers">'),
                  after.find('<section id="yield">'),
                  after.find('<section id="book">'))
    if not (0 < ip < iy < ib):
        fails.append("section order wrong: papers=%d yield=%d book=%d" % (ip, iy, ib))

    rule_before = text.count('<div class="container"><hr class="section-rule"></div>')
    rule_after = after.count('<div class="container"><hr class="section-rule"></div>')
    if rule_after != rule_before:
        fails.append("section-rule count moved %d -> %d (the AI section carries its own)"
                     % (rule_before, rule_after))

    if fails:
        for f in fails:
            print("  POST FAIL  " + f)
        die(2, "%d post-condition(s) failed - written but unverified" % len(fails),
            "git checkout -- " + INDEX + "   (git is the backup)")

    print("post-conditions : %d checks pass; %d/%d links kept, %d dropped; "
          "order hero>framework>corpus>AI>book>about>contact"
          % (len(POST) + len(KEEP) + len(DROP) + 3, len(KEEP), len(KEEP), len(DROP)))
    print("=" * 72)
    print("Next: lint, check_operator, render-verify, commit, push.")
    print("Then Cold Read Run C - the overhaul is not done until it is measured.")


if __name__ == "__main__":
    main()
