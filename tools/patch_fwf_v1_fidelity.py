#!/usr/bin/env python3
"""One-shot: FWF landing fidelity to the v1.0 deposit.
Replaces the v0.5-drafted abstract with the paper's own abstract (verbatim, house
dash spacing), adds the Naming-and-Crowning and Seam sections (operator-supplied
text), and upgrades do_not_read_as to v1.0 language. Dry-run default; --apply."""
import argparse, pathlib, sys

def die(m): print("FAIL  " + m); sys.exit(2)

ABSTRACT = '''          <p>Every inquiry begins from somewhere. Before a framework can justify, test, revise, or defend its claims, it already relies on norms, capacities, practices, or commitments it does not fully vindicate within the same episode. This paper names one subset of those dependencies as faith, while sharply distinguishing the term from religious belief, revelation, credulity, or assent against evidence: a faith-floor is an explicit, action-guiding program commitment held under incomplete warrant and governed by public conditions of correction.</p>
          <p>The paper argues that no enacted inquiry is floorless, and that the constructive response to the old regress problem is neither suspension nor concealment but naming. A crowned floor \u2014 a starting commitment promoted into final fact \u2014 becomes dogma. A named floor can be audited, inherited, revised, and abandoned if it degenerates. Naming does not validate the commitment; it makes the commitment auditable.</p>
          <p>The paper draws a seam the corpus has run implicitly: the access-floor and the content-floor differ in kind. The access-floor is experience as the route by which claims reach human inquiry \u2014 a necessary condition whose denial must use it. The content-floor is UCT\u2019s elected commitment that its canonical kernel tracks recurring structural relations across domains \u2014 named, revisable, and fruit-tested. Biological Faith Systems and How Minds Resolve show the same commitment-before-certainty structure operating in biology and mind; this paper names the foundational form and gives it a stable address in the T0 gateway arc: Kernel First \u2192 Faith Without Fideism \u2192 Sealed Inquiry \u2192 The Tether.</p>
          <p><em>What this paper does not claim.</em> The claim is deliberately small. It does not defeat foundationalism, coherentism, infinitism, or externalist accounts of warrant, and it does not hold that all starting points have equal epistemic standing \u2014 some floors generate public records, discriminating tests, and reliable correction; others generate insulation and rescue maneuvers.</p>
          <p><strong>Keywords:</strong> faith-floor; named floor; access-floor; content-floor; gateway arc.</p>'''

SECTIONS = '''  <div class="container"><hr class="section-rule"></div>

  <section>
    <div class="container">
      <div class="section-label">Naming and Crowning</div>
      <div class="prose">
          <p>To name a floor is to say: this is where the system stands. It is not proven from within. It is held because without it the work cannot begin, and because the work it enables stays fruitful, corrigible, and open to failure. A named floor is exposed to audit \u2014 inheritable by successors, questionable by critics, droppable if it stops doing legitimate work. Naming does not validate a commitment; it makes the commitment auditable.</p>
          <p>To crown a floor is to treat that same starting point as final fact. The commitment is promoted into the base of all things, made unavailable for criticism, protected from contrary records, and defended by changing the rules of update whenever it is threatened. A crowned floor is the structural beginning of dogma.</p>
      </div>
    </div>
  </section>

  <div class="container"><hr class="section-rule"></div>

  <section>
    <div class="container">
      <div class="section-label">The Seam</div>
      <div class="prose">
          <p>The two floors under this program are not the same kind, and letting them sit under one surface is itself a failure mode.</p>
          <p>The access-floor is experience as the route by which claims reach human inquiry. Its warrant is that any attempt to deny it must use it. It is a necessary condition of claim-making, not an elected commitment.</p>
          <p>The content-floor is the program\u2019s elected commitment that its canonical kernel tracks recurring structural relations across domains. Declared, revisable, judged by its fruits.</p>
          <p>They differ in the kind of warrant that holds them, not in whether they are crowned. Blurring the seam would let a chosen theoretical commitment borrow the standing of an undeniable access condition. That would be crowning.</p>
      </div>
    </div>
  </section>

'''

DNRA_OLD = '''      do_not_read_as:
        - "A defense of fideism \u2014 the paper is its refusal: the floor stays revisable, not protected"
        - "A religious or doctrinal claim \u2014 faith names a process posture, commitment under incomplete resolution, content-neutral across inquiry"
        - "A claim that the floor is constitutive bedrock \u2014 the constitutive grain belongs to the spine (WP04, forthcoming); this paper names the elected, program-level floor"'''

DNRA_NEW = '''      do_not_read_as:
        - "A defense of fideism \u2014 the paper is its refusal: the floor stays revisable, not protected"
        - "Religious belief, revelation, credulity, or assent against evidence \u2014 faith here is a restricted structural term: an explicit, action-guiding commitment under public conditions of correction"
        - "A refutation of foundationalism, coherentism, infinitism, or externalist accounts of warrant \u2014 the claim is deliberately small, and starting points do not all have equal standing"
        - "A license for the content-floor to borrow the access-floor\u2019s standing \u2014 the seam between them is the point; blurring it would be crowning"'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    land = pathlib.Path("public/faith_without_fideism.html")
    yml  = pathlib.Path("tools/site_data.yaml")
    for p in (land, yml):
        if not p.exists(): die(f"not found: {p} \u2014 run from repo root")
    t = land.read_text()

    # ---- 1. replace the Abstract prose ----
    start_anchor = '<div class="section-label">Abstract</div>\n      <div class="prose">'
    i = t.find(start_anchor)
    if i < 0: die("landing: Abstract prose anchor not found")
    j = t.find("\n      </div>", i)
    if j < 0: die("landing: Abstract prose close not found")
    body_start = i + len(start_anchor)
    old_body = t[body_start:j]
    if "gateway arc's third step" not in old_body:
        die("landing: expected the v0.5-drafted abstract in place; found something else \u2014 inspect before applying")
    t = t[:body_start] + "\n" + ABSTRACT + t[j:]
    print("  landing: Abstract replaced with the v1.0 deposit abstract (verbatim, house dashes)")

    # ---- 2. insert the two sections before the Position section ----
    pos = t.find("<!-- position:")
    if pos < 0: die("landing: position-block comment not found")
    sec = t.rfind("<section>", 0, pos)
    if sec < 0: die("landing: enclosing <section> for position block not found")
    t = t[:sec] + SECTIONS.rstrip() + "\n\n  " + t[sec:]
    print("  landing: Naming-and-Crowning + The Seam sections inserted before Position")

    # ---- 3. yaml dnra upgrade ----
    y = yml.read_text()
    n = y.count(DNRA_OLD)
    if n != 1: die(f"yaml: current FWF do_not_read_as block found {n}x (want exactly 1)")
    y = y.replace(DNRA_OLD, DNRA_NEW)
    print("  yaml: FWF do_not_read_as upgraded to v1.0 language (3 \u2192 4 clauses, seam included)")

    # ---- post-conditions ----
    if "gateway arc's third step" in t: die("post: stale third-step phrasing survives")
    if "Kernel First \u2192 Faith Without Fideism \u2192 Sealed Inquiry \u2192 The Tether" not in t:
        die("post: deposit arc order not present")
    for label in ("Naming and Crowning", "The Seam"):
        if t.count(f'<div class="section-label">{label}</div>') != 1:
            die(f"post: section {label!r} count != 1")
    if t.count("<section>") - land.read_text().count("<section>") != 2:
        die("post: section delta != 2")
    try:
        import yaml as _y
        d = _y.safe_load(y)
        fwf = next(p for p in d["papers"] if p["slug"] == "faith_without_fideism")
        if len(fwf["relations"]["do_not_read_as"]) != 4: die("post: FWF dnra != 4")
        print("  post \u2713  arc order = deposit; 2 sections; dnra = 4; yaml parses")
    except ImportError:
        print("  post \u2713  (pyyaml unavailable \u2014 text asserts held)")

    if not a.apply:
        print("\nDRY RUN \u2014 nothing written. Re-run with --apply."); return
    land.write_text(t); yml.write_text(y)
    print("\nAPPLIED  public/faith_without_fideism.html + tools/site_data.yaml")
    print("next: build_site_meta (write), patch_position_blocks (dry then --apply), lint tail, commit, push")

if __name__ == "__main__": main()
