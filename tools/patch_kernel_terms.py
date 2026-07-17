#!/usr/bin/env python3
"""
patch_kernel_terms.py — the UCT kernel as a schema.org DefinedTermSet.

uct_lint.py enforces notation law INSIDE the corpus; nothing enforced it at the
retrieval boundary. A DefinedTerm carrying the canonical form is the mechanism
that makes a retrieving model reproduce the operator correctly when it
paraphrases — the notation law extended to the one surface that had no control
(handoff 2026-07-17 item 4).

Definitions live in site_data.yaml under `program.kernel.terms` — the SINGLE
source, shared with the llms.txt kernel section that build_site_meta emits. They
are one-sentence condensations of UCT_Symbols_and_Formulas_Reference v1.7 and are
not authored here: edit the Reference, then site_data, then rerun both tools. A
second copy of the kernel in this file would be the exact drift the tier split
was fixed to prevent.

TARGETS: public/index.html and public/kernel_first.html — the two stable,
authored surfaces where the kernel is defined. Read pages are regenerated from
docx and would silently drop an injected block on rebuild; putting slug-
conditional content into the global template is the wrong shape. Landing +
homepage cover the crawl paths.

NOTATION SELF-CHECK: per CLAUDE.md §3, "never write X" still emits X for a
scraper — so the forbidden subscript-K operator form appears NOWHERE in this
file or its output, not even as a prohibition. The patcher asserts its own
payload contains the canonical form and no C-underscore-K sequence before
writing a byte.

Repeatable; dry-run by default; --apply writes. No backups: git is the backup.

    python3 tools/patch_kernel_terms.py
    python3 tools/patch_kernel_terms.py --apply
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUB = Path("public")
TARGETS = ["index.html", "kernel_first.html"]

MARK_BEGIN = "<!-- kernel-terms: derived by patch_kernel_terms.py from the Symbols and Formulas Reference v1.7. Edit the Reference, then this tool; do not hand-edit. -->"
MARK_END = "<!-- /kernel-terms -->"
RE_BLOCK = re.compile(r"^[ \t]*" + re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END)
                      + r"\n?", re.S | re.M)
ANCHOR_OG = re.compile(r"^([ \t]*)<!-- Open Graph", re.M)
ANCHOR_PRE = re.compile(r'^([ \t]*)<link rel="preconnect"', re.M)



def build(site, terms):
    base = site["base"].rstrip("/")
    set_id = f"{base}/kernel_first#kernel-terms"
    return {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": set_id,
        "name": "UCT Kernel Notation",
        "url": f"{base}/kernel_first",
        "description": "The eight-element kernel of Universal Collapse Theory — "
                       "canonical symbols and one-line definitions, per the "
                       "Symbols and Formulas Reference (v1.7).",
        "hasDefinedTerm": [
            {
                "@type": "DefinedTerm",
                "termCode": code,
                "name": name,
                "description": desc,
                "inDefinedTermSet": set_id,
            }
            for code, name, desc in terms
        ],
    }


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    site = d["site"]
    kd = (d.get("program") or {}).get("kernel") or {}
    terms = [(t["code"], t["name"], t["description"]) for t in kd.get("terms", [])]
    if len(terms) != 8:
        sys.exit(f"FAIL  site_data program.kernel.terms has {len(terms)} entries, "
                 f"expected the 8-element kernel — refusing to emit a partial kernel")
    obj = build(site, terms)
    payload = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")

    # notation self-check on the exact bytes about to land
    if "C^K_t" not in payload:
        sys.exit("FAIL  payload lost the canonical operator form")
    if re.search(r"C_[Kk]\b|C_\{[Kk]\}", payload):
        sys.exit("FAIL  payload contains a forbidden operator form")

    touched = 0
    for name in TARGETS:
        f = PUB / name
        if not f.exists():
            sys.exit(f"FAIL  {f} not found")
        html = f.read_text(encoding="utf-8")
        m = ANCHOR_OG.search(html) or ANCHOR_PRE.search(html)
        if not m:
            sys.exit(f"FAIL  {name}: no insertion anchor")
        indent = m.group(1)
        block = "\n".join([f"{indent}{MARK_BEGIN}",
                           f'{indent}<script type="application/ld+json">',
                           payload,
                           f"{indent}</script>",
                           f"{indent}{MARK_END}",
                           ""])
        if RE_BLOCK.search(html):
            out = RE_BLOCK.sub(block, html, count=1)
            action = "replace"
        else:
            out = html[: m.start()] + block + html[m.start():]
            action = "insert"
        print(f"  {name}: {action}")
        if apply:
            f.write_text(out, encoding="utf-8")
            touched += 1

    if apply:
        for name in TARGETS:
            html = (PUB / name).read_text(encoding="utf-8")
            m = RE_BLOCK.search(html)
            assert m, f"{name}: block missing after write"
            inner = re.search(r'<script type="application/ld\+json">\n(.*?)\n[ \t]*</script>',
                              m.group(0), re.S)
            got = json.loads(inner.group(1).replace("<\\/", "</"))
            assert len(got["hasDefinedTerm"]) == 8, f"{name}: term count != 8"
            assert any(t["name"] == "C^K_t" for t in got["hasDefinedTerm"])
        print(f"verified: {touched} page(s), 8 terms each, canonical operator present, parses clean")
    else:
        print("DRY-RUN (use --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
