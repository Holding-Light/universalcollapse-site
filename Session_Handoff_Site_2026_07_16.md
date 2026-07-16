# Session Handoff — universalcollapse.com Phase 0

**Date:** 2026-07-16
**Scope:** Site Blueprint v1.0 Phase 0 — verified against production, not asserted.
**Read with:** `CLAUDE.md` (site repo root), `UCT_Site_Architecture_Blueprint_v1_0_2026_07.md`

---

## 0. Why this file exists

Everything below was established in a chat session and none of it is in the repo.
It includes two corrections to documents that are currently wrong, and three
decisions reserved to the operator. Read this before acting on the blueprint.

**Method note:** every claim here was checked against an artifact — an HTTP status,
a byte, a SHA, a diff. Where a claim could not be checked, it is marked UNKNOWN.
Two prior claims from a different model's session are corrected below; both were
stated confidently and both were wrong on contact with curl.

---

## 1. Live state, verified 2026-07-16

| Check | Result |
|---|---|
| `sitemap.xml` | **200**, 8 URLs |
| Paper landing pages | **17 live, all 200** |
| Read pages | **1 of 17.** `/read/kernel_first` 200; other 16 → **404** |
| `llms.txt` | **404** — does not exist |
| `robots.txt` | 200 — open to all crawlers, declares the sitemap |
| `.html` variants | **307** → extensionless (clean) |
| `/kernelfirst`, `/read/kernelfirst` | **301** → underscore slugs (migration done correctly) |
| Landing `rel=canonical` | all **self** ✓ |
| `/read/kernel_first` `rel=canonical` | → `/kernel_first` (the **landing**) |
| `citation_pdf_url` on landings | **2 of 17** (kernel_first, wp01) |
| Notation in live read HTML | **clean** — 0 violations, 6 correct `Cᴷ`, 0 mangled |
| Encoding on `/read/kernel_first` | **2× U+FFFD** — `Tier 0 �� Gateway` |
| site_data DOIs vs live `citation_doi` tags | **17/17 match** (independent of transcription) |

### The headline finding — not on the blueprint's register

**The sitemap lists 8 URLs. 18 pages are live.** All 17 landings return 200;
only 3 are in the sitemap (kernel_first, wp01, wp02). **14 live pages are
invisible to crawlers via the sitemap.**

Context: Cloudflare reports `sitemap.xml` as the single most-crawled path
(15 successful hits in the reporting period, 19 requests from Amazonbot). Crawl
budget is being spent on a map that hides most of the site. This is the highest-
value fix in Phase 0 and it is one file.

---

## 2. Corrections to existing documents

### 2.1 — Site Blueprint Phase 0 register: "sitemap 404 VERIFY" is FALSE

`sitemap.xml` returns 200 and always did. The 404 originated in another model's
`web_fetch` and was written into the register as a finding. curl says 200; every
one of its 8 URLs resolves 200.

**The real defect is the inverse**: not broken URLs — missing ones (§1).

Also in the register: "sitemap `.html` mismatch." Live sitemap is **already
extensionless and correct**. The `.html` version is a stale copy in project files.
Live is correct in *form*, incomplete in *coverage*.

**Action:** strike both lines on next blueprint touch; replace with the coverage
finding.

### 2.2 — The template copy in project files is OLDER than production

`uct-paper.html` in project files: SHA `6409998e31d1802d`.
Recorded in memory: `0332b7cfe9ef4297`. Mismatch.

It is not merely stale — it is the **previous generation**. It emits
`<link rel="canonical" href="$public_url$">`, which matches the *older* build
(`kernelfirst.html`, self-canonical). Production emits `$landing_url$`.

**Any reasoning done against that copy is reasoning against a superseded file.**
The repo is authoritative.

---

## 3. The canonical question — SOLVED, and it was a decision

Three read-page generations exist as loose files in `~/Downloads`:

| File | `rel=canonical` | Generation |
|---|---|---|
| `kernelfirst.html` | `/read/kernelfirst` | **self** — old template, `$public_url$` |
| `read_kernelfirst.html` | `/kernelfirst` | landing — `$landing_url$`, old slug |
| `read_kernel_first.html` | `/kernel_first` | landing — `$landing_url$`, current |

The env proves the mechanism:
```
PUBLIC_URL="https://universalcollapse.com/read/kernel_first"   -> emitted as og:url
LANDING_URL="https://universalcollapse.com/kernel_first"        -> emitted as rel=canonical
```

So the live template uses `$landing_url$` on the canonical line. **Someone changed
it from self → landing deliberately.** Option A is a *revert*, not a bugfix.

**The current design is coherent** and deserves the credit: the landing carries all
8 `citation_*` tags including `citation_pdf_url`; read pages carry **zero**;
canonical consolidates to the citation surface. That is a real Google Scholar
strategy — landing = citation surface, read = reading surface.

**The cost** is the stated goal: it tells crawlers the only full-text page on the
site is a duplicate of a page that shows only an abstract. Scholar indexes off the
landing's citation tags → PDF regardless of what the read page canonicalizes to,
so self-canonical reads do not break Scholar — they only let the full text be
indexed for everything else.

**If Option A is elected** — one line, `tools/uct-paper.html`:
```diff
- <link rel="canonical" href="$landing_url$">
+ <link rel="canonical" href="$public_url$">
```
Leave `og:url` (already correct). Do **not** add citation tags to read pages.
Note: the template edit triggers a rebuild of every read page — batch it with
Phase 1 rather than rebuilding twice.

**Reserved to the operator. See CLAUDE.md §7.1.**

---

## 4. The encoding artifact — root cause found, fix already proven in-repo

`kernelfirst.env` line 5 is **clean**: `TIER="Tier 0 · Gateway"` — 1× correct
UTF-8 middot (`0xC2 0xB7`), zero U+FFFD.

Every pandoc output renders `Tier 0 �� Gateway` — **2×** U+FFFD. Two, not one:
each byte of the two-byte sequence was independently replaced. Signature of a
byte-wise, non-UTF-8-aware step (sed under C/POSIX locale). **Source is clean;
the build corrupts it.**

The fix is not a hypothesis — it is already running one file over.
`landing_kernelfirst.html` uses `Tier 0 &middot; Gateway` and has **zero** U+FFFD.

```
TIER="Tier 0 &middot; Gateway"        # in each env — ASCII, locale-immune
export LC_ALL=en_US.UTF-8             # in build_paper.sh — general hardening
```

Do both. The entity fixes the known case; the locale export covers the em-dashes,
Greek, and subscripts throughout the corpus that will hit the same path.

---

## 5. The finding that resizes Phase 1: landings are authored

`landing_kernelfirst.html` is 14K of bespoke editorial prose — "Kernel-first, not
primitive-first", "The Observer's Fallacy", "What would make it wrong", the §9
claim-ledger pointer. **None of it is in the read page** (grep: 2 hits landing,
0 read). It is not pandoc output. `build_paper.sh` builds `/read/` only.

Consequences:
1. `citation_pdf_url` at 2/17 is explained — hand-maintained pages drift.
2. The blueprint's design principle takes a crack: *"if a page can't be
   regenerated from deposits + ledgers, it shouldn't exist."* The 17 landings
   **can't** be regenerated. They're authored. They're closer to records than views.
3. Phase 1 is bigger than "batch the read pages."

**UNKNOWN, and the first task worth doing:** memory records a `build_data.py` +
`generate_pages.py` pipeline for landings. Determine whether it sources the
per-paper prose from a data file — in which case the prose is already data and
Rule 3 is close — or whether landings are hand-maintained. **Check before
assuming.** This determines whether §7.2 is a real decision or a non-problem.

**Until determined: do not regenerate a landing page.**

---

## 6. What shipped this session

Five files, all verified before hand-off. Every emitted URL was curl-checked 200;
one link (a PhilPapers author search) was **pulled** rather than shipped because it
returned 403.

| File | Destination | Notes |
|---|---|---|
| `site_data.yaml` | `tools/` | Rule 3 single source. 17 live papers + **27-DOI backlog** of live deposits with no page (HMR `92RQ5`, EAR `2RC4D`, CMB `PNF89`, F2 `5TG3P`, TN×3, Methods×3, Primes×5, A&G×3, SBOM, Starter Packs×4). |
| `build_site_meta.py` | `tools/` | site_data.yaml → sitemap.xml + llms.txt |
| `uct_lint_html.py` | `tools/` | Rule 4 web gate. Run against live; it caught the two real defects with no false positives on 17 landings. |
| `sitemap.xml` | `public/` | **8 → 22 URLs.** No existing `lastmod` churned (no false update signals). |
| `llms.txt` | `public/` | New. Includes the kernel grammar + anti-reification guard, so a model that fetches only llms.txt still gets Ω/K/C^K_t/x*_t/R_t/S_t/U and "collapse is not a substance." |

Deploy:
```bash
cd ~/universalcollapse-site
cp <files> tools/ && cp <files> public/
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/
python3 tools/uct_lint_html.py --landing public/*.html
git add -A && git commit -m "Phase 0: sitemap coverage 8->22, llms.txt, site_data + lint gate" && git push
```

---

## 7. Suggested first tasks for CC

1. **Determine the landing pipeline** (§5). Read `tools/build_data.py` and
   `tools/generate_pages.py`. Report whether landing prose is data-sourced or
   hand-maintained. Everything about Phase 1 scope depends on this.
2. **Confirm the real template** (§2.2). Read `tools/uct-paper.html` in the repo.
   Verify the canonical line reads `$landing_url$` and report its SHA.
3. **Diff `~/Downloads/uct_pages/*.html` against `public/*.html`.** Identical →
   dead copy. Differs → unpushed work or stale draft; **report, do not delete.**
   That diff is the whole inventory job.
4. **Land the Phase 0 five** (§6), lint, push, then re-curl the sitemap and confirm
   22/22 resolve.
5. **`citation_pdf_url` on 15 landings** — blocked on whether the PDFs exist at
   `/pdf/`. Check `public/pdf/` and report coverage.

Do **not** do without operator sign-off: the canonical revert (§3), the landing
prose decision (§5), any deletion in Downloads (§7.3 of CLAUDE.md).

---

## 8. Not this repo, but open

From the same session, on the OSF/records side — tracked in
`UCT_OSF_Architecture_Blueprint_v3_1_2026_07.md`, listed here so they aren't lost:

- **DOI Registry v2.3 has a factual error.** It states twice that the Provenance
  Clarification Note (`7NVMX`) is appended to S3-RAG-01. The deposited note's own
  header says **JPXCU**. The blueprint was right; the registry needs the fix.
- That is the **second** error traced to the July 2026 conversion pipeline (the
  first was the EAR §2.1 false verification claim). Two findings, same pipeline —
  which raises the registry's own "verification-claim spot-check" open item from
  prudence to pattern.
- **CCR's gate is cleared** (SofAI live at `6M7VW`) and its ~early–mid July window
  has passed. Deposit or re-date.

---

*Verified against production 2026-07-16. Where this file and a stale copy disagree,
re-verify against the live site or the repo — not against project-file copies.*
