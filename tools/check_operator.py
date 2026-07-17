#!/usr/bin/env python3
"""
check_operator.py — verify the collapse operator survived OMML -> MathML.

uct_lint_html.py reads TEXT. It cannot see structure: <msub>C K</msub> and
<msubsup>C t K</msubsup> both strip to the characters "C K t" and both pass.
The notation law is about STRUCTURE — K superscript, t subscript — so it needs
a structural check.

Correct:   <msubsup><mi>C</mi><mi>t</mi><mi>K</mi></msubsup>   (base, sub, sup)
Correct:   <msup><mi>C</mi><mi>K</mi></msup>                   (time-suppressed, licensed)
VIOLATION: <msub><mi>C</mi><mi>K</mi></msub>                   (K as subscript)

Usage:
    python3 tools/check_operator.py public/read/*.html
"""
import re
import sys
from pathlib import Path

# MathML fragments, whitespace-tolerant
MSUBSUP = re.compile(
    r"<msubsup>\s*<m[in]>\s*C\s*</m[in]>\s*<m[in]>\s*t\s*</m[in]>\s*<m[in]>\s*K\s*</m[in]>\s*</msubsup>",
    re.I | re.S)
MSUB_BAD = re.compile(
    r"<msub>\s*<m[in]>\s*C\s*</m[in]>\s*<m[in]>\s*K\s*</m[in]>\s*</msub>", re.I | re.S)
MSUP_OK = re.compile(
    r"<msup>\s*<m[in]>\s*C\s*</m[in]>\s*<m[in]>\s*K\s*</m[in]>\s*</msup>", re.I | re.S)
# Unicode rendering (what Kernel First used — no MathML at all)
# U+1D37 MODIFIER LETTER CAPITAL K — NOT U+1D30. Verified against the deployed
# page: the operator is C + U+1D37 + U+209C ("Cᴷₜ"), 6 occurrences. An earlier
# version of this file checked U+1D30 and reported "no operator present" on a
# page whose operator was perfectly formed.
UNI_OK = re.compile("C[\u1D37\u1D30]")
UNI_BAD = re.compile(r"C\u2096|C_\{?K\}?")

# HTML sup/sub — the FOURTH form. Hand-authored pages (architecture.html) typeset the
# operator with <sup>/<sub> rather than MathML or Unicode. A checker that knows only
# the first three reports "no operator present" on a page carrying six correct ones.
# That has now happened three times with three different blind spots: U+1D30-vs-U+1D37,
# MathML-only, and this. Accept every form the corpus actually uses.
HTML_SUBSUP = re.compile(r"C\s*<sup>\s*K\s*</sup>\s*<sub>\s*t\s*</sub>", re.I)
HTML_SUP_OK = re.compile(r"C\s*<sup>\s*K\s*</sup>", re.I)
HTML_BAD = re.compile(r"C\s*<sub>\s*K\s*</sub>", re.I)

fail = 0
print(f"{'page':<30} {'msubsup':>8} {'msup':>6} {'uni':>5} {'html':>5} {'BAD':>5}  verdict")
print("-" * 84)
for f in sys.argv[1:]:
    s = Path(f).read_text(encoding="utf-8", errors="replace")
    good_ss = len(MSUBSUP.findall(s)) + len(HTML_SUBSUP.findall(s))
    good_sp = len(MSUP_OK.findall(s))
    good_u  = len(UNI_OK.findall(s))
    good_h  = len(HTML_SUP_OK.findall(s))
    bad     = len(MSUB_BAD.findall(s)) + len(UNI_BAD.findall(s)) + len(HTML_BAD.findall(s))
    total_good = good_ss + good_sp + good_u + good_h
    if bad:
        verdict = "VIOLATION — K as subscript"
        fail += 1
    elif total_good:
        verdict = "ok"
    else:
        verdict = "no operator present"
    print(f"{Path(f).name:<30} {good_ss:>8} {good_sp:>6} {good_u:>5} {good_h:>5} {bad:>5}  {verdict}")

print()
print(f"  {len(sys.argv)-1} page(s), {fail} with structural violations")
sys.exit(1 if fail else 0)
