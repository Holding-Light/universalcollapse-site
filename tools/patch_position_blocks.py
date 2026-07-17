#!/usr/bin/env python3
"""
patch_position_blocks.py — "Position in the Program" onto landings that
declare relations in site_data.

The operator's design call (2026-07-17): in-card, no extra page, no extra
click. The block sits directly above the Cite box — same visual furniture,
same container — so a reader (or a crawler) who reaches the bottom of a
landing learns where the paper sits: what to read first, what it grounds,
what tests it, and what it must not be read as.

Everything renders from site_data `relations` (closed schema, gated by
check_relations in build_site_meta — every edge is a built slug before this
tool ever runs). Link text is short_title-or-title from the same file. The
authored prose is not read, not matched, not rewritten.

Two marker-wrapped injections per page, both replace-in-place on rerun:
  - a CSS chunk into the page <style> (pos-* classes are outside the
    lint-guarded prefixes; their rules ship with their markup)
  - the HTML section, inserted immediately before the Cite section-label

Dry-run by default; --apply writes; no backups — git is the backup. Refuses
any page whose anchors don't match rather than guessing. Post-apply
verification re-reads the written bytes: marker exactly once per relations
paper, every edge href present, zero markers on papers without relations.

    python3 tools/patch_position_blocks.py
    python3 tools/patch_position_blocks.py --apply
"""
import html as htmlmod
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml")

DATA = "tools/site_data.yaml"
PUB = Path("public")

CSS_BEGIN = "/* position-block: derived by patch_position_blocks.py — edit site_data, rerun */"
CSS_END = "/* /position-block */"
HTML_BEGIN = "<!-- position: derived by patch_position_blocks.py from site_data relations. Edit site_data, rerun; do not hand-edit. -->"
HTML_END = "<!-- /position -->"

RE_CSS_BLOCK = re.compile(re.escape(CSS_BEGIN) + r".*?" + re.escape(CSS_END) + r"\n?", re.S)
RE_HTML_BLOCK = re.compile(re.escape(HTML_BEGIN) + r".*?" + re.escape(HTML_END) + r"\n?", re.S)
RE_CITE_ANCHOR = re.compile(r'^([ \t]*)<div class="section-label">Cite</div>', re.M)
RE_STYLE_END = re.compile(r"^([ \t]*)</style>", re.M)

CSS_RULES = """    .pos-block { background: var(--bg-surface); border: 1px solid var(--rule); padding: 1.5rem 1.6rem; margin-bottom: 2.5rem; }
    .pos-purpose { font-family: var(--serif); font-size: 0.98rem; line-height: 1.75; color: var(--text-secondary); margin-bottom: 1.1rem; }
    .pos-rels { display: grid; grid-template-columns: max-content 1fr; gap: 0.5rem 1.4rem; margin: 0; }
    .pos-rels dt { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); opacity: 0.75; padding-top: 0.2rem; }
    .pos-rels dd { font-family: var(--serif); font-size: 0.95rem; line-height: 1.65; color: var(--text-secondary); margin: 0; }
    .pos-rels dd a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--rule); }
    .pos-rels dd a:hover { border-color: var(--accent); }
    @media (max-width: 560px) { .pos-rels { grid-template-columns: 1fr; gap: 0.2rem; } .pos-rels dd { margin-bottom: 0.6rem; } }"""

FIELD_LABELS = [
    ("read_first", "Read first"),
    ("supports", "Supports"),
    ("tested_by", "Tested by"),
    ("related", "Related"),
]


def esc(t):
    return htmlmod.escape(str(t), quote=True)


def render_block(rel, names, indent):
    rows = []
    for field, label in FIELD_LABELS:
        slugs = rel.get(field) or []
        if not slugs:
            continue
        links = " &middot; ".join(
            f'<a href="/{s}">{esc(names[s])}</a>' for s in slugs)
        rows.append(f"{indent}    <dt>{label}</dt><dd>{links}</dd>")
    dnra = rel.get("do_not_read_as") or []
    if dnra:
        items = " &middot; ".join(esc(x) for x in dnra)
        rows.append(f"{indent}    <dt>Do not read as</dt><dd>{items}</dd>")

    lines = [f"{indent}{HTML_BEGIN}",
             f'{indent}<div class="section-label">Position in the Program</div>',
             f'{indent}<div class="pos-block">']
    if rel.get("purpose"):
        lines.append(f'{indent}  <p class="pos-purpose">{esc(rel["purpose"])}</p>')
    if rows:
        lines.append(f'{indent}  <dl class="pos-rels">')
        lines.extend(rows)
        lines.append(f"{indent}  </dl>")
    lines += [f"{indent}</div>",
              f"{indent}{HTML_END}",
              ""]
    return "\n".join(lines)


def main():
    apply = "--apply" in sys.argv
    d = yaml.safe_load(open(DATA))
    papers = [p for p in d.get("papers", []) if p.get("built")]
    names = {p["slug"]: p.get("short_title") or p["title"] for p in papers}
    with_rel = [p for p in papers if p.get("relations")]

    touched = []
    for p in with_rel:
        slug = p["slug"]
        f = PUB / f"{slug}.html"
        if not f.exists():
            sys.exit(f"FAIL  {slug}: no landing file")
        s = f.read_text(encoding="utf-8")

        cite = RE_CITE_ANCHOR.search(s)
        style_end = RE_STYLE_END.search(s)
        if not cite or not style_end:
            sys.exit(f"FAIL  {slug}: anchor missing "
                     f"(cite={'ok' if cite else 'ABSENT'}, style={'ok' if style_end else 'ABSENT'}) "
                     f"— refusing to guess")

        css_chunk = f"    {CSS_BEGIN}\n{CSS_RULES}\n    {CSS_END}\n"
        if RE_CSS_BLOCK.search(s):
            s = RE_CSS_BLOCK.sub(css_chunk, s, count=1)
        else:
            s = s[: style_end.start()] + css_chunk + s[style_end.start():]

        block = render_block(p["relations"], names, cite.group(1))
        # cite anchor may have moved after CSS insertion — re-find
        cite = RE_CITE_ANCHOR.search(s)
        if RE_HTML_BLOCK.search(s):
            s = RE_HTML_BLOCK.sub(block, s, count=1)
        else:
            s = s[: cite.start()] + block + s[cite.start():]

        touched.append(slug)
        if apply:
            f.write_text(s, encoding="utf-8")

    mode = "APPLIED" if apply else "DRY-RUN (use --apply)"
    print(f"{mode}: {len(touched)} landing(s) with relations -> {touched}")

    if apply:
        # verification on written bytes
        bad = 0
        for p in papers:
            s = (PUB / f"{p['slug']}.html").read_text(encoding="utf-8")
            n = s.count(HTML_BEGIN)
            if p.get("relations"):
                if n != 1:
                    print(f"  VERIFY FAIL {p['slug']}: marker count {n}"); bad += 1; continue
                for field, _ in FIELD_LABELS:
                    for edge in p["relations"].get(field) or []:
                        if f'href="/{edge}"' not in s:
                            print(f"  VERIFY FAIL {p['slug']}: edge /{edge} not rendered"); bad += 1
            elif n:
                print(f"  VERIFY FAIL {p['slug']}: has a position block but no relations"); bad += 1
        if bad:
            sys.exit(f"FAIL  {bad} verification failure(s)")
        print("verified: one block per relations paper, all edges rendered, "
              "zero strays elsewhere")
    return 0


if __name__ == "__main__":
    sys.exit(main())
