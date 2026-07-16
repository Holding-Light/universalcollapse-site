#!/usr/bin/env python3
"""
check_conversion.py — did the docx→HTML conversion DROP notation?

The problem this solves: a page with no operator and a page whose operator was
silently eaten by pandoc look identical from the output side. uct_lint_html.py
flags both. Only the SOURCE can tell them apart.

For each env: read the docx's own text + OMML, read the built HTML, compare.

    docx has operator, html has it      -> ok
    docx has NO operator, html has none -> ok (paper simply doesn't use the symbol)
    docx HAS operator, html has none    -> CONVERSION LOSS  <- the real defect
    docx has subscript-K anywhere       -> SOURCE VIOLATION (notation law, in the deposit)

Usage:
    python3 tools/check_conversion.py tools/*.env
"""
import re
import sys
import zipfile
from pathlib import Path

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

# Correct Unicode operator: C + MODIFIER LETTER CAPITAL K.
# U+1D37 is what this corpus actually uses (verified against the deployed page).
# U+1D30 accepted too — an earlier tool checked only U+1D30 and was blind.
UNI_OK = re.compile("C[\u1D37\u1D30]")
UNI_BAD = re.compile("C\u2096|C_\\{?K\\}?")


def env_get(text, key):
    m = re.search(rf'^{key}="(.*)"', text, re.M)
    return m.group(1) if m else ""


def docx_text(path):
    """All w:t and m:t runs, joined. Catches both prose and equation text."""
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception as e:
        return None, f"unreadable: {e}"
    runs = re.findall(r"<[wm]:t[^>]*>([^<]*)</[wm]:t>", xml)
    return "".join(runs), xml


def omml_operator(xml):
    """Count OMML sub/sup structures with base C. Returns (subsup, sup, sub_BAD)."""
    subsup = len(re.findall(r"<m:sSubSup>.{0,400}?<m:t>C</m:t>", xml, re.S))
    sup = len(re.findall(r"<m:sSup>.{0,400}?<m:t>C</m:t>", xml, re.S))
    sub = len(re.findall(r"<m:sSub>.{0,200}?<m:t>C</m:t>.{0,200}?<m:t>K</m:t>", xml, re.S))
    return subsup, sup, sub


def main():
    envs = sys.argv[1:]
    if not envs:
        sys.exit("usage: check_conversion.py tools/*.env")

    print(f"{'paper':<20} {'docx':>18}  {'html':>14}  verdict")
    print("-" * 76)
    bad = 0
    for e in envs:
        t = Path(e).read_text(encoding="utf-8")
        src, out = env_get(t, "SRC"), env_get(t, "OUT")
        slug = Path(e).stem
        if not Path(src).exists():
            print(f"{slug:<20} {'SRC missing':>18}"); bad += 1; continue
        if not Path(out).exists():
            print(f"{slug:<20} {'':>18}  {'not built':>14}"); continue

        text, xml = docx_text(src)
        if text is None:
            print(f"{slug:<20} {xml:>18}"); bad += 1; continue

        d_uni = len(UNI_OK.findall(text))
        d_bad = len(UNI_BAD.findall(text))
        ss, sp, sb = omml_operator(xml)
        d_has = d_uni + ss + sp
        d_names = "collapse operator" in text.lower()

        h = Path(out).read_text(encoding="utf-8", errors="replace")
        h_uni = len(UNI_OK.findall(h))
        h_math = h.count("<math")
        h_has = h_uni + h_math

        dcol = f"uni={d_uni} omml={ss+sp}"
        hcol = f"uni={h_uni} math={h_math}"

        if sb or d_bad:
            v = f"SOURCE VIOLATION — subscript-K in the docx ({sb+d_bad}x)"; bad += 1
        elif d_has and not h_has:
            v = "CONVERSION LOSS — docx has it, html lost it"; bad += 1
        elif not d_has and d_names:
            v = "ok — prose names it; docx never renders the symbol"
        elif d_has and h_has:
            v = "ok — present in both"
        else:
            v = "ok — operator not used"
        print(f"{slug:<20} {dcol:>18}  {hcol:>14}  {v}")

    print(f"\n  {len(envs)} paper(s), {bad} needing attention")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
