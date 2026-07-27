#!/usr/bin/env python3
"""One-shot: add faith_without_fideism, human_interface_laws, ai_meaning_layer
to site_data.yaml, compute all hashes, inject SRC_SHA256 into the two new envs.
Dry-run by default; --apply writes. Fail-loud; git is backup."""
import argparse, hashlib, pathlib, re, sys

SLUGS = ["faith_without_fideism", "human_interface_laws", "ai_meaning_layer"]
PDFS  = {"faith_without_fideism": "UCT_T0_Faith_Without_Fideism_Named_Floor_v1_0_2026_07.pdf",
         "human_interface_laws":  "UCT_T15_Human_Interface_Laws_v1_0_2026_07.pdf",
         "ai_meaning_layer":      "UCT_T15_AI_in_the_Meaning_Layer_v1_0_2026_05.pdf"}
NEW_ENVS = ["human_interface_laws", "ai_meaning_layer"]
ANCHOR = "  - slug: starter_physics"

BLOCKS = """  - slug: faith_without_fideism
    relations:
      purpose: >-
        Every enacted inquiry relies on commitments it cannot fully vindicate 
        from within; UCT names its floor as an elected, corrigible commitment 
        and refuses to crown it.
      read_first: [kernel_first]
      related: [bfs, how_minds_resolve, wp01, records, uis, soe]
      do_not_read_as:
        - "A defense of fideism — the paper is its refusal: the floor stays revisable, not protected"
        - "A religious or doctrinal claim — faith names a process posture, commitment under incomplete resolution, content-neutral across inquiry"
        - "A claim that the floor is constitutive bedrock — the constitutive grain belongs to the spine (WP04, forthcoming); this paper names the elected, program-level floor"
    short_title: "Faith Without Fideism"
    tier_label: "Tier 0 · Gateway"
    pdf_sha256: "__PDF_SHA_faith_without_fideism__"
    src_file: "UCT_T0_Faith_Without_Fideism_Named_Floor_v1_0_2026_07.docx"
    pdf_file: "UCT_T0_Faith_Without_Fideism_Named_Floor_v1_0_2026_07.pdf"
    title: "Faith Without Fideism: The Named Floor of Open Inquiry"
    subtitle: "The Named Floor of Open Inquiry"
    doi: "PF5RZ"
    tier: "Tier 0 — Orientation"
    version: "1.0"
    philarchive: "JONFWF"
    lastmod: "2026-07-27"
    priority: "0.9"
    desc: "Every enacted inquiry relies on commitments it cannot fully vindicate from within. This paper names UCT's floor as an elected, corrigible commitment — and refuses to crown it."
    built: true
    read: true
    pdf: true

  - slug: human_interface_laws
    relations:
      purpose: >-
        Eight regularities of the human interface — how cognition begins from 
        starting trust, allocates bandwidth, weights feeling, protects identity, 
        retains records, responds to signal regimes, risks self-sealing, and 
        reopens revision — the kernel as lived from the inside.
      read_first: [how_minds_resolve]
      related: [wp01, bfs, self_ego, records, cim_foundational, uis]
      do_not_read_as:
        - "Kernel laws — these are interface laws: regularities of a human subsystem at its own surface"
        - "Exceptionless regularities — the regime laws are conditional and directional"
        - "A claim that positional love and hate are emotions — they are aperture orientations, and the Aperture Check is the reflective heuristic"
    short_title: "Human Interface Laws"
    pdf_sha256: "__PDF_SHA_human_interface_laws__"
    src_file: "UCT_T15_Human_Interface_Laws_v1_0_2026_07.docx"
    pdf_file: "UCT_T15_Human_Interface_Laws_v1_0_2026_07.pdf"
    title: "Human Interface Laws: A Philosophical Mechanics of Belief, Update, and Shared Reality"
    subtitle: "A Philosophical Mechanics of Belief, Update, and Shared Reality"
    doi: "437HX"
    tier: "Tier 1.5 — Interpretive Bridges"
    version: "1.0"
    philarchive: "JONHIL"
    lastmod: "2026-07-27"
    priority: "0.8"
    desc: "Eight regularities of the human interface — starting trust, bandwidth, gain-control, identity, records, signal regimes, self-sealing, and repair — the kernel as lived from the inside."
    built: true
    read: true
    pdf: true

  - slug: ai_meaning_layer
    relations:
      purpose: >-
        Locates the AI encounter inside the meaning-layer — CIM met from the 
        first-person side of the channel. Foundation models are the first 
        sustained, open-domain synthetic source operating inside that layer; the 
        felt dissonance is the layer itself becoming visible.
      read_first: [cim_foundational]
      related: [soai, ai_synthetic, self_ego, wp01]
      do_not_read_as:
        - "A claim that AI is conscious — the gap between surface signature and underlying structure is itself the phenomenon"
        - "A claim that users are confused or that AI is 'just a tool' — mind-recognition heuristics fire on a genuine surface signature"
        - "A forecast — the long-run dynamics of AI outputs entering the layer as records remain open"
    short_title: "AI in the Meaning Layer"
    pdf_sha256: "__PDF_SHA_ai_meaning_layer__"
    src_file: "UCT_T15_AI_in_the_Meaning_Layer_v1_0_2026_05.docx"
    pdf_file: "UCT_T15_AI_in_the_Meaning_Layer_v1_0_2026_05.pdf"
    title: "AI in the Meaning Layer: The Channel Made Visible"
    subtitle: "The Channel Made Visible"
    doi: "Z3SKB"
    tier: "Tier 1.5 — Interpretive Bridges"
    version: "1.0"
    lastmod: "2026-07-27"
    priority: "0.8"
    desc: "Locates the AI encounter inside the meaning-layer — CIM met from the first-person side of the channel — and reads the felt dissonance as the layer itself becoming visible."
    built: true
    read: true
    pdf: true

"""

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def die(msg):
    print("FAIL  " + msg); sys.exit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(".")
    yml = root / "tools" / "site_data.yaml"
    if not yml.exists():
        die("run from repo root (~/universalcollapse-site) — tools/site_data.yaml not found")

    # 1. asset gate ---------------------------------------------------------
    missing, later = [], []
    for s in SLUGS:
        for q in (root/"public"/f"{s}.html", root/"public"/"pdf"/PDFS[s]):
            if not q.exists():
                missing.append(str(q))
        rp = root/"public"/"read"/f"{s}.html"
        if not rp.exists():
            later.append(str(rp))
    if missing:
        die("missing assets (place them first):\n      " + "\n      ".join(missing))
    print("assets ✓  3 landings + 3 PDFs present")
    if later:
        print("note: read pages pending (build_paper.sh runs AFTER this step):\n      "
              + "\n      ".join(later))

    # 2. compute hashes -----------------------------------------------------
    blocks = BLOCKS
    for s in SLUGS:
        h = sha256(root/"public"/"pdf"/PDFS[s])
        blocks = blocks.replace(f"__PDF_SHA_{s}__", h)
        print(f"pdf sha  {s[:24]:24} {h[:16]}…")
    if "__PDF_SHA_" in blocks:
        die("internal: unreplaced pdf sha placeholder")

    env_writes = {}
    for s in NEW_ENVS:
        env_p = root/"tools"/f"{s}.env"
        if not env_p.exists():
            die(f"missing {env_p} — untar the package at repo root first")
        env = env_p.read_text()
        m = re.search(r'SRC="([^"]+)"', env)
        src = pathlib.Path(m.group(1))
        if not src.exists():
            die(f"docx not found: {src}  (fix SRC= in {env_p})")
        h = sha256(src)
        env2, n = re.subn(r'SRC_SHA256="[^"]*"', f'SRC_SHA256="{h}"', env)
        if n != 1:
            die(f"SRC_SHA256 line not found exactly once in {env_p}")
        env_writes[env_p] = env2
        print(f"docx sha {s[:24]:24} {h[:16]}…")

    # 3. yaml insertion -----------------------------------------------------
    text = yml.read_text()
    for s in SLUGS:
        c = text.count(f"- slug: {s}")
        if c:
            die(f"'{s}' already in site_data.yaml ({c}×) — inspect before re-running; refusing to double-apply")
    if text.count(ANCHOR) != 1:
        die(f"anchor not found exactly once: {ANCHOR!r}")
    new_text = text.replace(ANCHOR, blocks + ANCHOR)

    # 4. post-conditions ----------------------------------------------------
    try:
        import yaml as _y
        d = _y.safe_load(new_text)
        papers = d["papers"]
        n = len(papers)
        if n != 44:
            die(f"post-parse paper count {n} != 44")
        built = {p["slug"] for p in papers}
        edges = 0
        for p in papers:
            r = p.get("relations", {}) or {}
            for f in ("read_first", "supports", "tested_by", "related"):
                for e in r.get(f, []) or []:
                    edges += 1
                    if e not in built:
                        die(f"{p['slug']}: {f} edge {e!r} is not a built slug")
        aiml = next(p for p in papers if p["slug"] == "ai_meaning_layer")
        if "philarchive" in aiml:
            die("ai_meaning_layer must not carry a philarchive key (OSF-only by design)")
        print(f"yaml ✓  44 papers, {edges} edges, all edges resolve, AIML philarchive-free")
    except ImportError:
        print("WARN  pyyaml unavailable — structural post-check skipped (text asserts held)")

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return
    yml.write_text(new_text)
    for p, v in env_writes.items():
        p.write_text(v)
    print("\nAPPLIED  tools/site_data.yaml + " + ", ".join(str(p) for p in env_writes))
    print("next: build_site_meta --check, then write; then patchers; then lints (see README_ADD3.md)")

if __name__ == "__main__":
    main()
