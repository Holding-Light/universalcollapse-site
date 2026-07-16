# Session Handoff — universalcollapse.com

**Date:** 2026-07-16 · **Status:** Phase 0 COMPLETE · Phase 1 COMPLETE — deployed, verified live
**Load this at the start of a new session.** It is the site's state of record.
**Read with:** `CLAUDE.md` (repo root), `UCT_Site_Architecture_Blueprint_v1_0_2026_07.md`

---

## 1. WHAT THIS IS

`~/universalcollapse-site` → github.com/Holding-Light/universalcollapse-site (branch `main`)
Cloudflare Workers · web root is **`public/`** · deploy = `git push` (~1–2 min)

The public face of the UCT research program. **It is not the record** — OSF holds
the records, each with a permanent DOI. The site renders them.

Three audiences, one landing page per paper:
- **human** → `Read →` (full text on-site) or `Download PDF` (same-origin)
- **Google Scholar** → `citation_*` tags in `<head>` → follows `citation_pdf_url` → indexes
- **AI crawler** → `/read/{slug}`, self-canonical, 80K clean HTML, notation intact

---

## 2. WHERE IT STANDS (verified 2026-07-16, not recalled)

| | Start of session | Now |
|---|---|---|
| Sitemap | 8 URLs (18 pages live) | **38** — every page mapped |
| Read pages (full text) | 1 of 17 | **17 of 17**, all 200, self-canonical |
| PDFs on site | 2 | **17**, all same-origin, **all SHA-recorded** |
| Scholar-indexable | 2 | **17** (`citation_pdf_url` on every landing) |
| Landing CTA | 16 → off-site PhilArchive | **17 → local** `/read/` + `Download PDF` |
| llms.txt | 404 | live; kernel grammar + anti-reification guard |
| Canonical gaps | 4 | **1** (`architecture.html`) |
| Lint gates | 0 | **4** independent |

Lint: **20 pages, 1 error, 1 warning.** The error is `architecture.html`; the
warning is the operator note on wp03/soai (correct — verified against source).

Notation intact across all 17. `check_conversion` proves nothing was dropped:
collapse_reframed 8 OMML → 51 math, wp01 26 → 163, wp02 35 → 340.

---

## 3. WHAT'S NEXT (priority order)

**3.1 — Registry contradicts the site. OPERATOR CALL. Do not let this sit.**
DOI Registry v2.3 routing principle: *"Website → paper links (PhilArchive
available) → PhilArchive."* All 17 landings now route to local `/read/` and
local `/pdf/`. The registry predates the read pages. **Two records of the same
fact disagree** — exactly what UIS (`DWM29`) exists to prevent, in the author's
own records. Update the registry or revert the site. Don't leave both.

**3.2 — Registry PCN error.** v2.3 says twice that the Provenance Clarification
Note (`7NVMX`) is appended to S3-RAG-01. The deposited note's own header says
**JPXCU**. This is the *second* error traced to the July 2026 conversion pipeline
(first: EAR §2.1 false verification claim). Two findings, same pipeline — raises
the registry's own "verification-claim spot-check" item from prudence to pattern.

**3.3 — `architecture.html`.** Last lint error (no canonical) AND renders **16
words** without JS — a compiled React bundle, so every AI crawler sees a blank
page. One of three homepage doors. Both fixes go in the **HTML shell**, never the
deployed file. Source: `UCT_Architecture_Map_v4.jsx`; procedure in
`Session_Handoff_Architecture_Map_2026_06_29.md`.
**Do not hand-edit `public/architecture.html`.**

**3.4 — Phase 1 backlog: 27 live DOIs with no page.** Listed in `site_data.yaml`.
Not 27 papers — `YNG6M` is a container, the 4 Starter Packs are runnable code,
and `7NVMX` belongs *on* the ai_sig_deployed landing, not beside it. Real number
≈ 20. Each needs a landing (see CLAUDE.md §6) + a read page (mechanical).

**3.5 — `patch_landings.py` stale map.** Job done; holds a hardcoded 2-entry PDF
map that now duplicates `site_data`'s `pdf_file`. Delete or gut it.

---

## 4. HOW TO WORK

### Adding paper #18
```bash
# 1. add to tools/site_data.yaml: slug, title, subtitle, doi, tier, src_file,
#    pdf_file, version, desc, philarchive (or null), built: true, read: true
# 2. env + build + verify
python3 tools/make_envs.py --inventory     # confirm the docx maps
python3 tools/make_envs.py --write
bash tools/build_paper.sh tools/{slug}.env # hash guard runs here
python3 tools/import_pdfs.py --apply       # copies from ~/Desktop/Papers/Published pdf
python3 tools/patch_pdf_button.py --apply
python3 tools/patch_citation_pdf.py --apply
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/
# 3. gate
python3 tools/uct_lint_html.py --landing --papers-from tools/site_data.yaml \
  public/*.html public/read/*.html public/roadmap/*.html
python3 tools/check_operator.py public/read/*.html
python3 tools/check_conversion.py tools/*.env
python3 tools/import_pdfs.py --verify
rm -f public/*.html.bak && git add -A && git commit -m "..." && git push
```
The landing itself is the one part with no generator — see CLAUDE.md §6.

### The toolchain (`tools/`)
| Script | Does |
|---|---|
| `build_paper.sh` | docx → read page. pandoc + **SRC_SHA256 guard** + built-in lint |
| `make_envs.py` | site_data + docx library → envs. Propose-then-approve. `--harvest-subtitles` |
| `set_src_files.py` | the 16 adjudicated docx mappings. Run-once; values read off disk |
| `import_pdfs.py` | published PDFs → `public/pdf/` under web names. Records `pdf_sha256`. `--verify` |
| `build_site_meta.py` | site_data → sitemap.xml + llms.txt |
| `uct_lint_html.py` | web gate: notation, encoding, canonical, citation tags, sitemap agreement |
| `check_operator.py` | **structural** operator check — lint reads text, this reads MathML |
| `check_conversion.py` | docx OMML vs built HTML — "not used" vs "pandoc ate it" |
| `patch_pdf_button.py` | CTA secondary button + CSS. Re-targets to local as PDFs land |
| `patch_citation_pdf.py` | `citation_pdf_url` where the PDF exists. Never points at a 404 |
| `patch_landings.py` | one-shot CTA migration. **DONE — do not re-run** |

---

## 5. DECISIONS LOCKED (do not relitigate without cause)

**Canonical: Option A.** Read pages self-canonicalise (`$public_url$`). This
REVERSED a deliberate earlier choice. Landing and read are not duplicates —
290-word abstract vs 80K paper — so canonical was suppressing the better page,
not deduplicating. Scholar indexes off the landing's tags → PDF regardless.

**PDF routing: local-first, always.** Independence is the DOI's job, not the
download button's. Third-party standing lives in the cite-box archival line
(`PhilArchive · OSF`). Same-origin PDFs are what `citation_pdf_url` needs.

**Records source:** `UCT_Standards_Records_v2.0_2026_04.docx` (not
`..._Records_Across_the_Stack_v1.0_...`). Registry: Live (v2.0) at `7H6DY`.

**Rice/COGITATE dates:** 2026/04 — both deposited 2026-04-02. Operator-confirmed;
no filename carries a date.

**Version law:** all papers v1.0 EXCEPT WP01 and Records (v2.0). In `site_data`
as `version:`. Never hardcode.

---

## 6. GOTCHAS THAT COST REAL TIME

- **`~/Desktop/Papers/T0 &AG/`** — `&` is a sed metacharacter; sed expanded it
  into the whole matched line and corrupted an env. **Python for any edit
  touching these paths.**
- **The operator is U+1D37**, not U+1D30. A checker looking for U+1D30 reported
  "no operator present" on a page carrying six correct ones.
- **Version separators are inconsistent**: 12 papers `v1.0` (dots), 3 `v1_0`.
  Any filename regex must accept `[._]`.
- **`Trash/` outranks real files.** The matcher suggested
  `Trash/Update_Integrity_Standard_UIS_v1.0_2026-01-30.docx` for a paper live at
  `DWM29`, and offered `..._REJECTED_NOT_LIVE.docx` as a candidate.
  `make_envs.py` excludes Trash/drafts/copies. **Never auto-accept a suggestion.**
- **pandoc resolves a bare `--template=` against its own data dir**, not `tools/`.
  Every env carries `TEMPLATE="tools/uct-paper.html"`.
- **Cloudflare caches HTML aggressively.** Three times today a fresh deploy read
  stale via curl and looked like a bug. Bust it:
  `curl -s "https://universalcollapse.com/records?cb=$(date +%s)"`
- **zsh does not honour `#` comments interactively.** Pasted comment lines error.
- **iCloud does not touch bytes** — verified. Kernel First's docx sat in iCloud
  since June, moved folders, still hashes to its recorded value.

---

## 7. CLAIMS FALSIFIED THIS SESSION — do not re-inherit

Six of the assistant's own claims died to artifacts. **None to argument.**

1. *"citation_pdf_url drift"* → 2 tags, 2 PDFs, exact match. Never drift.
2. *"Landings are 14K of authored prose"* → **290 words.** 83% is boilerplate.
3. *"Landings are hand-written by the operator"* → model-generated, operator-
   approved. Provenance is not in the bytes; only the operator knew.
4. *CIM filename* → guessed `..._PUBLIC.docx` twice; disk says
   `UCT_T15_CIM_Foundational_v1.0_2026_05.docx`.
5. *Date regex assumed `v2_0`* → corpus uses `v2.0`. 13 of 16 envs got `DATE=""`.
6. *Operator codepoint U+1D30* → corpus uses **U+1D37**. A tool built to enforce
   the notation law was blind to the notation; the lint would have PASSED a page
   that lost its operator entirely.

Also corrected: another model's confident *"sitemap 404"* (it was 200, always)
and a third model's *"cache-miss on /library, /roadmap, /architecture"* (the
first two are healthy; `/architecture` has a real but different problem — §3.3).

**Standing rule:** multiple models reading the same stale file is one channel
wearing two hats. See Methods-S₁, *Auditing Independence in Multi-Channel
Measurement* (`7U8SK`). A second opinion only counts if it touched the artifact
independently.

**What the guards caught today** — each would have shipped silently: a trashed
UIS about to build under a live DOI; a v1.9 draft beside a v2.0 deposit;
`Rice.pdf` beside `Rice_FINAL.pdf`; a `_REJECTED_NOT_LIVE.docx` offered as a
candidate; a stale `SRC` path after the Papers/ reorg; `DATE=""` on 13 envs; and
wp02's PDF in the wrong folder — where "missing" was the right answer instead of
a confident wrong match.

---

*Verified against production 2026-07-16. Where this file and a project-file copy
disagree, re-verify against the live site or the repo — not against the copy.*
