#!/usr/bin/env python3
"""One-shot: library cards + roadmap rows/flips for FWF, HIL, AIML.
Dry-run by default; --apply writes. Every op exact-count asserted; git is backup."""
import argparse, pathlib, sys

def die(m): print("FAIL  " + m); sys.exit(2)

def sub1(text, old, new, label):
    n = text.count(old)
    if n != 1: die(f"{label}: anchor found {n}x (want exactly 1)")
    return text.replace(old, new), label

LIB_CARDS = {
"kernel_first": """
        <a href="/faith_without_fideism" class="paper-card">
          <span class="paper-number">T0</span>
          <div class="paper-info">
            <span class="paper-title">Faith Without Fideism: The Named Floor of Open Inquiry</span>
            <span class="paper-desc">The gateway arc&rsquo;s second step &mdash; every enacted inquiry rests on commitments it cannot fully vindicate from within. Names UCT&rsquo;s floor as an elected, corrigible commitment and refuses to crown it: faith as process posture, and fideism as exactly what this is not.</span>
            <span class="paper-venue">OSF &middot; DOI 10.17605/OSF.IO/PF5RZ</span>
          </div>
          <span class="paper-arrow">&rarr;</span>
        </a>""",
"how_minds_resolve": """
        <a href="/human_interface_laws" class="paper-card">
          <span class="paper-number">T1.5</span>
          <div class="paper-info">
            <span class="paper-title">Human Interface Laws: A Philosophical Mechanics of Belief, Update, and Shared Reality</span>
            <span class="paper-desc">Eight regularities of the human interface &mdash; starting trust, bandwidth, gain-control feelings, identity protecting its constraints, records writing the person, signal regimes, self-sealing, and repair. The kernel as lived from the inside, with positional love and hate as aperture orientations.</span>
            <span class="paper-venue">OSF &middot; DOI 10.17605/OSF.IO/437HX</span>
          </div>
          <span class="paper-arrow">&rarr;</span>
        </a>""",
"ai_synthetic": """
        <a href="/ai_meaning_layer" class="paper-card">
          <span class="paper-number">T1.5</span>
          <div class="paper-info">
            <span class="paper-title">AI in the Meaning Layer: The Channel Made Visible</span>
            <span class="paper-desc">Completes the AI series &mdash; the encounter located inside the meaning-layer, CIM met first-person. Mind-recognition heuristics fire on a genuine surface signature from a non-mind structural source; the felt dissonance is the layer itself becoming visible.</span>
            <span class="paper-venue">OSF &middot; DOI 10.17605/OSF.IO/Z3SKB</span>
          </div>
          <span class="paper-arrow">&rarr;</span>
        </a>""",
}

def patch_library(t):
    ops = []
    for anchor_slug, card in LIB_CARDS.items():
        i = t.find(f'<a href="/{anchor_slug}" class="paper-card">')
        if i < 0: die(f"library: card for /{anchor_slug} not found")
        j = t.find("</a>", i)
        if j < 0: die(f"library: unterminated card for /{anchor_slug}")
        j += 4
        t = t[:j] + card + t[j:]
        ops.append(f"library: inserted card after /{anchor_slug}")
    return t, ops

def patch_roadmap(t):
    ops = []
    # --- 4 flips: dim forthcoming -> live linked step ---
    flips = [
      ('<div class="step dim"><div class="step-num">3</div><div class="step-body"><div class="step-title">Human Interface Laws <span class="ft">forthcoming</span></div><div class="step-note">Eight laws of cognition under constraint. No notation. Experiential.</div></div></div>',
       '<a class="step" href="/human_interface_laws"><div class="step-num">3</div><div class="step-body"><div class="step-title">Human Interface Laws</div><div class="step-note">Eight laws of cognition under constraint. No notation. Experiential.</div></div><span class="step-arrow">\u2192</span></a>',
       "roadmap: flip HIL (General Reader, step 3)"),
      ('<div class="step dim"><div class="step-num">4</div><div class="step-body"><div class="step-title">Human Interface Laws <span class="ft">forthcoming</span></div><div class="step-note">Eight laws. Experiential entry. No formalism required.</div></div></div>',
       '<a class="step" href="/human_interface_laws"><div class="step-num">4</div><div class="step-body"><div class="step-title">Human Interface Laws</div><div class="step-note">Eight laws. Experiential entry. No formalism required.</div></div><span class="step-arrow">\u2192</span></a>',
       "roadmap: flip HIL (Cognitive Scientist, step 4)"),
      ('<div class="step dim"><div class="step-num">5</div><div class="step-body"><div class="step-title">How Minds Resolve <span class="ft">forthcoming</span></div><div class="step-note">Accessible introduction to FRLB \u2014 faith, reason, logic, belief.</div></div></div>',
       '<a class="step" href="/how_minds_resolve"><div class="step-num">5</div><div class="step-body"><div class="step-title">How Minds Resolve</div><div class="step-note">Accessible introduction to FRLB \u2014 faith, reason, logic, belief.</div></div><span class="step-arrow">\u2192</span></a>',
       "roadmap: flip HMR (Cognitive Scientist, step 5) \u2014 stale two weeks"),
      ('<div class="step dim"><div class="step-num">6</div><div class="step-body"><div class="step-title">Human Interface Laws <span class="ft">forthcoming</span></div><div class="step-note">Applied epistemology \u2014 what the architecture means for minds.</div></div></div>',
       '<a class="step" href="/human_interface_laws"><div class="step-num">6</div><div class="step-body"><div class="step-title">Human Interface Laws</div><div class="step-note">Applied epistemology \u2014 what the architecture means for minds.</div></div><span class="step-arrow">\u2192</span></a>',
       "roadmap: flip HIL (Philosopher, step 6)"),
    ]
    for old, new, label in flips:
        t, op = sub1(t, old, new, label); ops.append(op)
    # --- AIML: AI Researcher step 3, renumber 3,4,5 -> 4,5,6 (reverse order) ---
    t, op = sub1(t,
      '<div class="step-num">5</div><div class="step-body"><div class="step-title">The AI Integrity Protocol',
      '<div class="step-num">6</div><div class="step-body"><div class="step-title">The AI Integrity Protocol',
      "roadmap: renumber AIP 5\u21926"); ops.append(op)
    t, op = sub1(t,
      'href="/s3_rag"><div class="step-num">4</div>',
      'href="/s3_rag"><div class="step-num">5</div>',
      "roadmap: renumber s3_rag 4\u21925"); ops.append(op)
    t, op = sub1(t,
      'href="/ai_sig_deployed"><div class="step-num">3</div>',
      'href="/ai_sig_deployed"><div class="step-num">4</div>',
      "roadmap: renumber ai_sig_deployed 3\u21924"); ops.append(op)
    aiml_step = '<a class="step" href="/ai_meaning_layer"><div class="step-num">3</div><div class="step-body"><div class="step-title">AI in the Meaning Layer</div><div class="step-note">Completes the AI series \u2014 the meaning-layer encounter, structural sight forming.</div></div><span class="step-arrow">\u2192</span></a>\n      '
    t, op = sub1(t,
      '<a class="step" href="/ai_sig_deployed">',
      aiml_step + '<a class="step" href="/ai_sig_deployed">',
      "roadmap: insert AIML (AI Researcher, step 3)"); ops.append(op)
    # --- FWF: Philosopher step 7, after the (now-flipped) HIL step 6 ---
    hil6 = '<a class="step" href="/human_interface_laws"><div class="step-num">6</div><div class="step-body"><div class="step-title">Human Interface Laws</div><div class="step-note">Applied epistemology \u2014 what the architecture means for minds.</div></div><span class="step-arrow">\u2192</span></a>'
    fwf_step = '\n      <a class="step" href="/faith_without_fideism"><div class="step-num">7</div><div class="step-body"><div class="step-title">Faith Without Fideism: The Named Floor</div><div class="step-note">Every inquiry\u2019s unvindicated commitment \u2014 named, elected, and kept corrigible.</div></div><span class="step-arrow">\u2192</span></a>'
    t, op = sub1(t, hil6, hil6 + fwf_step, "roadmap: insert FWF (Philosopher, step 7)"); ops.append(op)
    # --- tier-card docs corrections ---
    t, op = sub1(t,
      '<div class="docs">Kernel First: Collapse Without Reification</div>',
      '<div class="docs">Kernel First: Collapse Without Reification, Faith Without Fideism: The Named Floor of Open Inquiry</div>',
      "roadmap: Tier 0 docs += FWF"); ops.append(op)
    t, op = sub1(t,
      'How Minds Resolve, Human Interface Laws</div>',
      'How Minds Resolve, Human Interface Laws, AI in the Meaning Layer</div>',
      "roadmap: Tier 1.5 docs += AIML"); ops.append(op)
    t, op = sub1(t,
      'Entropy as Record, CMB Record Consensus (forthcoming)</div>',
      'Entropy as Record, CMB Record Consensus</div>',
      "roadmap: Tier 1.6 docs \u2014 drop false forthcoming on live pair"); ops.append(op)
    return t, ops

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    lib = pathlib.Path("public/library.html")
    rm  = pathlib.Path("public/roadmap/index.html")
    for p in (lib, rm):
        if not p.exists(): die(f"not found: {p} \u2014 run from repo root")
    lt, lops = patch_library(lib.read_text())
    rt, rops = patch_roadmap(rm.read_text())
    for o in lops + rops: print("  " + o)
    ft = rt.count('class="ft"')
    if ft != 6: die(f"post-check: expected 6 remaining forthcoming markers, found {ft}")
    for href in ("/faith_without_fideism", "/human_interface_laws", "/ai_meaning_layer"):
        if lt.count(f'href="{href}"') != 1: die(f"post-check: library link count for {href} != 1")
    print(f"post \u2713  roadmap forthcoming markers: 10 \u2192 {ft}; library links: 3 new")
    if not a.apply:
        print("\nDRY RUN \u2014 nothing written. Re-run with --apply."); return
    lib.write_text(lt); rm.write_text(rt)
    print("\nAPPLIED  public/library.html + public/roadmap/index.html")

if __name__ == "__main__": main()
