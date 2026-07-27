#!/usr/bin/env python3
"""One-shot: closing polish + docs. Homepage FWF card after Kernel First;
CLAUDE.md gains the ADDING_PAPERS.md pointer (§6) and the §10 trap register.
Dry-run by default; --apply writes."""
import argparse, pathlib, sys

def die(m): print("FAIL  " + m); sys.exit(2)

def sub1(t, old, new, label):
    n = t.count(old)
    if n != 1: die(f"{label}: anchor found {n}x (want exactly 1)")
    return t.replace(old, new), label

FWF_CARD = '''

        <a href="/faith_without_fideism" class="paper-card">
          <span class="paper-number">T0</span>
          <div class="paper-info">
            <span class="paper-title">Faith Without Fideism: The Named Floor of Open Inquiry</span>
            <span class="paper-desc">The gateway arc\u2019s second step \u2014 every enacted inquiry rests on commitments it cannot fully vindicate from within. Names UCT\u2019s floor as an elected, corrigible commitment and refuses to crown it: naming a floor makes it auditable; crowning one is the structural beginning of dogma.</span>
          </div>
          <span class="paper-arrow">\u2192</span>
        </a>'''

SEC10 = '''## 10. Traps \u2014 a tool encoding one assumption about a world that has two

Register added 2026-07-27. Each entry earned by an actual failure or near-miss;
none is hypothetical. The shape is always the same: an instrument, template, or
reviewer carrying one assumption about a world that turned out to have two.

- **The DOI-shadow lint guards the site; nothing guards the papers' reference
  lists.** SoE cites Records and UIS with DOIs and WP01 bare. The site's
  identifier discipline does not propagate to the corpus's own bibliographies.
- **A deposited abstract is a retrieval surface with its own version.** Kernel
  drift surfaces are three \u2014 `patch_kernel_terms.TERMS`, `build_llms` prose,
  and the PhilArchive record abstract \u2014 and nothing compares them.
  (JONUCT-2 gained a forward pointer + DOI 2026-07-27; the trap outlives the
  instance.)
- **Unnamed discipline gets named by readers.** A floating acronym resolved two
  ways across two cold reads; an everywhere-practiced, nowhere-named boundary
  got a reader-invented scheme attributed to the project. No lint catches "the
  corpus does this but never says so."
- **Steering is invisible from inside.** Anonymous prompts control for
  author-deference, not frame-following: a steered cold model elaborates the
  offered thesis back and calls it more compelling. Only unsteered turns are
  signal.
- **Instruments inherit the ontology of their config.** The acceptance sweep
  verified every URL the sitemap declares and could not see the hostname the
  sitemap never mentions. www was dead for five months beside all-green checks.
- **A green gate can be reading a stale artifact.** The architecture build died
  upstream (`npm: command not found`); the operator gate and lint downstream
  truthfully PASSED \u2014 on yesterday's page. The same week, an external
  reviewer's cache produced a punch list of already-fixed items. Before
  trusting a gate, confirm the artifact it read is the one you just made.
- **Legacy configs resurrect retired bugs.** `kernelfirst.env` (pre-migration
  era) used as a template carried `OUT=read/\u2026` and re-created the 2026-06-29
  split-brain. Envs are records of an era; clone the newest sibling, never the
  oldest.
- **TIER is a cross-checked record, not a label.** `build_site_meta` byte-
  matches each env's TIER against the ledger's tier_label-or-tier and dies on
  mismatch. The ledger is source; sync the env to it. Do not default.
- **Cloned surfaces hide fields you didn't grep.** `citation_public_url`
  survived a truncated head-dump and shipped on three landings pointing at the
  template's URL. When cloning an authored page, diff every `citation_*`,
  canonical, and `og:` field against the ledger \u2014 not the ones you remember.

---

'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    idx = pathlib.Path("public/index.html")
    cm  = pathlib.Path("CLAUDE.md")
    for p in (idx, cm):
        if not p.exists(): die(f"not found: {p} \u2014 run from repo root")
    ops = []

    # ---- 1. homepage: FWF card after Kernel First ----
    t = idx.read_text()
    i = t.find('href="/kernel_first"')
    if i < 0: die("index: kernel_first card not found")
    i = t.rfind('<a ', 0, i)
    j = t.find('</a>', i)
    if j < 0: die("index: kernel_first card unterminated")
    j += 4
    if 'faith_without_fideism' in t: die("index: FWF already present \u2014 refusing to double-apply")
    t = t[:j] + FWF_CARD + t[j:]
    ops.append("index: FWF card inserted after Kernel First (Published Work)")

    # ---- 2. CLAUDE.md: \u00a76 pointer to the playbook ----
    c = cm.read_text()
    c, o = sub1(c,
      "follow the same authored-then-patched shape.",
      "follow the same authored-then-patched shape. **The full batch sequence \u2014\ngates, expected numbers, and per-paper checklist \u2014 is `ADDING_PAPERS.md` at\nrepo root. Read it first.**",
      "CLAUDE.md: \u00a76 gains the ADDING_PAPERS.md pointer"); ops.append(o)

    # ---- 3. CLAUDE.md: \u00a710 trap register before the closing line ----
    c, o = sub1(c,
      "---\n\nThe site renders; the deposits assert.",
      "---\n\n" + SEC10 + "The site renders; the deposits assert.",
      "CLAUDE.md: \u00a710 trap register inserted (9 traps)"); ops.append(o)

    for o in ops: print("  " + o)

    # ---- post-conditions ----
    if t.count('href="/faith_without_fideism"') != 1: die("post: index FWF link != 1")
    if c.count("## 10. Traps") != 1: die("post: \u00a710 header != 1")
    if c.count("ADDING_PAPERS.md") < 1: die("post: playbook pointer missing")
    if "C_K" in (t + c).replace("C^K", ""): die("post: banned notation emitted")
    print("post \u2713  homepage card 1\u00d7 \u00b7 \u00a710 present \u00b7 playbook referenced \u00b7 notation clean")

    if not a.apply:
        print("\nDRY RUN \u2014 nothing written. Re-run with --apply."); return
    idx.write_text(t); cm.write_text(c)
    print("\nAPPLIED  public/index.html + CLAUDE.md")
    print("note: ADDING_PAPERS.md ships alongside \u2014 ensure it is untarred at repo root before committing")

if __name__ == "__main__": main()
