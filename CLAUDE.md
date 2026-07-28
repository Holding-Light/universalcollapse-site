# CLAUDE.md — universalcollapse-site

Operating constants for the UCT website repo. Read before touching anything.
Sibling to `~/uct-t16/CLAUDE.md`. Same discipline, different surface: that repo
produces records, this one produces views of records.

> **Refreshed 2026-07-20.** Brought current from the 17-paper / Registry v2.3 era:
> now 41 papers / DOI Registry v2.8, backlog 6. Corrections to the prior version —
> `build_site_meta.py` emits `library.json` too (§4.2); the architecture map has its
> own jsx→build pipeline that the old doc never documented (§4.3, §5); a "confirm
> nothing drifted" startup ritual is now §0. The architecture-map pipeline (§4.3) is
> confirmed from the build scripts themselves (`build_architecture.sh`,
> `gen_static_block.mjs`, `verify_architecture.mjs`, `check_operator.py`). Two
> current-state numbers (§0) still want one live `--check` to confirm they haven't
> moved since the v7 handoff.
>
> **§0 refreshed 2026-07-27** — append-only correction, post FWF/HIL/AIML
> ship. The 07-20 note above stands as written; its numbers were the
> 41-paper era's. Current, confirmed by one live `--check` at `6d45a86`:
> 44 papers · 41 read pages · 90 sitemap URLs · 177 edges · 134 do-not-read-as
> · 88 pages / 0 errors / 6 warnings. The measured numbers were never
> wrong; only the documented expectations were.

---

## 0. First: confirm nothing drifted

Run this cold, before touching anything. The build arc closed on evidence: a
non-empty site diff means something changed, and this is how you see it.

```
git status --short | head
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/lint_doi_shadow.py
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
```

Want: clean status; `papers built : 44`; `read pages : 41`; `sitemap URLs : 90`;
`backlog: 6`; `no doi.org links shadowing a local page ✓`; **88 pages — 0
errors, 6 warnings** (the check_conversion trio + the known-clean pair +
`read/faith_without_fideism`, pre-cleared — the structural gate reads its
`msubsup` as lawful; only the text linter can't see it).

**Trap: without `--papers-from`, every ledger cross-check silently skips** and the
lint still prints green. The flag is what makes the gate real.

Ledger fingerprint (reproducible from the committed yaml): **44 papers, 177 edges**
(related 116 + read_first 30 + supports 23 + tested_by 8), **134 do-not-read-as**.
`--check` validates and writes nothing; drop it to write.

---

## 1. What this repo is

The public face of the Universal Collapse Theory research program. It is not the
record. OSF holds the records; every paper has a permanent DOI. This site renders
them.

**Design principle:** *If a page cannot be regenerated from deposits + ledgers, it
should not exist* — with one live exception (see §6, and read it before you
regenerate anything).

- **Repo:** `~/universalcollapse-site` → github.com/Holding-Light/universalcollapse-site (branch `main`)
- **Host:** Cloudflare Workers. `wrangler.jsonc` sets `"assets": { "directory": "./public" }`.
- **Web root is `public/`.** Files at repo root are not served. This has bitten us
  before (2026-06-29: split-brain, files copied to root and never served).
- **Deploy:** `git push` → auto-build ~1–2 min. Confirm the push printed
  `main -> main`, not "Everything up-to-date." Hard-refresh (Cmd+Shift+R).
- **Deploy verification (authoritative):** `git show origin/main:<path>` reads the
  git object store, which cannot be CDN-cached. HTTP-layer instruments are
  unreliable here (raw.githubusercontent ~5-min cache; Cloudflare ignores query
  strings in its cache key). When you need to *know* what deployed, read the object.
- **DNS / www:** `www` is a proxied CNAME → apex **paired with** a Single Redirect
  301 rule. www has no Worker binding — delete the rule and www dies even with DNS
  intact. Treat the record and the rule as one object. Full spec in
  `Website_Setup_Reference.md` §DNS.

---

## 2. Hard rules

**Rule 1 — A live URL outranks a tidy namespace.**
Web analogue of OSF Blueprint Rule 7. Live URLs do not move. Paper landing slugs
stay at root (`/kernel_first`, `/wp01`) permanently. New sections take prefixed
directories (`/concepts/`, `/results/`). The root namespace gains no new non-paper
pages without operator sign-off. A slug migration already happened
(`kernelfirst → kernel_first`) and the old URLs 301 correctly. Do not break those.

**Rule 2 — No hand-written status page, ever (the Ledger Rule).**
Any page asserting claim status (Results, Predictions, Evidence, Replications,
Criticisms) is a public claims surface under the same discipline as a deposited
record. A stale "Confirmed" dashboard is a claim-discipline failure and a live
counterexample to this program's own Update Integrity Standard (DOI DWM29). Status
sections are generated from a YAML ledger with a lint gate, or they are not built.
None exist yet. Do not create one ad hoc.

**Rule 3 — One data source feeds everything.**
`tools/site_data.yaml` is the single input. One build emits `sitemap.xml`,
`llms.txt`, and `library.json`. `library.html` and the landings are **authored**
surfaces (§6) — lint-gated, not generated. A new deposit should cost: one data
entry + one build + the authored landing + one render QA. Anything cheaper than
that for the machine surfaces, and anything more for the human ones, is a signal to
check §6 before you act.

**Rule 4 — Render-verify applies to the web.**
Never trust the build; read the output. Same discipline as the docx pipeline in
`~/uct-t16`. Every generated page gets a render check and a lint pass before push.

**Rule 5 — `public/` is truth. `~/Downloads` is transit.**
Nothing is ever authored in Downloads. Files there are copies by definition and
drift silently (2026-07-16: three generations of one read page under two slug
conventions, indistinguishable by eye). If a Downloads file and a `public/` file
disagree, `public/` wins unless the operator says otherwise.

---

## 3. Notation law (sacred — inherited from the corpus)

The collapse operator is **C^K_t** — K superscript, t subscript. The subscript-K
variant is forbidden in every artifact, including generated HTML and including
pedagogical mentions ("never write X" still emits X for a scraper to extract).

Correct kernel: **Ω, K, C^K_t, x\*_t, R_t, S_t, T, U**
Canonical source: `UCT_Symbols_and_Formulas_Reference_v1_7_2026_07.md`.

Bare `C^K` (time-suppressed) is licensed shorthand and is not an error. One lawful
operator legitimately appears in **four render forms** — MathML `<msubsup>`, MathML
`<msup>` (time-suppressed), Unicode `Cᴷ`/`Cᴷₜ` (**U+1D37**, *not* U+1D30), and HTML
`C<sup>K</sup><sub>t</sub>` (what the architecture map uses). A single-convention
checker warns on three of four while the law is violated on none.

**`uct_lint_html.py` reads text and cannot see structure** — `<msub>C K</msub>` and
`<msubsup>C t K</msubsup>` both strip to "C K t" and both pass it. The notation law
is *structural*, so `tools/check_operator.py` is the structural gate: it accepts all
four forms and flags the subscript-K variant by MathML/Unicode/HTML shape. Run it on
read pages and on `architecture.html`. The docx→HTML conversion is the real risk
surface — gate it with both.

---

## 4. Build pipeline

### 4.1 Read pages — `tools/build_paper.sh <config.env>`

pandoc wrapper. Emits read pages only (`public/read/{slug}.html`).

- **Source-hash guard.** `SRC_SHA256` must match the docx. On mismatch it exits 2
  with "Adjudicate before building. Do not override." Honor that — it stops the HTML
  diverging from the deposited record. Never bypass it.
- Flags: `--mathml --toc --toc-depth=2 --section-divs --template=uct-paper.html`.
  `ALIASES` injects short anchor ids over pandoc's verbose slugs.
- **Built-in lint:** forbidden subscript-K forms in MathML and prose, placeholders
  (`XXXX`, `TKTK`, empty `citation_pdf_url`), required `rel="canonical"`. Exits
  nonzero on failure.

### 4.2 Site meta — `tools/build_site_meta.py`

The Rule 3 build. One ledger in, three machine surfaces out.

```
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check   # validate
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/           # write
```

- **Emits:** `sitemap.xml`, `llms.txt`, **`library.json`** (the whole ledger, one
  GET — `llms.txt` is prose for agents, sitemap is URLs, `library.json` is the
  program graph).
- `--check` validates and writes nothing ("check wins: would sync N flag(s), wrote
  nothing"); `--sync-flags` reconciles `built:` flags.
- `live_backlog(d)` prunes every backlog DOI that already appears in a built paper,
  so the backlog self-corrects on every ship. This is the one backlog definition;
  `status.py` imports it.

### 4.3 Architecture map — `tools/UCT_Architecture_Map_v4.jsx` → build → `public/architecture.html`   **[the one that bit us — read this]**

The architecture map is the **only** view in this repo that compiles from source
rather than going the patcher route. `public/architecture.html` is a **build
output** — its own top comment says *"Rebuild via `tools/build_architecture.sh`.
NEVER hand-edit."* Honor that; a hand-splice onto a stale shell is how a push
silently regresses the canonical tag, the no-JS summary, and the back-link.

- **Source of record:** `tools/UCT_Architecture_Map_v4.jsx` — React 18.3.1 +
  lucide-react@0.383.0, esbuild-bundled to an IIFE. Card objects carry
  `name / layerId / register ("sorted"|"applied") / role / edge / cousins[] /
  uctNotes`; `LAYERS` carry per-layer `uctPapers[]` with optional `soon: true`
  (renders "· forthcoming"). A `KernelText` parser renders `^`/`_` markup as
  sup/sub — so `K_t` is legal source and renders as a subscript.
- **Build:** `bash tools/build_architecture.sh tools/UCT_Architecture_Map_v4.jsx`
  writes `public/architecture.html` directly. Five steps: (1) esbuild the map
  (`react@18` + `react-dom@18` + `lucide-react`, IIFE, production, `--jsx=automatic`
  — **required**, no React default import); (2) `node gen_static_block.mjs map.jsx`
  generates the no-JS static block *from the jsx data* — the **8-element kernel-gloss
  guard runs inside the generator; fewer than 8 and the build dies**; (3) assemble
  `tools/architecture_shell.html` (carries the canonical tag + backlink script) by
  filling its `<!--STATIC_BLOCK-->` and `<!--BUNDLE_SCRIPT-->` placeholders —
  placeholder count is asserted, payload-corruption is checked, and the replace uses
  function-form so `$$` in the bundle stays literal (this is the `$$typeof`
  protection); (4) `node verify_architecture.mjs` — the gate: cold parse + executed
  (jsdom) parse; (5) copy to `public/`. Scratch dir `tools/_arch_build/` is
  gitignored. **First run needs network** (npm installs into `_arch_build/`).
- **Invocation trap:** the script's `SRC` defaults to a bare `UCT_Architecture_Map_v4.jsx`
  in the *current directory*. Run from repo root and **pass the path explicitly**
  (`tools/UCT_Architecture_Map_v4.jsx`), or it exits "source JSX not found". Output
  path (`public/`) is resolved relative to the script, so CWD only affects finding
  the source.
- **Gates:** kernel gloss (8 elements, inside `gen_static_block.mjs`); cold parse +
  executed/jsdom parse and `$$typeof` integrity (`verify_architecture.mjs`); operator
  structure via `check_operator.py` (§3). The build dies on any of them.
- **Why the static block matters:** it mirrors the interactive data one-to-one, so
  **adding a card is one jsx edit that the rebuild fans out to both** the interactive
  bundle and the no-JS summary (schools list, papers list, and the
  "UCT-Derived Frameworks (N entries)" count). Never edit the static block by hand.

**Deploy sequence** (mirrors patch 0004):

```
cp ~/Downloads/UCT_Architecture_Map_v4.jsx tools/UCT_Architecture_Map_v4.jsx
bash tools/build_architecture.sh tools/UCT_Architecture_Map_v4.jsx   # writes public/architecture.html
grep -c "<new card name>" public/architecture.html            # want >= 1
grep -o "UCT-Derived Frameworks (. entries)" public/architecture.html
git add tools/UCT_Architecture_Map_v4.jsx public/architecture.html
git commit -m "Architecture map: <change>; rebuild"
git push
```

Prefer patching the **jsx source** (idempotent, fail-loud, one assertion per edit),
not the built html. The patcher aborting on an anchor mismatch is the feature — it
means your source drifted from the base, so re-derive rather than force.

### Env files — `tools/{slug}.env`

`kernel_first.env` is current; `kernelfirst.env` is dead (old slug). Two variables
drive URL emission and are **not** interchangeable:

- `PUBLIC_URL` → the read URL → emitted as `og:url`
- `LANDING_URL` → the landing URL → emitted as `rel=canonical` (see §7.1)

### Encoding — known defect, fix is proven

A byte-wise, non-UTF-8-aware step under a C/POSIX locale renders a clean `·` in the
env as `��` (2× U+FFFD). Fix, already proven in this repo:

```
# in the env — ASCII, immune to locale
TIER="Tier 0 &middot; Gateway"
# in build_paper.sh, general hardening
export LC_ALL=en_US.UTF-8
```

---

## 5. Tools

**Generation / build**

| File | Does |
|---|---|
| `tools/build_paper.sh` | docx → read page (pandoc + hash guard + lint) |
| `tools/build_site_meta.py` | `site_data.yaml` → `sitemap.xml` + `llms.txt` + `library.json` |
| `tools/build_architecture.sh` | jsx → `public/architecture.html` (esbuild bundle + static block + assemble + verify; needs network on first run) |
| `tools/gen_static_block.mjs` | generates the no-JS crawler summary from the map jsx; the 8-element kernel-gloss guard lives here |
| `tools/verify_architecture.mjs` | architecture-map gate: cold parse + executed (jsdom) parse + `$$typeof` integrity |

**Source / templates**

| File | Does |
|---|---|
| `tools/uct-paper.html` | read-page template |
| `tools/UCT_Architecture_Map_v4.jsx` | architecture-map source of record |
| `tools/{slug}.env` | per-paper build config |
| `tools/site_data.yaml` | Rule 3 single source — 44 papers + 6-DOI backlog |

**Linters / gates**

| File | Does |
|---|---|
| `tools/uct_lint_html.py` | Rule 4 web gate — TEXT (notation, encoding, canonical, citation tags, sitemap agreement) |
| `tools/check_operator.py` | STRUCTURAL operator gate — accepts all four `C^K_t` forms, flags the subscript-K variant by MathML/Unicode/HTML shape (text lint can't see structure) |
| `tools/lint_doi_shadow.py` | flags `doi.org` nav links shadowing a live local page (excludes own-DOI, backlog DOIs, `<article>` bibliographies) |

**Ledger-derived patchers** — idempotent, dry-run by default, `--apply` writes,
git-is-backup, fail-loud on anchor mismatch. They maintain the *mechanical* blocks
on authored pages; they never read, match, or rewrite authored prose.

| File | Does |
|---|---|
| `tools/patch_landing_jsonld.py` | ScholarlyArticle / SoftwareSourceCode JSON-LD on landings (StarterPacks → SoftwareSourceCode) |
| `tools/patch_position_blocks.py` | "Position in the Program" block from `relations` |
| `tools/patch_kernel_terms.py` | kernel `DefinedTermSet` JSON-LD on `index` + `kernel_first` |
| `tools/patch_llms_link.py` | `llms.txt` `<link rel="alternate">` on authored pages |
| `tools/fix_extension_hops.py` | rewrite internal `.html` links to extensionless form per sitemap |
| `tools/fix_landing_read_cta.py` | primary CTA → `/read/<slug>` where a read page exists |
| `tools/fix_doi_shadow.py` | rewrite shadowing `doi.org` nav links to the local page (companion to the linter) |

**Status**

| File | Does |
|---|---|
| `tools/status.py` | where the site is, read off disk — `--library` (link audit), `--queue` (what's next) |

```
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
python3 tools/lint_doi_shadow.py
python3 tools/status.py --queue
```

`site_data.yaml` never invents a DOI. Truth is
the latest `UCT_DOI_Registry_v*`. Cross-check each entry against its live page's
own `citation_doi` before trusting it.

---

## 6. Generated vs authored — read before regenerating

- **Read pages are generated.** pandoc output from a hash-pinned docx. Safe to
  rebuild any time.
- **`library.json` is generated.** `build_site_meta.py`. Safe to rebuild.
- **The architecture map is generated** from its jsx (§4.3). Safe to rebuild — via
  the build, never by hand.
- **Landing pages are NOT generated by any script in this repo.** There is no
  landing generator — `build_data.py` / `generate_pages.py` do not exist (an old
  memory recorded them; that record is wrong). `build_paper.sh` builds `/read/`
  only. **`library.html` is likewise authored**, not generated — the patchers only
  rewire its mechanical parts (links, JSON-LD).

"Not generated" does not mean "hand-typed by the operator." The landings were
produced in a prior assistant session — one first, then the rest — and approved.
Provenance is not visible in the bytes. Measured composition of a landing
(`kernel_first`, 14,113 bytes): **60% CSS** (shared boilerplate), **14% head tags**
(every field already in `site_data.yaml`), **17% authored prose** (~290 words, 4
sections), **9% chrome** (header, CTA, cite box).

So the correct line: **generate the mechanical ~83% via the patchers; keep the ~290
words under review.** The head tags are where `citation_doi` and `citation_pdf_url`
live — facts that should never be typed twice. Regenerating a landing costs a review
pass, not authorship. Do not do it casually, and never without showing the operator
the diff.

**Adding a new paper's landing** (the common task) is therefore: one `site_data.yaml`
entry → rebuild meta → **author** the ~290-word landing (match an existing one) →
run the mechanical patchers (`patch_landing_jsonld`, `patch_position_blocks`,
`fix_landing_read_cta`, `patch_llms_link`, `fix_extension_hops`) → lint
(`uct_lint_html`, `lint_doi_shadow`) → render-verify → push. Library row + roadmap
follow the same authored-then-patched shape. **The full batch sequence —
gates, expected numbers, and per-paper checklist — is `ADDING_PAPERS.md` at
repo root. Read it first.**

---

## 7. Open adjudications — DO NOT DECIDE THESE

Operator (Jeremy) is sole adjudicator. Surface findings; do not act.

**7.1 — Canonical policy.** Read pages canonicalize to their landing
(`rel=canonical = $landing_url$`) — a deliberate change (an older build was
self-canonical). Coherent: the landing carries all 8 `citation_*` tags including
`citation_pdf_url`; read pages carry none; canonical consolidates to the citation
surface. Cost: it tells crawlers the only full-text page is a duplicate, working
against the AI-retrieval goal. If Option A is elected, it's one line in
`tools/uct-paper.html` (`$landing_url$` → `$public_url$`); leave `og:url` alone; do
not add citation tags to read pages.

**7.2 — Landing prose.** Move it into `site_data.yaml` as per-paper fields so Rule 3
holds, or amend Rule 3 to exempt landings as an authored, lint-gated surface.
Operator's call.

**7.3 — Downloads reconciliation.** Which `uct_pages/*.html` differences are
unpushed work vs abandoned drafts. Diff and report; do not delete without sign-off.

---

## 8. Cross-references (truth sources)

| Question | File |
|---|---|
| DOIs, publication status | latest `UCT_DOI_Registry_v*` — highest version wins |
| Notation | `UCT_Symbols_and_Formulas_Reference_v1_7_2026_07.md` |
| Site target architecture, phases, ledger schemas | `UCT_Site_Architecture_Blueprint_v1_0_2026_07.md` |
| OSF component structure | `UCT_OSF_Architecture_Blueprint_v3_1_2026_07.md` |
| Hosting / deploy history, DNS & www | `Website_Setup_Reference.md` |

**Known error in the Site Blueprint:** the Phase 0 register carries "sitemap 404
VERIFY". False — `sitemap.xml` returns 200 and always did (the 404 was a
fetch-pipeline artifact from another model's session). The real defect was the
inverse: live landing pages missing from the sitemap, since fixed. Strike the line
on next blueprint touch.

---

## 9. Author / metadata constants

Jeremy C. Jones · HoldingLight LLC
ORCID 0009-0007-2515-3774 · contact@universalcollapse.com
CC BY 4.0 · © 2025–2026 HoldingLight LLC
Theme: bg `#08090c` · accent `#c9a96e` · EB Garamond / Outfit / JetBrains Mono

---

## 10. Traps — a tool encoding one assumption about a world that has two

Register added 2026-07-27. Each entry earned by an actual failure or near-miss;
none is hypothetical. The shape is always the same: an instrument, template, or
reviewer carrying one assumption about a world that turned out to have two.

- **The DOI-shadow lint guards the site; nothing guards the papers' reference
  lists.** SoE cites Records and UIS with DOIs and WP01 bare. The site's
  identifier discipline does not propagate to the corpus's own bibliographies.
- **A deposited abstract is a retrieval surface with its own version.** Kernel
  drift surfaces are three — `patch_kernel_terms.TERMS`, `build_llms` prose,
  and the PhilArchive record abstract — and nothing compares them.
  (JONUCT-2 gained a forward pointer + DOI 2026-07-27; the trap outlives the
  instance.)
- **Unnamed discipline gets named by readers.** A floating acronym resolved two
  ways across two cold reads; an everywhere-practiced, nowhere-named boundary
  got a reader-invented scheme attributed to the project. No lint catches "the
  corpus does this but never says so."
- **Steering is invisible from inside.** Anonymous prompts control for
  author-deference, not frame-following: a steered cold model elaborates the
  offered thesis back and calls it more compelling. Only unsteered turns are
  signal.
- **Instruments inherit the ontology of their config.** The acceptance sweep
  verified every URL the sitemap declares and could not see the hostname the
  sitemap never mentions. www was dead for five months beside all-green checks.
- **A green gate can be reading a stale artifact.** The architecture build died
  upstream (`npm: command not found`); the operator gate and lint downstream
  truthfully PASSED — on yesterday's page. The same week, an external
  reviewer's cache produced a punch list of already-fixed items. Before
  trusting a gate, confirm the artifact it read is the one you just made.
- **Legacy configs resurrect retired bugs.** `kernelfirst.env` (pre-migration
  era) used as a template carried `OUT=read/…` and re-created the 2026-06-29
  split-brain. Envs are records of an era; clone the newest sibling, never the
  oldest.
- **TIER is a cross-checked record, not a label.** `build_site_meta` byte-
  matches each env's TIER against the ledger's tier_label-or-tier and dies on
  mismatch. The ledger is source; sync the env to it. Do not default.
- **Cloned surfaces hide fields you didn't grep.** `citation_public_url`
  survived a truncated head-dump and shipped on three landings pointing at the
  template's URL. When cloning an authored page, diff every `citation_*`,
  canonical, and `og:` field against the ledger — not the ones you remember.

- **A verification grep dies when a class string grows.** `grep -c
  'class="paper-card"'` returned 4 where 8 cards existed: four carried
  `class="paper-card is-static"`, which does not contain the searched
  string — the closing quote differs. The patcher's own post-conditions,
  which asserted both forms separately, were right; the verification line
  typed afterward was wrong. Verify with the assertion the tool already
  makes, not a fresh string from memory.

- **A paste block is a program in the operator's shell, not yours.** A run
  block written with trailing `# comment` annotations was pasted into zsh,
  where `interactive_comments` is off by default: the `#` became an
  argument, argparse rejected it, and the dry run was silently skipped —
  the patcher went straight to `--apply` with no review pass. The same `#`
  swallowed both post-push verification greps. Annotations belong in the
  tool's own output, never in a block someone else pastes.

---

The site renders; the deposits assert. When in doubt: if a page can't be
regenerated from deposits + ledgers, it shouldn't exist — unless §6 says a human
wrote it, in which case leave it alone.
