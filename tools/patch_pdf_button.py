#!/usr/bin/env python3
"""
patch_pdf_button.py — restore a styled "Download PDF" button on every landing.

TWO PROBLEMS, one cause:

1. STYLING. kernel_first carries a `.cta-secondary` rule appended AFTER its
   @media block — a tell that it was patched in when its Download button was
   added. The other 16 landings never had a secondary button, so they never got
   the rule. patch_landings.py added the class without the CSS, so the browser
   falls back to default link styling: purple text, no border. This injects the
   rule where missing.

2. TARGET. Only 2 PDFs exist locally (Kernel First, WP01). For the other 15 the
   button points at the best available source:
       local /pdf/  ->  PhilArchive  ->  OSF
   Off-site buttons are labelled honestly ("PDF at PhilArchive") and open in a
   new tab. As each PDF is exported to public/pdf/, re-run and it swaps to local
   automatically — local always wins.

SAFETY: dry-run default; --apply writes .bak; idempotent; refuses on structure
mismatch. Touches only <style> and the cta-row. Prose is never matched.

    python3 tools/patch_pdf_button.py
    python3 tools/patch_pdf_button.py --apply
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUBLIC = Path("public")

CSS_RULE = """
    .cta-secondary { color: var(--accent); background: transparent; border-color: var(--accent-dim); }
    .cta-secondary:hover { background: rgba(201, 169, 110, 0.08); border-color: var(--accent); }
"""

RE_CTA = re.compile(r'<div class="cta-row">.*?</div>', re.S)
RE_STYLE_END = re.compile(r"</style>")

def pdf_target(paper, on_disk):
    """Local PDF always wins. The filename comes from site_data's `pdf_file`
    (Rule 3) — never guessed. A wrong PDF under a DOI is precisely the failure
    the read-page hash guard prevents, and the PDF path has no such guard, so
    nothing here is inferred."""
    f = paper.get("pdf_file")
    if f and f in on_disk:
        return f"/pdf/{f}", "Download PDF", False
    if paper.get("philarchive"):
        return f'https://philarchive.org/rec/{paper["philarchive"]}', "PDF at PhilArchive", True
    return f'https://osf.io/{paper["doi"].lower()}/', "PDF at OSF", True


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    on_disk = {p.name for p in (PUBLIC / "pdf").glob("*.pdf")}

    css_added = btn_added = skipped = refused = 0
    print(f"{'slug':<18} {'css':<10} {'button':<22} target")
    print("-" * 76)

    for paper in d["papers"]:
        slug = paper["slug"]
        f = PUBLIC / f"{slug}.html"
        if not f.exists():
            print(f"{slug:<18} MISSING"); refused += 1; continue

        s = f.read_text(encoding="utf-8")
        out = s
        did_css = did_btn = False

        # --- 1. CSS -------------------------------------------------------
        if ".cta-secondary" in out:
            css_state = "present"
        else:
            m = RE_STYLE_END.search(out)
            if not m:
                print(f"{slug:<18} REFUSE — no </style> found"); refused += 1; continue
            out = out[:m.start()] + CSS_RULE + out[m.start():]
            css_state = "ADDED"
            did_css = True

        # --- 2. button ----------------------------------------------------
        m_cta = RE_CTA.search(out)
        if not m_cta:
            print(f"{slug:<18} REFUSE — no cta-row"); refused += 1; continue
        row = m_cta.group(0)

        href, label, external = pdf_target(paper, on_disk)
        attrs = ' target="_blank" rel="noopener"' if external else ""
        btn = f'<a class="cta cta-secondary" href="{href}"{attrs}>{label}</a>'

        m_sec = re.search(r'<a class="cta cta-secondary"[^>]*>.*?</a>', row, re.S)
        if m_sec:
            if m_sec.group(0) == btn:
                btn_state = "present"
            else:
                # re-target: a PDF may have landed since the last run
                new_row = row[:m_sec.start()] + btn + row[m_sec.end():]
                out = out[:m_cta.start()] + new_row + out[m_cta.end():]
                was_off = "philarchive" in m_sec.group(0) or "osf.io" in m_sec.group(0)
                btn_state = f"RETARGET{' -> local' if was_off and not external else ''}"
                did_btn = True
        else:
            new_row = row.replace("</div>", "\n        " + btn + "\n      </div>")
            out = out[:m_cta.start()] + new_row + out[m_cta.end():]
            btn_state = label
            did_btn = True

        tgt = href if len(href) < 44 else href[:41] + "…"
        print(f"{slug:<18} {css_state:<10} {btn_state:<22} {tgt}")
        css_added += did_css
        btn_added += did_btn
        if not (did_css or did_btn):
            skipped += 1
        elif apply:
            f.with_suffix(".html.bak").write_text(s, encoding="utf-8")
            f.write_text(out, encoding="utf-8")

    print(f"\n  css injected: {css_added}   buttons added: {btn_added}   "
          f"unchanged: {skipped}   refused: {refused}")
    if not apply:
        print("  dry run — nothing written. Re-run with --apply")
    print("  NOTE: as PDFs land in public/pdf/ with the name recorded in site_data's")
    print("        pdf_file, re-run --apply. Existing off-site buttons are RE-TARGETED")
    print("        to local automatically; local always wins.")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
