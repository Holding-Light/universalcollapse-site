#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_claudemd_trio.py - Commit 0 of the 2026-07-27 copy pass.

Three riders that have deferred through three commits as passengers, now
travelling alone:

  S5a  Sec 5 tail still names UCT_DOI_Registry_v2_8_2026_07.md; Sec 8 was
       generalized in 931f1ce and this is the last hard-coded pointer.
  S5b  Sec 5 tools table still says 41 papers; the ledger holds 44.
  T10  Sec 10 gains the zsh paste-block trap, earned 2026-07-27 when a run
       block with trailing `# comment` annotations skipped its own dry run.

Touches ONE file: CLAUDE.md (repo root, documentation only).
Touches nothing under public/, nothing generated, no ledger. Changes no counts:
this commit cannot move 4 / 44 / 41 / 90 because it edits no site surface.

Usage
  python3 tools/patch_claudemd_trio.py                   # dry run (default)
  python3 tools/patch_claudemd_trio.py --apply           # write
  python3 tools/patch_claudemd_trio.py --also-grep-trap  # + the 4th, OPTIONAL
Exit codes: 0 ok / nothing to do . 2 gate failure
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CLAUDEMD = "CLAUDE.md"

REGISTER_TAIL = ("  canonical, and `og:` field against the ledger \u2014 not the "
                 "ones you remember.\n")

ZSH_TRAP = (
    "\n"
    "- **A paste block is a program in the operator's shell, not yours.** A run\n"
    "  block written with trailing `# comment` annotations was pasted into zsh,\n"
    "  where `interactive_comments` is off by default: the `#` became an\n"
    "  argument, argparse rejected it, and the dry run was silently skipped \u2014\n"
    "  the patcher went straight to `--apply` with no review pass. The same `#`\n"
    "  swallowed both post-push verification greps. Annotations belong in the\n"
    "  tool's own output, never in a block someone else pastes.\n"
)

GREP_TRAP = (
    "\n"
    "- **A verification grep dies when a class string grows.** `grep -c\n"
    "  'class=\"paper-card\"'` returned 4 where 8 cards existed: four carried\n"
    "  `class=\"paper-card is-static\"`, which does not contain the searched\n"
    "  string \u2014 the closing quote differs. The patcher's own post-conditions,\n"
    "  which asserted both forms separately, were right; the verification line\n"
    "  typed afterward was wrong. Verify with the assertion the tool already\n"
    "  makes, not a fresh string from memory.\n"
)

EDITS = [
    dict(
        id="S5a-registry-pointer",
        why="Sec 5 tail - last hard-coded v2.8 pointer (Sec 8 generalized in 931f1ce)",
        old="`UCT_DOI_Registry_v2_8_2026_07.md`. Cross-check each entry",
        new="the latest `UCT_DOI_Registry_v*`. Cross-check each entry",
    ),
    dict(
        id="S5b-yaml-paper-count",
        why="Sec 5 tools table - ledger holds 44, table said 41",
        old="| `tools/site_data.yaml` | Rule 3 single source \u2014 41 papers + 6-DOI backlog |",
        new="| `tools/site_data.yaml` | Rule 3 single source \u2014 44 papers + 6-DOI backlog |",
    ),
    dict(
        id="T10-zsh-paste-trap",
        why="Sec 10 register - earned 2026-07-27",
        old=REGISTER_TAIL,
        marker="A paste block is a program in the operator's shell",
        new=REGISTER_TAIL + ZSH_TRAP,
    ),
]

OPTIONAL = [
    dict(
        id="T10-grep-class-trap",
        why="Sec 10 register - OPTIONAL, second trap earned the same day",
        old=REGISTER_TAIL,
        marker="A verification grep dies when a class string grows",
        new=REGISTER_TAIL + GREP_TRAP,
    ),
]

POST = [
    ("UCT_DOI_Registry_v2_8_2026_07.md", "==", 0),
    ("the latest `UCT_DOI_Registry_v*`", ">=", 1),
    ("44 papers + 6-DOI backlog", "==", 1),
    ("41 papers", "==", 1),
    ("**44 papers, 177 edges**", "==", 1),
    ("A paste block is a program in the operator's shell", "==", 1),
]


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def nl_of(t):
    return "\r\n" if "\r\n" in t else "\n"


def norm(s, nl):
    return s if nl == "\n" else s.replace("\n", nl)


def die(code, msg, remedy):
    print("\n  GATE FAILED: " + msg)
    print("  REMEDY: " + remedy + "\n")
    sys.exit(code)


def classify(text, e, nl):
    marker = norm(e.get("marker") or e["new"], nl)
    if text.count(marker) >= 1:
        return "ALREADY"
    return "PENDING" if text.count(norm(e["old"], nl)) == 1 else "AMBIGUOUS"


def main():
    ap = argparse.ArgumentParser(description="Commit 0 - CLAUDE.md riders (dry run by default).")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--also-grep-trap", action="store_true",
                    help="add the OPTIONAL second Sec 10 entry (modifier-class grep)")
    args = ap.parse_args()

    edits = list(EDITS) + (list(OPTIONAL) if args.also_grep_trap else [])

    print("patch_claudemd_trio - " + ("APPLY" if args.apply else "DRY RUN"))
    print("=" * 68)

    if not Path("tools").is_dir() or not Path(CLAUDEMD).exists():
        die(2, "not at repo root", "cd ~/universalcollapse-site && python3 tools/patch_claudemd_trio.py")

    text = read(CLAUDEMD)
    nl = nl_of(text)
    print("file            : CLAUDE.md, %d lines, %d edit(s)"
          % (text.count("\n") + 1, len(edits)))

    states = {}
    for e in edits:
        s = classify(text, e, nl)
        states[e["id"]] = s
        print("%-9s %-24s %s" % (s, e["id"], e["why"]))

    if all(s == "ALREADY" for s in states.values()):
        print("-" * 68)
        print("nothing to do - every edit already applied. No write.")
        sys.exit(0)

    bad = [i for i, s in states.items() if s == "AMBIGUOUS"]
    if bad:
        die(2, "anchor drift or ambiguity: " + ", ".join(bad),
            "re-harvest those anchors from CLAUDE.md and rebuild; do not force")

    if not args.apply:
        print("-" * 68)
        print("DRY RUN - nothing written. Re-run with --apply.")
        sys.exit(0)

    out = text
    for e in edits:
        if states[e["id"]] != "PENDING":
            continue
        old, new = norm(e["old"], nl), norm(e["new"], nl)
        if out.count(old) != 1:
            die(2, "anchor count changed mid-run for %s" % e["id"],
                "git checkout -- " + CLAUDEMD)
        out = out.replace(old, new, 1)
    write(CLAUDEMD, out)
    print("wrote           : " + CLAUDEMD)

    after = read(CLAUDEMD)
    fails = []
    for needle, op, n in POST:
        got = after.count(needle)
        if not ((got == n) if op == "==" else (got >= n)):
            fails.append("%r %s %d, got %d" % (needle[:52], op, n, got))
    if args.also_grep_trap and "A verification grep dies" not in after:
        fails.append("optional grep trap requested but absent")
    if fails:
        for f in fails:
            print("  POST FAIL  " + f)
        die(2, "%d post-condition(s) failed" % len(fails),
            "git checkout -- " + CLAUDEMD + "   (git is the backup)")

    print("post-conditions : %d checks pass" % len(POST))
    print("  note: `41 papers` == 1 is correct - the dated 2026-07-20 note is")
    print("        preserved as written; append-only, not rewritten.")
    print("=" * 68)
    print("No site surface touched. Commit and push; no lint run required.")


if __name__ == "__main__":
    main()
