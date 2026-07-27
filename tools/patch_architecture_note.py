#!/usr/bin/env python3
"""One-shot: architecture map — note 2026-07-19 §A1/§A2/§A3 + §B1–§B4.
Faith-conflation fixes, HIL + AIML cards, 7 reciprocal cousins, uctPapers flips.
Dry-run by default; --apply writes the jsx. Rebuild via build_architecture.sh after."""
import argparse, pathlib, sys

def die(m): print("FAIL  " + m); sys.exit(2)

def sub1(t, old, new, label):
    n = t.count(old)
    if n != 1: die(f"{label}: anchor found {n}x (want exactly 1)")
    return t.replace(old, new), label

HIL_CARD = '''  mind_hil: {
    name: "Human Interface Laws (HIL)",
    layerId: "mind",
    register: "applied",
    role: "Eight regularities of the human interface \u2014 how cognition begins from starting trust, allocates bandwidth, weights feeling, protects identity, retains records, responds to signal regimes, risks self-sealing, and reopens revision. Three strengths: interface invariants, modulation principles, and conditional regime laws \u2014 the kernel as lived from the inside.",
    edge: "Applied output of the sort. Interface laws, not kernel laws: regularities of a human subsystem at its own surface. Regime laws are conditional and directional, not exceptionless; the aperture proposal stands or falls on discriminating positional openness from bandwidth, emotional tone, and threat load.",
    cousins: ["mind_frlb", "mind_etrust", "perc_pp01", "bio_bfs"],
    uctNotes: "Emerged from sorting the lived surface of cognition through the kernel. Law 1's starting trust is phase faith \u2014 the corrigible, commitment-bearing subset of K_t (grain per How Minds Resolve); the constitutive grain routes to the spine (WP04), not asserted here. Adds positional love and hate as aperture orientations \u2014 not emotions \u2014 and the Aperture Check as the reflective heuristic.",
  },

'''

AIML_CARD = '''  rcim_meaning: {
    name: "AI in the Meaning Layer",
    layerId: "recursive_cim",
    register: "applied",
    role: "Locates the AI encounter inside the meaning-layer \u2014 CIM as met from the first-person side of the perception channel. Foundation models are the first sustained, open-domain, language-producing synthetic source operating inside that layer: mind-recognition heuristics fire on a genuine surface signature from a non-mind structural source, and the felt dissonance is the layer itself becoming visible \u2014 structural sight forming.",
    edge: "Applied output of the sort. Claims neither that AI is conscious, nor that users are confused, nor that AI is 'just a tool' \u2014 the gap between surface signature and underlying structure is itself the phenomenon. AI outputs entering the layer become records that update its constraints; the long-run dynamics of that update remain open.",
    cousins: ["rcim_synth", "cim_cim", "perc_pp01", "rcim_philAI"],
    uctNotes: "Completes the four-part AI series, building on AI as Synthetic Collapse and The Structuralization of AI. The glass-and-fingerprint move: a medium becomes visible when something sufficiently foreign lands in it at sustained scale.",
  },
'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    p = pathlib.Path("tools/UCT_Architecture_Map_v4.jsx")
    if not p.exists(): die("run from repo root \u2014 tools/UCT_Architecture_Map_v4.jsx not found")
    t = p.read_text(); orig = t
    ops = []

    # ---- A1: FWF capsule (operatingPosture.t0) ----
    t, o = sub1(t,
      "Faith Without Fideism \u2014 a constitutive starting commitment is unavoidable, but it stays revisable, not protected.",
      "Faith Without Fideism \u2014 every enacted inquiry relies on commitments it cannot fully vindicate from within; UCT names its floor as an elected, corrigible commitment and refuses to crown it.",
      "A1: FWF capsule rewritten (grain-word fix)"); ops.append(o)

    # ---- A2: mind_frlb uctNotes (constitutive grain routed to spine) ----
    t, o = sub1(t,
      "uctNotes: \"Emerged from sorting mind through the kernel. Symbolic, narrated version of BFS. Note: here 'Faith' is the FRLB phase-position \u2014 the commitment slot conscious updating begins from \u2014 related to, but not identical with, the T0 constitutive floor in Faith Without Fideism.\",",
      "uctNotes: \"Emerged from sorting mind through the kernel. Symbolic, narrated version of BFS. Note: here 'Faith' is the FRLB phase-position \u2014 the commitment slot conscious updating begins from. Faith Without Fideism (T0) names the program-level instance of this same phase grain \u2014 the elected, corrigible faith-floor; the constitutive grain belongs to the spine (WP04, forthcoming).\",",
      "A2: mind_frlb note \u2014 constitutive grain routed to WP04"); ops.append(o)

    # ---- A3 (optional in note; included): kernelNote indexed-form appendix ----
    t, o = sub1(t,
      "the canonical kernel carries all eight elements \u2014 \u03a9, K, C^K, x*, R, S, T, U.\",",
      "the canonical kernel carries all eight elements \u2014 \u03a9, K, C^K, x*, R, S, T, U (shown time-suppressed; fully indexed: \u03a9, K_t, C^K_t, x_t*, R_t, S_t, T, U).\",",
      "A3: kernelNote gains the fully indexed form"); ops.append(o)

    # ---- B1: mind_hil card (inserted after mind_frlb, before the CIM divider) ----
    t, o = sub1(t,
      "  // ---------- CIM ----------",
      HIL_CARD + "  // ---------- CIM ----------",
      "B1: mind_hil card inserted (mind layer)"); ops.append(o)

    # ---- B2: rcim_meaning card (last card, after rcim_synth) ----
    t, o = sub1(t,
      "    uctNotes: \"Emerged from sorting AI through the kernel.\",\n  },\n};",
      "    uctNotes: \"Emerged from sorting AI through the kernel.\",\n  },\n" + AIML_CARD + "};",
      "B2: rcim_meaning card inserted (recursive_cim layer)"); ops.append(o)

    # ---- B3: seven reciprocal cousins ----
    recip = [
      ('cousins: ["bio_bfs", "mind_cbt", "mind_act", "mind_etrust"],',
       'cousins: ["bio_bfs", "mind_cbt", "mind_act", "mind_etrust", "mind_hil"],',
       "B3: mind_frlb += mind_hil (hub, 5 \u2014 operator may trim)"),
      ('cousins: ["mind_frlb", "perc_pp01", "cim_cultural"],',
       'cousins: ["mind_frlb", "perc_pp01", "cim_cultural", "mind_hil"],',
       "B3: mind_etrust += mind_hil"),
      ('cousins: ["bio_autopoiesis", "bio_homeostasis", "mind_frlb"],',
       'cousins: ["bio_autopoiesis", "bio_homeostasis", "mind_frlb", "mind_hil"],',
       "B3: bio_bfs += mind_hil"),
      ('cousins: ["perc_predproc", "perc_phenom", "mind_etrust"],',
       'cousins: ["perc_predproc", "perc_phenom", "mind_etrust", "mind_hil", "rcim_meaning"],',
       "B3: perc_pp01 += mind_hil, rcim_meaning (hub, 5 \u2014 operator may trim)"),
      ('cousins: ["rcim_llms", "cim_cim", "rcim_philAI"],',
       'cousins: ["rcim_llms", "cim_cim", "rcim_philAI", "rcim_meaning"],',
       "B3: rcim_synth += rcim_meaning"),
      ('cousins: ["cim_extended", "cim_cultural", "rcim_synth"],',
       'cousins: ["cim_extended", "cim_cultural", "rcim_synth", "rcim_meaning"],',
       "B3: cim_cim += rcim_meaning"),
      ('cousins: ["rcim_alignment", "perc_phenom"],',
       'cousins: ["rcim_alignment", "perc_phenom", "rcim_meaning"],',
       "B3: rcim_philAI += rcim_meaning"),
    ]
    for old, new, label in recip:
        t, o = sub1(t, old, new, label); ops.append(o)

    # ---- B4: uctPapers list updates ----
    t, o = sub1(t,
      '{ t: "How Minds Resolve (FRLB01, T15)" }',
      '{ t: "How Minds Resolve (T15)" }, { t: "Human Interface Laws (T15)" }',
      "B4: mind list \u2014 FRLB01 code retired, HIL added"); ops.append(o)
    t, o = sub1(t,
      '{ t: "AI in the Meaning Layer (T15)", soon: true }',
      '{ t: "AI in the Meaning Layer (T15)" }',
      "B4: AIML soon flag dropped (live at Z3SKB)"); ops.append(o)

    for o in ops: print("  " + o)

    # ---- post-conditions ----
    if t.count("soon: true") != 4:
        die(f"post: soon flags {t.count('soon: true')} != 4 (WP04, WP04 s7, Structural Biology, Structural Mind)")
    for k in ("mind_hil: {", "rcim_meaning: {"):
        if t.count(k) != 1: die(f"post: card {k!r} count != 1")
    if t.count("FRLB01") != 0: die("post: FRLB01 code still present")
    db = t.count("{") - orig.count("{"); dc = t.count("}") - orig.count("}")
    if db != dc: die(f"post: brace deltas unbalanced (+{db} vs +{dc})")
    print(f"post \u2713  soon 5\u21924 \u00b7 both cards present once \u00b7 FRLB01 retired \u00b7 brace deltas balanced (+{db}/+{dc})")

    if not a.apply:
        print("\nDRY RUN \u2014 nothing written. Re-run with --apply, then rebuild:")
        print("  bash tools/build_architecture.sh tools/UCT_Architecture_Map_v4.jsx")
        return
    p.write_text(t)
    print("\nAPPLIED  tools/UCT_Architecture_Map_v4.jsx")
    print("next: bash tools/build_architecture.sh tools/UCT_Architecture_Map_v4.jsx")

if __name__ == "__main__": main()
