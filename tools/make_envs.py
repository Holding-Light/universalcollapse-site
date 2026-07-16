#!/usr/bin/env python3
"""
make_envs.py — generate build_paper.sh env files from site_data.yaml + the docx library.

TWO PHASES, deliberately. This script proposes; the operator approves; then it writes.
Guessing which docx produced a deposit is exactly how wrong bytes end up under a DOI.

    python3 tools/make_envs.py --inventory          # propose. writes nothing.
    python3 tools/make_envs.py --write              # emit envs for CONFIDENT matches only
    python3 tools/make_envs.py --write --slug wp01  # or one at a time

Rules honored:
  - Ambiguous match (2+ candidate docx) -> REPORT, never pick. Operator adjudicates.
  - No match -> REPORT. Never invent a path.
  - SHA is computed from the file found, and recorded. build_paper.sh enforces it later.
  - TIER uses &middot; (HTML entity) not the literal middot — the pandoc path mangles
    the UTF-8 byte pair into 2x U+FFFD. Proven: the hand-written landing uses the
    entity and is clean; every pandoc output using the literal is corrupt.
  - Paths are written quoted. The library contains 'T0 &AG' — spaces and ampersands
    both. Never use sed on these.

NOT handled here (deliberately):
  - The canonical policy is a TEMPLATE change (tools/uct-paper.html), not an env
    change. Make that edit ONCE before the batch, or every read page builds twice.
  - SUBTITLE is not derivable from site_data.yaml. Emitted blank; fill if wanted.
    build_paper.sh treats it as optional.
"""
import argparse
import glob
import hashlib
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml:  pip install pyyaml")

PAPERS_DIR = os.path.expanduser("~/Desktop/Papers")
BASE = "https://universalcollapse.com"

# Directories that never contain a deposited record. Non-negotiable: on the first
# real run the matcher SUGGESTED Trash/Update_Integrity_Standard_UIS_v1.0_2026-01-30.docx
# for a paper live at DOI DWM29, and offered a file literally named
# ..._SUBMITTED_REJECTED_NOT_LIVE.docx as a candidate.
EXCLUDE_DIRS = {"Trash", "trash", ".Trash", "Archive", "archive", "Old", "old", "Drafts", "drafts"}

# Filename markers that mean "not the deposit"
EXCLUDE_MARKERS = re.compile(
    r"\bcopy\b|\bcopy \d|_streamlined|_REJECTED|_NOT_LIVE|_SUBMITTED|_DRAFT|_draft|_final_\d",
    re.I,
)


def version_of(fn):
    """Parse vX.Y or vX_Y from a filename -> (X, Y). Unparseable sorts last."""
    m = re.search(r"_v(\d+)[._](\d+)", Path(fn).stem)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def is_excluded(path):
    parts = set(Path(path).parts)
    if parts & EXCLUDE_DIRS:
        return "in an excluded directory"
    if EXCLUDE_MARKERS.search(Path(path).name):
        return "filename marks it as not-the-deposit"
    return None


def norm_tokens(s):
    """Lowercase alnum tokens, dropping noise that appears on one side only."""
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    drop = {"uct", "the", "a", "an", "of", "and", "in", "v1", "v2", "0", "1", "2",
            "docx", "universal", "collapse", "theory", "wp01", "wp02", "wp03"}
    return [t for t in s.split() if t not in drop and len(t) > 1]


def score(title, filename):
    """Token overlap, normalised by the shorter side. 1.0 = every token of one
    appears in the other."""
    a, b = set(norm_tokens(title)), set(norm_tokens(Path(filename).stem))
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def date_from_filename(fn):
    """Extract YYYY/MM from the filename.

    The house convention is DOTS in version numbers: _v2.0_2025_11_11. An earlier
    regex here assumed underscores (_v2_0_) and silently produced DATE="" for 13 of
    16 papers — build_paper.sh requires DATE and halts. Both forms are in the
    library, and dates appear with _ or - separators.

        UCT_WP01_..._v2.0_2025_11_11.docx   -> 2025/11
        UCT_T15_Collapse_Reframed_v1.0_2026-02-12.docx -> 2026/02
        UCT_T15_..._v1_0_2026_06.docx       -> 2026/06
        UCT_T16_Bio_Constraint_Sweep_Rice_FINAL.docx -> "" (needs date: in site_data)
    """
    m = re.search(r"_v\d+[._]\d+[_-](\d{4})[_-](\d{2})", Path(fn).stem)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    # no version-anchored date: try a bare YYYY_MM / YYYY-MM tail
    m = re.search(r"[_-](\d{4})[_-](\d{2})(?:[_-]\d{2})?$", Path(fn).stem)
    return f"{m.group(1)}/{m.group(2)}" if m else ""


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_pdf(slug, papers):
    """A PDF only exists for some papers. Only 2 of 17 today. Empty is fine —
    the read template emits no citation tags, so an empty PDF_URL ships nothing."""
    p = next((x for x in papers if x["slug"] == slug), None)
    return f"{BASE}/pdf/{p['pdf_file']}" if p and p.get("pdf_file") else ""


def classify(paper, docs, papers_dir):
    """-> (status, [candidates]).  confident | ambiguous | missing

    AUTHORITATIVE PATH: `src_file` in site_data.yaml. If present, it is used and
    fuzzy matching never runs. This is Rule 3 doing its job — the single source
    should carry the source filename, not make a script guess it.

    Fuzzy matching is a SUGGESTION ENGINE for the inventory pass only. It scored
    3/16 on a replica library: docx filenames use short forms ('Records') while
    titles are long ('Records Across Nature, Life, and Mind'), and the overlap
    ratio collapses. Do not trust it to write anything.
    """
    if paper.get("src_file"):
        hits = [d for d in docs if Path(d).name == paper["src_file"]]
        if len(hits) == 1:
            return "confident", hits
        if len(hits) > 1:
            return "ambiguous", hits          # same filename in two folders
        return "missing", []                  # named file not found — do not fall back

    scored = sorted(((score(paper["title"], d), d) for d in docs), reverse=True)
    if not scored or scored[0][0] < 0.45:
        return "missing", []
    top = scored[0][0]
    near = [d for s, d in scored if s >= top - 0.10 and s >= 0.45]
    # Newest version first — the deposit is almost never v0.3. This orders the
    # operator's shortlist; it does NOT decide anything.
    near.sort(key=version_of, reverse=True)
    if len(near) > 1:
        return "ambiguous", near
    return "suggested", [scored[0][1]]        # NOT confident — needs src_file to build


def env_text(paper, docpath, sha):
    tier = paper.get("tier", "")
    # Encoding law: entity, never the literal. See module docstring.
    tier_html = tier.replace("—", "&mdash;").replace("·", "&middot;")
    if "·" not in tier and "&middot;" not in tier_html:
        tier_html = f"{tier_html} &middot; {paper.get('tier_note','')}".strip(" &middot;")
    date = date_from_filename(docpath) or paper.get("date", "")
    desc = " ".join(paper.get("desc", "").split())
    # Version baseline: every paper is v1.0 EXCEPT WP01 and Records, which are v2.0.
    # Never hardcode — a wrong version in CITATION_TITLE is a wrong citation.
    version = paper.get("version", "1.0")
    subtitle = paper.get("subtitle", "").replace('"', "'")
    short = paper.get("short_title") or paper["title"].split(":")[0].split("—")[-1].strip()
    return f'''SRC="{docpath}"
SRC_SHA256="{sha}"
FROM="docx"
OUT="public/read/{paper['slug']}.html"
TIER="{tier_html}"
TITLE="{paper['title']}"
SUBTITLE="{subtitle}"
CITATION_TITLE="{paper['title']} (v{version})"
DATE="{date}"
DOI="10.17605/OSF.IO/{paper['doi']}"
PDF_URL="{paper.get('pdf_url','')}"
PUBLIC_URL="{BASE}/read/{paper['slug']}"
LANDING_URL="{BASE}/{paper['slug']}"
DESCRIPTION="{desc}"
SHORT_TITLE="{short}"
'''


def harvest_subtitles(papers, public_dir):
    """Subtitles already exist — the landing pages carry them in <p class="paper-sub">.
    Nothing to author; this is extraction. Returns {slug: subtitle}."""
    import html as htmllib
    found = {}
    for p in papers:
        f = Path(public_dir) / f"{p['slug']}.html"
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'<p class="paper-sub">(.*?)</p>', s, re.S)
        if not m:
            continue
        text = re.sub(r"<[^>]+>", "", m.group(1))
        text = htmllib.unescape(" ".join(text.split()))
        if text:
            found[p["slug"]] = text
    return found


def apply_subtitles(data_path, subs):
    """Insert `subtitle:` after each `- slug:` line. Line-surgery, not yaml.dump —
    dumping would strip every comment out of site_data.yaml."""
    lines = Path(data_path).read_text(encoding="utf-8").split("\n")
    out, n = [], 0
    for line in lines:
        out.append(line)
        m = re.match(r"^  - slug: (\S+)\s*$", line)
        if m and m.group(1) in subs:
            slug = m.group(1)
            if not any(f'subtitle:' in l and lines[i-1].strip().endswith(slug)
                       for i, l in enumerate(lines)):
                esc = subs[slug].replace('"', '\\"')
                out.append(f'    subtitle: "{esc}"')
                n += 1
    Path(data_path).write_text("\n".join(out), encoding="utf-8")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="tools/site_data.yaml")
    ap.add_argument("--papers-dir", default=PAPERS_DIR)
    ap.add_argument("--out-dir", default="tools")
    ap.add_argument("--inventory", action="store_true", help="propose only; write nothing")
    ap.add_argument("--write", action="store_true", help="emit envs for confident matches")
    ap.add_argument("--slug", help="restrict to one slug")
    ap.add_argument("--harvest-subtitles", action="store_true",
                    help="pull subtitles from the existing landing pages (they already have them)")
    ap.add_argument("--apply", action="store_true", help="with --harvest-subtitles: write into site_data.yaml")
    ap.add_argument("--public-dir", default="public")
    a = ap.parse_args()

    if not (a.inventory or a.write or a.harvest_subtitles):
        ap.print_help(); return 2

    d = yaml.safe_load(open(a.data))
    papers = [p for p in d.get("papers", []) if p.get("built") and not p.get("read")]
    if a.slug:
        papers = [p for p in papers if p["slug"] == a.slug]

    if a.harvest_subtitles:
        allp = [x for x in d.get("papers", [])]
        subs = harvest_subtitles(allp, a.public_dir)
        print(f"harvested {len(subs)} subtitles from {a.public_dir}/*.html\n")
        for k, v in subs.items():
            print(f'  {k:<18} "{v[:72]}{"…" if len(v) > 72 else ""}"')
        missing = [p["slug"] for p in allp if p["slug"] not in subs]
        if missing:
            print(f"\n  no paper-sub found for: {', '.join(missing)}")
        if a.apply:
            n = apply_subtitles(a.data, subs)
            print(f"\n  wrote {n} subtitle fields into {a.data}")
        else:
            print("\n  review only — re-run with --apply to write into site_data.yaml")
        return 0

    docs = glob.glob(os.path.join(a.papers_dir, "**", "*.docx"), recursive=True)
    docs = [x for x in docs if not Path(x).name.startswith("~$")]  # Word lock files
    raw = len(docs)
    excluded = [(x, is_excluded(x)) for x in docs]
    docs = [x for x, why in excluded if not why]
    n_trash = sum(1 for _, why in excluded if why)
    print(f"site_data: {len(papers)} papers needing read pages")
    print(f"library:   {raw} docx found, {n_trash} excluded (Trash/drafts/copies), "
          f"{len(docs)} eligible\n")
    if not docs:
        sys.exit(f"no eligible docx under {a.papers_dir} — check the path")

    buckets = {"confident": [], "suggested": [], "ambiguous": [], "missing": []}
    for p in papers:
        status, cands = classify(p, docs, a.papers_dir)
        buckets[status].append((p, cands))

    for p, c in buckets["confident"]:
        print(f"  OK        {p['slug']:<18} -> {Path(c[0]).parent.name}/{Path(c[0]).name}")
    for p, c in buckets["suggested"]:
        print(f"  SUGGEST   {p['slug']:<18} ?  {Path(c[0]).parent.name}/{Path(c[0]).name}")
    for p, c in buckets["ambiguous"]:
        print(f"  AMBIGUOUS {p['slug']:<18} -> {len(c)} candidates — OPERATOR MUST CHOOSE:")
        for x in c:
            print(f"                                  {Path(x).parent.name}/{Path(x).name}")
    for p, _ in buckets["missing"]:
        print(f"  MISSING   {p['slug']:<18} -> no src_file, and no confident guess")

    print(f"\n  confident {len(buckets['confident'])}  suggested {len(buckets['suggested'])}"
          f"  ambiguous {len(buckets['ambiguous'])}  missing {len(buckets['missing'])}")

    if a.inventory:
        claimed = {Path(c[0]).name for _, c in buckets["confident"] + buckets["suggested"]}
        loose = sorted(Path(d).name for d in docs if Path(d).name not in claimed)
        if loose:
            print(f"\n  {len(loose)} docx in the library not mapped to any paper:")
            for x in loose[:40]:
                print(f"    {x}")
        print("\n  Only `confident` builds. To make a paper confident, add to site_data.yaml:")
        print("      src_file: \"UCT_WP01_Foundations_of_Collapse_v2_0_2025_11_11.docx\"")
        print("  Fuzzy matching is a suggestion engine only (it scored 3/16 on a replica).")
        print("  Nothing written.")
        return 0

    print()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    needs_date = [p["slug"] for p, c in buckets["confident"]
                  if not (date_from_filename(c[0]) or p.get("date"))]
    if needs_date:
        print("  STOP — build_paper.sh requires DATE, and these have no date in the")
        print("  filename and no `date:` in site_data.yaml:")
        for s_ in needs_date:
            print(f"      {s_}")
        print("  Add to site_data.yaml under the slug:   date: \"2026/04\"")
        print("  Nothing written.")
        return 1

    for p, c in buckets["confident"]:
        src = c[0]
        sha = sha256(src)
        f = out / f"{p['slug']}.env"
        if f.exists():
            print(f"  SKIP  {f} exists — not overwriting"); continue
        f.write_text(env_text(p, src, sha), encoding="utf-8")
        print(f"  wrote {f}   sha {sha[:16]}…")

    if buckets["ambiguous"] or buckets["missing"]:
        print(f"\n  {len(buckets['ambiguous']) + len(buckets['missing'])} paper(s) NOT written — "
              f"they need an operator decision, not a default.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
