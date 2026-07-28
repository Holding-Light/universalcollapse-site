#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_homepage_claim_register.py — Phase 1 of the 2026-07-27 site overhaul.

Claim-register edits on AUTHORED surfaces only. Confirmation register -> test
register; both senses of "Theory of Everything" refused; masthead phrase;
Tier 1.6 docs completion; CLAUDE.md documented expectations brought current.

Surfaces touched (3):
  public/index.html          hero label, <title>, hero closer, framework claim x2, ToE clause
  public/roadmap/index.html  Tier 1.6 docs list completion + semicolon residue
  CLAUDE.md                  Sec 0 expected numbers + ledger fingerprint,
                             Sec 8 registry pointer, append-only dated note

NEVER touches: public/architecture.html (build output), public/read/* (derived
from deposits), sitemap.xml / llms.txt / library.json (generated),
tools/site_data.yaml (the ledger). No links added, no pages added.
Counts must not move: papers 44 / read 41 / sitemap 90 / backlog 6 /
88 pages - 0 errors, 6 warnings.

Every anchor was harvested from the operator's repo at 6d45a86 on 2026-07-27,
never from memory and never from the brief's quotations.

Usage
  python3 tools/patch_homepage_claim_register.py                  # dry run (default)
  python3 tools/patch_homepage_claim_register.py --apply          # write
  python3 tools/patch_homepage_claim_register.py --s5-pointers    # + optional Sec 5 stale pointers
  python3 tools/patch_homepage_claim_register.py --ignore-base-drift

Exit codes
  0  applied, or nothing to do (already applied)
  2  gate failure (anchor drift, ambiguity, post-condition)
  3  base fingerprint drift
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

INDEX = "public/index.html"
ROADMAP = "public/roadmap/index.html"
CLAUDEMD = "CLAUDE.md"

# Harvested 2026-07-27 at 6d45a86, pre-edit.
BASE_SHA = {
    INDEX: "0aef190dbe40cc0325cd72ef2f4bde317e8440a999f7bff89d81584bb2bc10f1",
    ROADMAP: "20ba4f272e105bc74fb6708f389f4532fc3461429f484d804e26479b009978ca",
}

# Approved as-is (brief Sec 2.1). Count must be identical before and after.
TRIPLET = ("Constraint shapes collapse. Collapse writes records. "
           "Records update constraints.")

# Notation law (CLAUDE.md Sec 3): the subscript-K variant is forbidden in every
# artifact. Nothing here should introduce one; assert it rather than assume it.
FORBIDDEN = ("C_K", "C<sub>K", "C\u2096")

EDITS = [
    dict(
        id="01-hero-label",
        path=INDEX,
        why="masthead phrase (brief Sec 2.3) - one occurrence, harvested",
        old=">A Unified Philosophical Framework<",
        new=">A Coherence-First Research Program<",
    ),
    dict(
        id="02-title-tag",
        path=INDEX,
        why="<title> takes the subtitle (operator call 2026-07-27)",
        old="<title>Universal Collapse Theory</title>",
        new="<title>Universal Collapse Theory \u2014 A Coherence-First Research Program</title>",
    ),
    dict(
        id="03-hero-closer",
        path=INDEX,
        why="hero closing sentence: confirmation -> test register (brief Sec 2.1)",
        old="Everywhere structure emerges, the process tends toward coherence.",
        new=("Whether that pattern holds everywhere structure emerges is what this "
             "program is built to test."),
    ),
    dict(
        id="04-framework-claim",
        path=INDEX,
        why="'shows they share' -> 'tests whether they share' (brief Sec 2.1)",
        old="UCT shows they share one architecture:",
        new="UCT tests whether they share one architecture:",
    ),
    dict(
        id="05-framework-closer",
        path=INDEX,
        why="'runs the same way' -> portable / discriminating / corrigible (brief Sec 2.1)",
        old=("That loop is the engine \u2014 and it runs the same way from quantum "
             "measurement to cellular regulation to conscious experience."),
        new=("That loop is the proposal under test, from quantum measurement to "
             "cellular regulation to conscious experience. The question is whether "
             "it is portable, discriminating, and corrigible enough to warrant "
             "treatment as a Law of Coherence."),
    ),
    dict(
        id="06-toe-both-senses",
        path=INDEX,
        why="refuse both ToE senses, per Kernel First (brief Sec 2.2)",
        old=("The result is not a theory of everything in the reductive sense, but a "
             "structural grammar \u2014"),
        new=("UCT is not a Theory of Everything, and it does not claim that reality "
             "is made of collapse. It is a structural grammar \u2014"),
    ),
    dict(
        id="07-roadmap-t16-docs",
        path=ROADMAP,
        why="Tier 1.6 docs completion + semicolon residue (brief Sec 2.4)",
        old="S3-RAG-01; Entropy as Record, CMB Record Consensus</div>",
        new=("S3-RAG-01, Entropy as Record, CMB Record Consensus, "
             "F2 Training-Layer Positive Control, S3 Positive-Control "
             "Calibration</div>"),
    ),
    dict(
        id="08-claudemd-s0-numbers",
        path=CLAUDEMD,
        why="Sec 0 expected numbers -> post-ship (operator call 2026-07-27)",
        old=("Want: clean status; `sitemap URLs : 84`; `read pages : 38`; `backlog: 6`;\n"
             "`no doi.org links shadowing a local page \u2713`; **82 pages \u2014 0 errors, 5 warnings**\n"
             "(the check_conversion trio + the known-clean pair \u2014 unchanged since v4)."),
        new=("Want: clean status; `papers built : 44`; `read pages : 41`; `sitemap URLs : 90`;\n"
             "`backlog: 6`; `no doi.org links shadowing a local page \u2713`; **88 pages \u2014 0\n"
             "errors, 6 warnings** (the check_conversion trio + the known-clean pair +\n"
             "`read/faith_without_fideism`, pre-cleared \u2014 the structural gate reads its\n"
             "`msubsup` as lawful; only the text linter can't see it)."),
    ),
    dict(
        id="09-claudemd-fingerprint",
        path=CLAUDEMD,
        why="Sec 0 ledger fingerprint -> post-ship",
        old=("Ledger fingerprint (reproducible from the committed yaml): **41 papers, 158 edges**\n"
             "(related 100 + read_first 27 + supports 23 + tested_by 8), **124 do-not-read-as**."),
        new=("Ledger fingerprint (reproducible from the committed yaml): **44 papers, 177 edges**\n"
             "(related 116 + read_first 30 + supports 23 + tested_by 8), **134 do-not-read-as**."),
    ),
    dict(
        id="10-claudemd-s8-registry",
        path=CLAUDEMD,
        why="Sec 8 registry pointer generalized (operator call 2026-07-27)",
        old="| DOIs, publication status | `UCT_DOI_Registry_v2_8_2026_07.md` |",
        new="| DOIs, publication status | latest `UCT_DOI_Registry_v*` \u2014 highest version wins |",
    ),
    dict(
        id="11-claudemd-correction-note",
        path=CLAUDEMD,
        why=("append-only dated correction (the program's own UIS pattern); also "
             "closes the 07-20 note's open 'still want one live --check'"),
        old="> moved since the v7 handoff.\n",
        marker="**§0 refreshed 2026-07-27**",
        new=("> moved since the v7 handoff.\n"
             ">\n"
             "> **\u00a70 refreshed 2026-07-27** \u2014 append-only correction, post FWF/HIL/AIML\n"
             "> ship. The 07-20 note above stands as written; its numbers were the\n"
             "> 41-paper era's. Current, confirmed by one live `--check` at `6d45a86`:\n"
             "> 44 papers \u00b7 41 read pages \u00b7 90 sitemap URLs \u00b7 177 edges \u00b7 134 do-not-read-as\n"
             "> \u00b7 88 pages / 0 errors / 6 warnings. The measured numbers were never\n"
             "> wrong; only the documented expectations were.\n"),
    ),
]

# OPTIONAL, off by default: two same-class stale pointers in Sec 5 that the
# operator did not name. Surfaced, not defaulted. Enable with --s5-pointers.
S5_EDITS = [
    dict(
        id="S5a-registry-pointer",
        path=CLAUDEMD,
        why="Sec 5 tail carries the same v2.8 pointer as Sec 8 (OPTIONAL)",
        old="`UCT_DOI_Registry_v2_8_2026_07.md`. Cross-check each entry",
        new="the latest `UCT_DOI_Registry_v*`. Cross-check each entry",
    ),
    dict(
        id="S5b-yaml-paper-count",
        path=CLAUDEMD,
        why="Sec 5 tools table still says 41 papers (OPTIONAL)",
        old="| `tools/site_data.yaml` | Rule 3 single source \u2014 41 papers + 6-DOI backlog |",
        new="| `tools/site_data.yaml` | Rule 3 single source \u2014 44 papers + 6-DOI backlog |",
    ),
]

# (path, needle, op, n) - asserted after write, on re-read bytes.
POST = [
    (INDEX, "A Unified Philosophical", "==", 0),
    (INDEX, "A Coherence-First Research Program", "==", 2),   # hero-label + <title>
    (INDEX, "Everywhere structure emerges, the process tends toward coherence.", "==", 0),
    (INDEX, "UCT shows they share", "==", 0),
    (INDEX, "runs the same way", "==", 0),
    (INDEX, "not a theory of everything", "==", 0),
    (INDEX, "not a Theory of Everything", "==", 1),
    (INDEX, "Law of Coherence", ">=", 2),
    (ROADMAP, "S3-RAG-01;", "==", 0),
    (ROADMAP, "F2 Training-Layer Positive Control", "==", 1),
    (ROADMAP, "S3 Positive-Control Calibration", "==", 1),
    (CLAUDEMD, "82 pages", "==", 0),
    (CLAUDEMD, "158 edges", "==", 0),
    (CLAUDEMD, "**44 papers, 177 edges**", "==", 1),
    (CLAUDEMD, "134 do-not-read-as", ">=", 1),
]


def read(p: str) -> str:
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p: str, s: str) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def sha256(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def nl_of(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def norm(s: str, nl: str) -> str:
    return s if nl == "\n" else s.replace("\n", nl)


def classify(text: str, e: dict, nl: str):
    old = norm(e["old"], nl)
    marker = norm(e.get("marker") or e["new"], nl)
    if text.count(marker) >= 1:
        return "ALREADY", text.count(old), text.count(marker)
    n_old = text.count(old)
    if n_old == 1:
        return "PENDING", 1, 0
    return "AMBIGUOUS", n_old, 0


def clip(s: str, n: int = 120) -> str:
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + " ..."


def die(code: int, msg: str, remedy: str) -> None:
    print("\n  GATE FAILED: " + msg)
    print("  REMEDY: " + remedy + "\n")
    sys.exit(code)


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 1 claim-register patcher (dry run by default).")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--s5-pointers", action="store_true",
                    help="also fix the two OPTIONAL Sec 5 stale pointers in CLAUDE.md")
    ap.add_argument("--ignore-base-drift", action="store_true",
                    help="proceed even if a base fingerprint does not match the harvest")
    args = ap.parse_args()

    edits = list(EDITS) + (list(S5_EDITS) if args.s5_pointers else [])

    print("patch_homepage_claim_register - " + ("APPLY" if args.apply else "DRY RUN"))
    print("=" * 72)

    # --- gate 0: repo root ------------------------------------------------
    if not Path("tools").is_dir() or not Path(INDEX).exists():
        die(2, "not at repo root (no tools/ or public/index.html here)",
            "cd ~/universalcollapse-site && python3 tools/patch_homepage_claim_register.py")

    # --- gate 1: self-check on the replacement strings ---------------------
    for e in edits:
        if e["old"] == e["new"]:
            die(2, "edit %s is a no-op" % e["id"], "fix the edit table")
        for bad in FORBIDDEN:
            if bad in e["new"]:
                die(2, "edit %s would introduce forbidden notation %r" % (e["id"], bad),
                    "the collapse operator is C^K_t; see CLAUDE.md Sec 3")
    print("self-check      : %d edits, no forbidden notation, no no-ops" % len(edits))

    # --- gate 2: base fingerprints ----------------------------------------
    drift = []
    for p, want in BASE_SHA.items():
        got = sha256(p)
        state = "match" if got == want else "DRIFT"
        print("base %-26s %s" % (p + ":", state))
        if got != want:
            drift.append((p, want, got))
    if drift and not args.ignore_base_drift:
        for p, want, got in drift:
            print("    %s\n      harvested %s\n      on disk   %s" % (p, want, got))
        die(3, "a base file changed since the 2026-07-27 harvest",
            "re-harvest the anchors and rebuild this patcher, or "
            "--ignore-base-drift if the change is known and unrelated")

    # --- gate 3: classify every anchor ------------------------------------
    texts = {}
    for p in sorted({e["path"] for e in edits}):
        texts[p] = read(p)

    print("-" * 72)
    states = {}
    for e in edits:
        t = texts[e["path"]]
        state, n_old, n_new = classify(t, e, nl_of(t))
        states[e["id"]] = state
        print("%-9s %-26s old=%d new=%d  %s" % (state, e["id"], n_old, n_new, e["path"]))

    if all(s == "ALREADY" for s in states.values()):
        print("-" * 72)
        print("nothing to do - every edit is already applied. No write.")
        sys.exit(0)

    bad = [i for i, s in states.items() if s == "AMBIGUOUS"]
    if bad:
        die(2, "anchor drift or ambiguity: " + ", ".join(bad),
            "re-run the harvest greps for those anchors and rebuild from the "
            "pasted bytes; do not force")

    mixed = [i for i, s in states.items() if s == "ALREADY"]
    if mixed:
        print("\n  NOTE: partially applied already, will be skipped: " + ", ".join(mixed))

    # --- preview ----------------------------------------------------------
    print("-" * 72)
    for e in edits:
        if states[e["id"]] != "PENDING":
            continue
        print("[%s] %s" % (e["id"], e["why"]))
        print("   - " + clip(e["old"]))
        print("   + " + clip(e["new"]))
    print("-" * 72)

    if not args.apply:
        print("DRY RUN - nothing written. Re-run with --apply when the wording is approved.")
        sys.exit(0)

    # --- apply ------------------------------------------------------------
    pre_triplet = texts[INDEX].count(TRIPLET)
    touched = []
    for p in texts:
        t = texts[p]
        nl = nl_of(t)
        changed = False
        for e in edits:
            if e["path"] != p or states[e["id"]] != "PENDING":
                continue
            old, new = norm(e["old"], nl), norm(e["new"], nl)
            if t.count(old) != 1:
                die(2, "anchor count changed mid-run for %s" % e["id"],
                    "git checkout -- " + " ".join(sorted(texts)))
            t = t.replace(old, new, 1)
            changed = True
        if changed:
            write(p, t)
            touched.append(p)
    print("wrote           : " + ", ".join(touched))

    # --- post-conditions --------------------------------------------------
    after = {p: read(p) for p in texts}
    failures = []
    for p, needle, op, n in POST:
        if p not in after:
            continue
        got = after[p].count(needle)
        ok = (got == n) if op == "==" else (got >= n)
        if not ok:
            failures.append("%s: %r %s %d, got %d" % (p, needle, op, n, got))

    post_triplet = after[INDEX].count(TRIPLET)
    if post_triplet != pre_triplet:
        failures.append("kernel triplet count moved: %d -> %d (it is approved as-is)"
                        % (pre_triplet, post_triplet))
    for p, t in after.items():
        for badstr in FORBIDDEN:
            if badstr in t and badstr not in texts[p]:
                failures.append("%s: introduced forbidden notation %r" % (p, badstr))

    if failures:
        for f in failures:
            print("  POST FAIL  " + f)
        die(2, "%d post-condition(s) failed - files are written but unverified" % len(failures),
            "git checkout -- " + " ".join(sorted(after)) + "   (git is the backup)")

    print("post-conditions : %d checks pass; kernel triplet preserved (%d)"
          % (len(POST) + 1, post_triplet))
    print("=" * 72)
    print("Next: build_site_meta --check, lint_doi_shadow, uct_lint_html "
          "(full form, --papers-from), then commit + push.")
    print("Counts must not move: 44 / 41 / 90, backlog 6, 88 pages - 0 errors, 6 warnings.")


if __name__ == "__main__":
    main()
