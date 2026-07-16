#!/usr/bin/env python3
"""
set_src_files.py — write the operator-adjudicated docx mapping into site_data.yaml.

Every value below was read off the filesystem (find / --inventory), NOT recalled.
Two are operator calls, marked. Run once, then `make_envs.py --write`.

    python3 tools/set_src_files.py            # dry run — shows what it would change
    python3 tools/set_src_files.py --apply
"""
import re
import sys
from pathlib import Path

DATA = "tools/site_data.yaml"

SRC = {
    # --- The spine -----------------------------------------------------------
    "wp01":              "UCT_WP01_Foundations_of_Collapse_v2.0_2025_11_11.docx",
    "wp02":              "UCT_WP02_Collapse_in_Physics_Coherence_as_Law_from_Cosmology_to_Matter_v1.0_2025_11_11.docx",
    # OPERATOR CALL: the other candidate was T15 Biological Faith Systems — a
    # different paper that scored high on shared words. This is the 2026_05 build.
    "wp03":              "UCT_WP03_Biological_Collapse_v1.0_2026_05.docx",

    # --- CIM -----------------------------------------------------------------
    # The matcher was blind here: title says "Consciousness-Induced Material",
    # filename says "CIM_Foundational". Acronym vs expansion — zero shared tokens.
    "cim_foundational":  "UCT_T15_CIM_Foundational_v1.0_2026_05.docx",
    "ai_synthetic":      "UCT_T15_AI_as_Synthetic_Collapse_v1_0_2026_06.docx",

    # --- T1.5 bridges --------------------------------------------------------
    "collapse_reframed": "UCT_T15_Collapse_Reframed_v1.0_2026-02-12.docx",
    # Umlaut broke tokenisation: "Schrödinger" -> schr + dinger; file says Schrodinger.
    "schrodinger":       "UCT_T15_Schrodinger_Mathematical_Experience_v1.0_2026_02.docx",
    "bfs":               "UCT_T15_Biological_Faith_Systems_v1.0_2026_04.docx",
    "self_ego":          "UCT_T15_Self_the_Ego_Did_Not_Build_v1.0_2026_03.docx",

    # --- Standards -----------------------------------------------------------
    # OPERATOR CALL: two candidates in Standards/ —
    #   UCT_Standards_Records_Across_the_Stack_v1.0_2026_04.docx   (v1.0, different title)
    #   UCT_Standards_Records_v2.0_2026_04.docx                    (v2.0)  <- taken
    # Registry: Records is Live (v2.0) at 7H6DY. Only one file is v2.0.
    "records":           "UCT_Standards_Records_v2.0_2026_04.docx",
    "soe":               "UCT_Structuralization_of_Empiricism_v1.0_2026_04.docx",
    # Trash held a decoy: Trash/Update_Integrity_Standard_UIS_v1.0_2026-01-30.docx
    # outranked the real file until Trash was excluded. This is the Standards/ one.
    "uis":               "UCT_Update_Integrity_Standard_v1.0_2026_04.docx",
    "soai":              "UCT_T15_Structuralization_of_AI_v1_0_2026_06.docx",

    # --- T1.6 empirical ------------------------------------------------------
    "rice":              "UCT_T16_Bio_Constraint_Sweep_Rice_FINAL.docx",
    "cogitate":          "UCT_T16_Constraint_Dependent_Perceptual_Resolution_COGITATE_v1.0.docx",
    "ai_sig_deployed":   "UCT_T16_AI_Empirical_Demo_v1_0_2026_05.docx",
}

# Version law: everything is v1.0 EXCEPT WP01 and Records.
VERSION = {"wp01": "2.0", "records": "2.0"}


def main():
    apply = "--apply" in sys.argv
    p = Path(DATA)
    if not p.exists():
        sys.exit(f"{DATA} not found — run from the repo root")

    lines = p.read_text(encoding="utf-8").split("\n")
    out, changed = [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^  - slug: (\S+)\s*$", line)
        if not m:
            out.append(line)
            i += 1
            continue

        slug = m.group(1)
        out.append(line)
        i += 1

        # Consume the WHOLE paper block, not just the next line. Subtitles were
        # inserted after the slug by --harvest-subtitles, so a naive one-line skip
        # walks past them and leaves stale src_file/version further down —
        # producing duplicate keys, where yaml.safe_load silently takes the LAST.
        block = []
        while i < len(lines) and not re.match(r"^  - slug: ", lines[i]) \
                and not re.match(r"^[a-z_]+:", lines[i]):
            block.append(lines[i])
            i += 1

        # strip every existing src_file/version anywhere in the block
        block = [b for b in block if not re.match(r"^    (src_file|version):", b)]

        if slug in SRC:
            out.append(f'    src_file: "{SRC[slug]}"')
            if slug in VERSION:
                out.append(f'    version: "{VERSION[slug]}"')
            changed.append(slug)
        out.extend(block)

    missing = sorted(set(SRC) - set(changed))
    print(f"  set src_file for {len(changed)} papers")
    if missing:
        print(f"  NOT FOUND in site_data.yaml: {missing}")

    if not apply:
        print("\n  dry run — nothing written. Re-run with --apply")
        return 0

    p.write_text("\n".join(out), encoding="utf-8")
    print(f"\n  wrote {DATA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
