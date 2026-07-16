# Session Handoff — universalcollapse.com

**Date:** 2026-07-16 (supersedes the earlier same-day version)
**Status:** Phase 0 COMPLETE · Phase 1 COMPLETE — both deployed and verified live
**Read with:** `CLAUDE.md`, `UCT_Site_Architecture_Blueprint_v1_0_2026_07.md`

---

## 0. Where the site actually is

| | This morning | Now |
|---|---|---|
| Sitemap | 8 URLs (18 pages live) | **38** — every page mapped |
| Read pages | 1 of 17 | **17 of 17**, all 200 |
| llms.txt | 404 | live; carries the kernel grammar + anti-reification guard |
| Canonical gaps | 4 | **1** (`architecture.html`) |
| Landing CTA | 16 → off-site PhilArchive | **17 → local `/read/{slug}`** |
| PDF buttons | 2 | **17** (2 local, 15 archive-linked until export) |
| Lint gates | none | 4 independent |

An AI could quote exactly one of the papers this morning. It can now quote seventeen.

---

## 1. Decisions locked this session (operator-adjudicated)

**1.1 — Canonical: Option A.** Read pages self-canonicalise. `tools/uct-paper.html`
emits `<link rel="canonical" href="$public_url$">`. This REVERSED a deliberate
earlier choice (`$landing_url$`). Rationale: Scholar indexes off the landing's
`citation_*` tags → PDF regardless, so self-canonical reads don't harm Scholar;
they let the full text be indexed for everything else. Landing and read are not
duplicates — a 290-word abstract vs an 80K paper — so canonical was suppressing
the better page rather than deduplicating anything.

**1.2 — Records source: `UCT_Standards_Records_v2.0_2026_04.docx`.** Two candidates
existed in `Standards/`; the other was `..._Records_Across_the_Stack_v1.0_...`
(different title, v1.0). Registry says Records is Live (v2.0) at `7H6DY`.
Operator confirmed.

**1.3 — PDF routing: local-first, always.** `Download PDF` points at same-origin
`/pdf/`. Independence is the DOI's job, not the download button's; third-party
standing lives in the cite-box archival line (`PhilArchive · OSF`). This
CONTRADICTS the DOI Registry's routing principle — see §5.1.

**1.4 — Rice/COGITATE dates: 2026/04** (both deposited 2026-04-02). Operator-
confirmed; the filenames carry no date and nothing else recorded one.

---

## 2. The toolchain (all in `tools/`)

| Script | Does | Notes |
|---|---|---|
| `build_paper.sh` | docx → read page | pandoc + **SRC_SHA256 guard** + built-in lint |
| `make_envs.py` | site_data + docx library → env files | propose-then-approve; `--harvest-subtitles` |
| `set_src_files.py` | writes the 16 adjudicated docx mappings | run once; values read off disk |
| `build_site_meta.py` | site_data → sitemap.xml + llms.txt | Rule 3 |
| `uct_lint_html.py` | web gate: notation, encoding, canonical, citation tags | `--papers-from site_data.yaml` |
| `check_operator.py` | **structural** operator check (MathML/Unicode) | lint reads text; this reads structure |
| `check_conversion.py` | docx OMML vs built HTML | distinguishes "not used" from "pandoc ate it" |
| `patch_pdf_button.py` | CTA secondary button + CSS | **re-targets to local as PDFs land** |
| `patch_landings.py` | one-shot CTA migration | **DONE. Do not re-run.** Holds a stale hardcoded PDF map. |

Standard verification pass:
```bash
python3 tools/uct_lint_html.py --landing --papers-from tools/site_data.yaml \
  public/*.html public/read/*.html public/roadmap/*.html
python3 tools/check_operator.py public/read/*.html
python3 tools/check_conversion.py tools/*.env
```

---

## 3. Verified facts (checked, not recalled)

- **Notation is intact across all 17.** 0 structural violations. `check_conversion`
  proves nothing was dropped: collapse_reframed 8 OMML → 51 math, wp01 26 → 163,
  wp02 35 → 340.
- **wp03 and soai warn "prose names the operator, no symbol."** Verified against
  their own docx: `omml=0` at source. Those papers discuss the operator without
  typesetting it. Correct as warnings, not errors.
- **wp01 uses `C^K` (19 × `msup`), not `C^K_t`.** Time-suppressed shorthand,
  explicitly licensed by the Symbols Reference. Its `msubsup` blocks are `x*_t`.
- **iCloud does not touch bytes.** Kernel First's docx sat in iCloud since June,
  moved folders, and still hashes to its recorded value. Zero `.icloud`
  placeholders in the library.
- **`citation_pdf_url` is on exactly 2 of 17 because exactly 2 PDFs exist.** Not
  drift — the pages were always honest.

---

## 4. Gotchas that cost real time today

- **`~/Desktop/Papers/T0 &AG/`** — `&` is a sed metacharacter. sed expanded it
  into the whole matched line and corrupted an env. **Use Python for any edit
  touching these paths.**
- **The operator is U+1D37**, not U+1D30. A checker looking for U+1D30 reported
  "no operator present" on a page carrying six correct ones.
- **Version separators are inconsistent**: 12 papers use `v1.0` (dots), 3 use
  `v1_0`. Any filename regex must accept `[._]`.
- **zsh does not honour `#` comments interactively.** Pasted comment lines error.
- **`Trash/` outranked real files.** The matcher suggested
  `Trash/Update_Integrity_Standard_UIS_v1.0_2026-01-30.docx` for a paper live at
  `DWM29`, and offered a `_REJECTED_NOT_LIVE.docx` as a candidate. `make_envs.py`
  now excludes Trash/drafts/copies. **Never auto-accept a suggestion.**
- **pandoc resolves a bare `--template=` against its own data dir**, not `tools/`.
  Every env now carries `TEMPLATE="tools/uct-paper.html"`.

---

## 5. Open — none blocking

**5.1 — DOI Registry contradicts the site (OPERATOR CALL).**
Registry v2.3 routing principle: *"Website → paper links (PhilArchive available)
→ PhilArchive."* All 17 landings now route to local `/read/`. The registry was
written before read pages existed. **Two records of the same fact disagree** —
precisely what UIS (`DWM29`) exists to prevent. Update the registry or revert the
site; do not leave both standing.

**5.2 — Registry PCN error.** v2.3 states twice that the Provenance Clarification
Note (`7NVMX`) is appended to S3-RAG-01. The deposited note's own header says
**JPXCU**. Second error traced to the July 2026 conversion pipeline (first: the
EAR §2.1 false verification claim).

**5.3 — 15 PDF exports.** Names are recorded in `site_data.yaml` as `pdf_file`.
Drop each into `public/pdf/`, then `python3 tools/patch_pdf_button.py --apply` —
the button re-targets to local automatically (verified by simulation). Each export
also clears a `citation_pdf_url` warning. **The PDF path has NO hash guard**,
unlike read pages. Recording each PDF's SHA in site_data and lint-checking it
would close the last unguarded artifact on the site.

**5.4 — `architecture.html`.** Last lint error (no canonical) AND renders **16
words** without JS — a compiled React bundle, so every AI crawler sees a blank
page. It is one of three homepage doors. Both fixes go in the HTML shell, not the
deployed file. Source: `UCT_Architecture_Map_v4.jsx`; procedure in
`Session_Handoff_Architecture_Map_2026_06_29.md`. **Do not hand-edit
`public/architecture.html`.**

**5.5 — §7.2 landing prose.** See CLAUDE.md §6 — reframed, mostly dissolved.

**5.6 — `patch_landings.py` stale map.** Job done; it holds a hardcoded 2-entry
PDF map that now duplicates `site_data`'s `pdf_file`. Delete or gut it.

---

## 6. Claims falsified this session — do not re-inherit

Six of the assistant's own claims died to artifacts today. None died to argument.
Listed so they are not re-derived from the same bad reasoning:

1. *"citation_pdf_url drift"* → 2 tags, 2 PDFs, exact match. Never drift.
2. *"Landings are 14K of authored prose"* → **290 words.** 83% is boilerplate.
3. *"Landings are hand-written by the operator"* → model-generated, operator-
   approved. Provenance is not in the bytes; only the operator knew.
4. *CIM filename* → guessed `..._PUBLIC.docx` twice; disk says
   `UCT_T15_CIM_Foundational_v1.0_2026_05.docx`.
5. *Date regex assumed `v2_0`* → corpus uses `v2.0`. 13 of 16 envs got `DATE=""`.
6. *Operator codepoint U+1D30* → corpus uses **U+1D37**. The notation checker was
   blind to the notation, and the lint would have PASSED a page that lost it.

Also corrected: another model's confident *"sitemap 404"* (it was 200, always) and
a third model's *"cache-miss on /library, /roadmap, /architecture"* (the first two
are healthy; `/architecture` has a real but different problem — see 5.4).

**Standing rule:** multiple models reading the same stale file is one channel
wearing two hats. See the operator's own Methods-S₁, *Auditing Independence in
Multi-Channel Measurement* (`7U8SK`). A second opinion only counts if it touched
the artifact independently.

---

*Verified against production 2026-07-16. Where this file and a project-file copy
disagree, re-verify against the live site or the repo.*
