# CLAUDE.md — universalcollapse-site

Operating constants for the UCT website repo. Read before touching anything.

Sibling to `~/uct-t16/CLAUDE.md`. Same discipline, different surface: that repo
produces records, this one produces **views of records**.

---

## 1. What this repo is

The public face of the Universal Collapse Theory research program. It is **not**
the record. OSF holds the records; every paper has a permanent DOI. This site
renders them.

**Design principle:** *If a page cannot be regenerated from deposits + ledgers,
it should not exist.* — with one live exception (see §6, and read it before you
regenerate anything).

- **Repo:** `~/universalcollapse-site` → github.com/Holding-Light/universalcollapse-site (branch `main`)
- **Host:** Cloudflare Workers. `wrangler.jsonc` sets `"assets": { "directory": "./public" }`
- **Web root is `public/`.** Files at repo root are **not served.** This has bitten
  us before (2026-06-29: split-brain, files copied to root and never served).
- **Deploy:** `git push` → auto-build ~1–2 min. Confirm the push printed
  `main -> main`, not "Everything up-to-date."
- **Deploy verification, in order (2026-07-17):** origin first —
  `curl -s https://raw.githubusercontent.com/Holding-Light/universalcollapse-site/main/public/architecture.html | grep -c forthcoming`
  is the honest instrument for "did it land." Then give the edge its 1–2 min.
  **The `?v=` query buster is a placebo on this zone** — `cf-cache-status: HIT`
  comes back on never-seen query strings, so the cache key ignores them. It
  never busted anything; it "worked" once because the wait outlasted the build.
  `curl -sI` + `cf-cache-status` tells you which world you're reading.

---

## 2. Hard rules

### Rule 1 — A live URL outranks a tidy namespace
Web analogue of OSF Blueprint Rule 7. Live URLs do not move. Paper landing slugs
stay at root (`/kernel_first`, `/wp01`) permanently. All **new** sections take
prefixed directories (`/concepts/`, `/results/`). The root namespace gains no new
non-paper pages without operator sign-off.

A slug migration already happened (`kernelfirst` → `kernel_first`) and the old URLs
301 correctly. Do not break those redirects.

### Rule 2 — No hand-written status page, ever (the Ledger Rule)
Any page asserting claim status (Results, Predictions, Evidence, Replications,
Criticisms) is a public claims surface under the same discipline as a deposited
record. A stale "Confirmed" dashboard is a claim-discipline failure and a live
counterexample to this program's own Update Integrity Standard (DOI `DWM29`).
Status sections are **generated from a YAML ledger** with a lint gate, or they are
not built. None exist yet. Do not create one ad hoc.

### Rule 3 — One data source feeds everything
`tools/site_data.yaml` is the single input. One build emits sitemap.xml, llms.txt,
and (target state) library.html and the landings. A new deposit should cost:
one data entry + one build + one render QA. Anything more is a pipeline defect,
not a process to document. **See §6 — this rule does not currently hold for landings.**

### Rule 4 — Render-verify applies to the web
Never trust the build; read the output. Same discipline as the docx pipeline in
`~/uct-t16`. Every generated page gets a render check and a lint pass before push.

### Rule 5 — `public/` is truth. `~/Downloads` is transit.
Nothing is ever authored in Downloads. Files there are copies by definition and
drift silently. As of 2026-07-16 Downloads held **three generations of the same
read page** under two slug conventions — indistinguishable by eye. If a Downloads
file and a `public/` file disagree, `public/` wins unless the operator says
otherwise.

---

## 3. Notation law (sacred — inherited from the corpus)

The collapse operator is **C^K_t** — K superscript, t subscript. The subscript-K
form is forbidden in every artifact, including generated HTML and including
pedagogical mentions ("never write X" still emits X for a scraper to extract).

Correct kernel: Ω, K, C^K_t, x*_t, R_t, S_t, T, U

Canonical source: `UCT_Symbols_and_Formulas_Reference_v1_7_2026_07.md`.
Bare `C^K` (time-suppressed) is licensed shorthand and is **not** an error.

Live HTML was clean as of 2026-07-16: 0 violations, 6 correct `Cᴷ` unicode forms
on `/read/kernel_first`. The docx→HTML conversion is the risk surface. Gate it.

---

## 4. Build pipeline

### Read pages — `tools/build_paper.sh <config.env>`
pandoc wrapper. Emits **read pages only** (`public/read/{slug}.html`).

- **Source-hash guard.** `SRC_SHA256` must match the docx. On mismatch it exits 2
  with "Adjudicate before building. Do not override." **Honor that.** It exists to
  stop the HTML diverging from the deposited record. Never bypass it.
- `--mathml --toc --toc-depth=2 --section-divs --template=uct-paper.html`
- `ALIASES` injects short anchor ids over pandoc's verbose slugs.
- Built-in lint: forbidden subscript-K operator forms in MathML and prose,
  placeholders (`XXXX`, `TKTK`,
  empty `citation_pdf_url`), required `rel="canonical"`. Exits nonzero on failure.

### Env files — `tools/{slug}.env`
`kernel_first.env` is current. `kernelfirst.env` is **dead** (old slug).

Two variables drive URL emission and they are not interchangeable:
- `PUBLIC_URL` → the read URL → emitted as `og:url`
- `LANDING_URL` → the landing URL → **emitted as `rel=canonical`** (see §7)

### Encoding — known defect, fix is proven
`TIER="Tier 0 · Gateway"` is clean UTF-8 in the env (verified: 1× `0xC2 0xB7`,
zero U+FFFD). Every pandoc output renders it as `Tier 0 �� Gateway` — **2×** U+FFFD,
one per byte. Classic signature of a byte-wise, non-UTF-8-aware step under a
C/POSIX locale.

The fix is already proven in this repo: `landing_kernelfirst.html` uses
`Tier 0 &middot; Gateway` and has **zero** U+FFFD.

```
# in the env — ASCII, immune to locale
TIER="Tier 0 &middot; Gateway"

# in build_paper.sh, general hardening
export LC_ALL=en_US.UTF-8
```

---

## 5. Tools

| File | Does |
|---|---|
| `tools/build_paper.sh` | docx → read page (pandoc + hash guard + lint) |
| `tools/uct-paper.html` | read-page template |
| `tools/{slug}.env` | per-paper build config |
| `tools/site_data.yaml` | **Rule 3 single source** — 41 built papers; `read`/`pdf` flags derived from disk; backlog pruned live (6 as of 2026-07-17) |
| `tools/build_site_meta.py` | site_data.yaml → sitemap.xml + llms.txt; `--check` = drift gate |
| `tools/status.py` | disk-derived status table; backlog via shared `live_backlog` |
| `tools/uct_lint_html.py` | Rule 4 web gate (notation, encoding, canonical, citation tags, ledger cross-check, library-card DOI display, sitemap agreement) |
| `tools/build_architecture.sh` | JSX → architecture.html (esbuild, generated static block, jsdom e2e gate) |
| `tools/patch_*.py`, `tools/fix_*.py` | one-shot landing/library patchers — the landing mechanics pipeline. **No landing generator exists; see §6** |

```bash
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
python3 tools/lint_doi_shadow.py
```

Without `--papers-from`, the ledger cross-checks silently skip — a bare
`--landing` run passes pages the full invocation would fail.

`site_data.yaml` never invents a DOI. Truth is `UCT_DOI_Registry_v2_6_2026_07.md`.
All 17 entries were cross-checked against each live page's own `citation_doi` tag
on 2026-07-16: 17/17 match. As of 2026-07-17 the same check runs on every lint
pass via `check_against_ledger` — 41/41, gated not recalled.

---

## 6. Generated vs authored — read before regenerating

**Read pages are generated.** pandoc output from a hash-pinned docx. Safe to
rebuild any time.

**Landing pages are NOT generated by any script in this repo.** There is no
landing generator — `build_data.py` / `generate_pages.py` do not exist (memory
recorded them; that record is wrong). `build_paper.sh` builds `/read/` only.

But "not generated" does not mean "hand-typed by the operator". The landings were
produced in a prior assistant session — one paper first, then the rest — and
approved by the operator. Provenance is not visible in the bytes. Measured
composition of a landing (`kernel_first`, 14,113 bytes):

```
60%  CSS            — boilerplate, shared
14%  head tags      — every field already in site_data.yaml
17%  authored prose — 290 words, 4 sections
 9%  chrome         — header, CTA, cite box
```

So the correct line is: **generate the mechanical 83%, keep the 290 words under
review.** The head tags are where `citation_doi` and `citation_pdf_url` live —
facts that should never be typed twice. Regenerating a landing costs a review
pass, not authorship. It is not sacred, but do not do it casually and never
without showing the operator the diff.

The working pattern (proven 2026-07): mechanical facts are injected by one-shot
patchers deriving from `site_data.yaml` — `patch_landings.py`,
`patch_citation_pdf.py`, `patch_library_cards.py`, `fix_landing_read_cta.py` —
hash-guarded, dry-run-by-default. New mechanical surfaces (landing JSON-LD,
relationship blocks) take this route until §7.2 is adjudicated.

## 7. Open adjudications — DO NOT DECIDE THESE

Operator (Jeremy) is sole adjudicator. Surface findings; do not act.

**7.1 — Canonical policy — RESOLVED, Option A shipped (verified live 2026-07-17).**
Read pages are self-canonical (`rel=canonical` = their own `/read/` URL) and carry
the full `citation_*` set plus JSON-LD, via `patch_read_metadata.py` →
`tools/uct-paper.html`; landings keep their Scholar tags. Verified on
`/read/wp01`: canonical `/read/wp01`, 8 citation tags, JSON-LD parses. The prior
design (read pages canonicalize to the landing, carry no tags) is history — do
not restore it, and treat any page still emitting it as unrebuilt.

**7.2 — Landing prose.** Move it into `site_data.yaml` as per-paper fields so
Rule 3 holds (17 papers of work), or amend Rule 3 to exempt landings as an
authored surface, lint-gated rather than generated. Operator's call.

**7.3 — Downloads reconciliation.** Which `uct_pages/*.html` differences are
unpushed work and which are abandoned drafts. Diff and report; do not delete
without sign-off.

---

## 8. Cross-references (truth sources)

| Question | File |
|---|---|
| DOIs, publication status | `UCT_DOI_Registry_v2_3_2026_07.md` |
| Notation | `UCT_Symbols_and_Formulas_Reference_v1_7_2026_07.md` |
| Site target architecture, phases, ledger schemas | `UCT_Site_Architecture_Blueprint_v1_0_2026_07.md` |
| OSF component structure | `UCT_OSF_Architecture_Blueprint_v3_1_2026_07.md` |
| Hosting/deploy history | `Website_Setup_Reference.md` |

**Known error in the Site Blueprint:** the Phase 0 register carries
"sitemap 404 VERIFY". That is false — `sitemap.xml` returns 200 and always did
(verified by curl 2026-07-16; the 404 was a fetch-pipeline artifact from another
model's session). The real defect was the inverse: 14 live landing pages **missing**
from the sitemap. Strike the line on next blueprint touch.

---

## 9. Author / metadata constants

```
Jeremy C. Jones · HoldingLight LLC
ORCID 0009-0007-2515-3774
contact@universalcollapse.com
CC BY 4.0 · © 2025–2026 HoldingLight LLC
Theme: bg #08090c · accent #c9a96e · EB Garamond / Outfit / JetBrains Mono
```

---

## 10. Traps (earned)

Each cost real time. Same shape throughout: **a tool encoding one assumption
about a world that has two.**

- **Project `.docx` files in the Claude project mount are markdown with a
  `.docx` extension** — `read_text()`, never pandoc/zipfile. Real docx live in
  `~/Desktop/Papers/**/`.
- **Git is the backup.** Patch scripts never write `.orig`/`.bak` into a tracked
  tree. `.gitignore` carries the patterns anyway; `git add -A` sweeps everything
  it can see.
- **A default that is always overridden has never been tested.** Grep for
  fallbacks whose override is universal. (`make_envs.py` TEMPLATE default: wrong
  from day one, unreachable until 21 new envs fell straight through it.)
- **A check that has never failed has never been tested.** Every new lint gets a
  doctored input that must FAIL before its PASS means anything. (Library-card
  DOI check: proven against the historical UWRS3 shape before first trust.)
- **`grep -c` counts lines, not structure.** Read the matched lines before
  concluding — a count of 2 was once read as "the citation block exists"; both
  hits were display code.
- **Derived fields must derive.** If a field states a fact about the filesystem,
  compute it at build time; never ask a human to declare it at 2 AM.
- **Commands handed to the operator must be paste-ready.** Concrete paths, real
  filenames, no `<placeholders>` — zsh parses `<` as a redirect and errors before
  the command runs (2026-07-17).
- **The edge lies politely.** See §1: origin first; the `?v=` buster is a placebo
  on this zone.

---

*The site renders; the deposits assert. When in doubt: if a page can't be
regenerated from deposits + ledgers, it shouldn't exist — unless §6 says a human
wrote it, in which case leave it alone.*
