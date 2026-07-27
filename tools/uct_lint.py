#!/usr/bin/env python3
"""uct_lint.py — notation & version lint for UCT docx deliverables.

Enforces:
  1. Notation law: collapse operator is C^K_t (K superscript, t subscript).
     C with subscript K is forbidden in any form:
       - OMML subscript-only structure (m:sSub with base C, sub K)  -> ERROR
       - literal text "C_K" / "C_{K}" in prose or math runs         -> ERROR
       - lowercase variants (C_k, C + U+2096)                        -> WARN
     Time-suppressed C^K (superscript only) and full C^K_t (m:sSubSup)
     are legitimate and are never flagged.
  2. Version consistency: the version in the end-matter Citation line
     "(vX.Y)" must match the filename version "_vX_Y_".
     Mismatch -> WARN by default (working files may anticipate the
     deposit version); use --deposit to escalate mismatch to ERROR for
     final pre-deposit checks. Missing Citation line -> WARN.

Usage:
  python tools/uct_lint.py FILE.docx [FILE2.docx ...]
  python tools/uct_lint.py UNPACKED_DIR/        # lint before repack
  python tools/uct_lint.py --deposit FILE.docx  # strict: version mismatch = ERROR

Accepts real .docx (zip), an unpacked docx directory (contains word/),
or plain UTF-8 text files carrying a .docx extension (project-file quirk).

Exit codes: 0 = PASS (warnings allowed), 1 = FAIL (errors), 2 = usage/IO.
"""

import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

# Literal-text patterns (run against run-joined paragraph text)
RE_CK_UPPER = re.compile(r"C_\{?K\}?")
RE_CK_LOWER = re.compile(r"C_\{?k\}?|C\u2096")  # includes C + subscript-k char
RE_CITE_VER = re.compile(r"\((?:[A-Z0-9]+\s+)?v(\d+\.\d+)\)")
RE_FILE_VER = re.compile(r"_v(\d+)_(\d+)(?=[_.\-])")

DOC_PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")


def _snippet(text, match=None, width=70):
    text = " ".join(text.split())
    if match:
        i = max(0, text.find(match) - 25)
        return ("…" if i else "") + text[i : i + width] + ("…" if len(text) > i + width else "")
    return text[:width] + ("…" if len(text) > width else "")


def _para_text(p):
    """Join all w:t and m:t text in document order (handles fragmented runs)."""
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))


def lint_xml_part(xml_bytes, part_name, findings):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        findings.append(("ERROR", part_name, f"XML parse failure: {e}"))
        return []

    parent = {c: pr for pr in root.iter() for c in pr}
    paragraphs = []

    # --- Check A: OMML structural — m:sSub with base C, subscript K/k ---
    for ssub in root.iter(M + "sSub"):
        e = ssub.find(M + "e")
        sub = ssub.find(M + "sub")
        base = "".join(t.text or "" for t in e.iter(M + "t")).strip() if e is not None else ""
        subt = "".join(t.text or "" for t in sub.iter(M + "t")).strip() if sub is not None else ""
        if base.endswith("C") and subt in ("K", "k"):
            node, ptxt = ssub, ""
            while node in parent:
                node = parent[node]
                if node.tag == W + "p":
                    ptxt = _para_text(node)
                    break
            sev = "ERROR" if subt == "K" else "WARN"
            findings.append((sev, part_name,
                f"OMML subscript form C_{subt} (m:sSub) — notation law requires C^K_t"
                + (f" — near: “{_snippet(ptxt)}”" if ptxt else "")))

    # --- Check B: literal text patterns on run-joined paragraph text ---
    for p in root.iter(W + "p"):
        ptxt = _para_text(p)
        if not ptxt:
            continue
        paragraphs.append(ptxt)
        for m in RE_CK_UPPER.finditer(ptxt):
            findings.append(("ERROR", part_name,
                f"literal “{m.group(0)}” — notation law requires C^K_t — near: “{_snippet(ptxt, m.group(0))}”"))
        for m in RE_CK_LOWER.finditer(ptxt):
            findings.append(("WARN", part_name,
                f"literal “{m.group(0)}” (lowercase subscript on C) — confirm intended — near: “{_snippet(ptxt, m.group(0))}”"))
    return paragraphs


def lint_plain_text(text, findings):
    paragraphs = text.splitlines()
    for ln, line in enumerate(paragraphs, 1):
        for m in RE_CK_UPPER.finditer(line):
            findings.append(("ERROR", f"line {ln}",
                f"literal “{m.group(0)}” — notation law requires C^K_t — near: “{_snippet(line, m.group(0))}”"))
        for m in RE_CK_LOWER.finditer(line):
            findings.append(("WARN", f"line {ln}",
                f"literal “{m.group(0)}” (lowercase subscript on C) — confirm intended"))
    return paragraphs


def check_version(display_name, all_paragraphs, findings, deposit=False):
    fm = RE_FILE_VER.search(display_name)
    if not fm:
        findings.append(("INFO", "version", "no _vX_Y_ version in filename — version check skipped"))
        return
    file_ver = f"{fm.group(1)}.{fm.group(2)}"
    def _cite_marker(p):
        s = p.strip().lstrip("*_# ")
        return s.startswith("Citation") or s.startswith("Suggested Citation")
    cite_idx = next((i for i, p in enumerate(all_paragraphs) if _cite_marker(p)), None)
    if cite_idx is None:
        findings.append(("WARN", "version",
            f"no “Citation.”/“Suggested Citation” paragraph found — cannot confirm filename version v{file_ver} against citation line"))
        return
    cm = RE_CITE_VER.search(all_paragraphs[cite_idx])
    if not cm:
        # heading form: the citation line is the next non-empty paragraph
        for p in all_paragraphs[cite_idx + 1: cite_idx + 4]:
            if not p.strip():
                continue
            cm = RE_CITE_VER.search(p)
            break
    if not cm:
        findings.append(("WARN", "version",
            "Citation marker present but no (vX.Y) found in it or the following line"))
        return
    cite_ver = cm.group(1)
    if cite_ver != file_ver:
        sev = "ERROR" if deposit else "WARN"
        note = "versions must match at deposit" if deposit else "may be deposit-anticipatory per version discipline — adjudicate"
        findings.append((sev, "version",
            f"filename says v{file_ver} but Citation line says (v{cite_ver}) — {note}"))


def lint_target(path, deposit=False):
    findings, all_paragraphs = [], []
    display_name = os.path.basename(os.path.normpath(path))

    if os.path.isdir(path):
        base = path if os.path.isdir(os.path.join(path, "word")) else None
        if base is None:
            return [("ERROR", "input", "directory has no word/ subfolder — not an unpacked docx")], display_name
        candidates = [os.path.join("word", "document.xml"),
                      os.path.join("word", "footnotes.xml"),
                      os.path.join("word", "endnotes.xml")]
        wdir = os.path.join(base, "word")
        candidates += [os.path.join("word", f) for f in sorted(os.listdir(wdir))
                       if re.match(r"(header|footer)\d*\.xml$", f)]
        for rel in candidates:
            full = os.path.join(base, rel)
            if os.path.exists(full):
                with open(full, "rb") as fh:
                    all_paragraphs += lint_xml_part(fh.read(), rel, findings)
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            parts = [p for p in DOC_PARTS if p in names]
            parts += sorted(n for n in names if re.match(r"word/(header|footer)\d*\.xml$", n))
            if "word/document.xml" not in names:
                findings.append(("ERROR", "input", "zip contains no word/document.xml — not a docx"))
            for part in parts:
                all_paragraphs += lint_xml_part(z.read(part), part, findings)
    else:
        # Project-file quirk: plain UTF-8 text carrying a .docx extension
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return [("ERROR", "input", "not a zip, not UTF-8 text — unrecognized file")], display_name
        findings.append(("INFO", "input", "plain UTF-8 text (not a real docx) — text-mode checks only"))
        all_paragraphs = lint_plain_text(text, findings)

    check_version(display_name, all_paragraphs, findings, deposit)
    return findings, display_name


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    deposit = "--deposit" in argv
    targets = [a for a in argv[1:] if a != "--deposit"]
    worst = 0
    for target in targets:
        if not os.path.exists(target):
            print(f"uct_lint: {target}: not found")
            worst = max(worst, 2)
            continue
        findings, name = lint_target(target, deposit)
        errors = [f for f in findings if f[0] == "ERROR"]
        status = "FAIL" if errors else "PASS"
        print(f"[{status}] {name}")
        for sev, part, msg in findings:
            print(f"  {sev:5s} [{part}] {msg}")
        if errors:
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
