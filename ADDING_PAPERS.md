# ADDING_PAPERS.md — the batch playbook

**Read this before adding any paper to universalcollapse-site.** It exists because
a session once spent two hours fighting this repo's conventions without it. Read
`CLAUDE.md` §2–§6 and §10 alongside; this file is the operational sequence, that
one is the law. Papers ship in batches (operator cadence: ~3 per pass).

Everything here is dry-run-first, exact-count-asserted, and verified from outside
after push. If a gate fails, stop and read what it says — every gate in this repo
prints its own remedy. **Never default. Never hand-edit a build output.**

---

## 0. Preconditions (per paper — collect before touching the repo)

- Paper **deposited**: OSF DOI minted; PhilArchive handle if applicable (OSF-only
  papers exist — then the yaml simply **omits** the `philarchive` key).
- DOI cross-checked against `UCT_DOI_Registry_v*.md` — **the yaml never invents a
  DOI** (CLAUDE.md §5).
- Real docx on disk (absolute path); final PDF named per current convention:
  **full docx stem, underscores + date** (e.g.
  `UCT_T15_How_Minds_Resolve_v1_0_2026_07.pdf`). The dotted short form
  (`UCT_T0_Kernel_First_v1.0.pdf`) is the older era — match the newest siblings.
- Slug chosen and **operator-approved** — slugs are permanent (Rule 1).
- The deposit's own abstract at hand — the landing abstract is the paper's
  abstract, verbatim (house dash spacing), plus a "What this paper does not
  claim" paragraph and a Keywords line.

## 1. Ledger entry — `tools/site_data.yaml`

Clone the **newest** sibling entry's field set and order (includes `version:`).
Insert before `- slug: starter_physics` (append-order convention). Tier strings
must match the ledger vocabulary **byte-for-byte** — current set:

| tier | tier_label |
|---|---|
| `Tier 0 — Orientation` | `Tier 0 · Gateway` (T0 only carries a label) |
| `Tier 1 — White Papers` | — |
| `Tier 1.5 — Interpretive Bridges` | — |
| `Tier 1.6 — Empirical Demonstrations` | — |
| `Tier 2 — Operating Manuals` | — |
| `Standards` / `Methods & Theoretical Notes` / `CIM` / `Architecture — Governance` / `Tier 30 — Primes` | — |

Relations come from the paper's own routing section (`read_first` / `related` /
`supports` / `tested_by`); every edge must name a **built slug** or the build
dies. `do_not_read_as`: 3–4 clauses in the paper's own language. `pdf_sha256`
of the placed PDF (a one-shot script computing it beats typing it).

## 2. Env file — `tools/<slug>.env`

Clone the **newest** env, never `kernelfirst.env` (pre-migration relic; its
`OUT=read/…` resurrected a retired split-brain once — §10). Non-negotiables:
- `OUT="public/read/<slug>.html"` — **with the `public/` prefix.**
- `TIER` must **byte-match** the ledger's `tier_label`-or-`tier` — the meta
  build cross-checks and dies on mismatch. Ledger is source; sync env to it.
- `SRC` absolute path to the real docx; `SRC_SHA256` via
  `shasum -a 256 <docx>`.
- Encoding: ASCII entities in the env (`&middot;`), per CLAUDE.md §4's locale
  defect.

## 3. Author the landing — `public/<slug>.html`

There is **no landing generator** (§6). Clone the **newest live landing** of the
same tier, then replace **every** metadata field against the ledger — not the
ones you remember: `<title>`, description, `rel=canonical`, all `citation_*`
**including `citation_public_url` and `citation_pdf_url`**, `og:*`, JSON-LD
headline/description, DOI links, PhilArchive link (drop entirely for OSF-only),
read CTA, PDF href, cite box. A field you didn't grep for once shipped three
landings pointing at the template's URL (§10). Body: the deposit's abstract
verbatim + not-claim + keywords (~290 words; extra concept sections allowed for
gateway-weight papers). Position block stays patcher-shaped. **Operator reviews
the prose** — always.

## 4. Build the read page

```
bash tools/build_paper.sh tools/<slug>.env
```
Hash guard passes only if `SRC_SHA256` matches the docx. On "Adjudicate before
building" — do exactly that; never bypass.

## 5. Meta build

```
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/
```
Expected numbers for N new papers: papers **+N**, read pages **+N**, sitemap
**+2N**. Zero flag drift if yaml and disk agree. Backlog self-prunes.

## 6. Patchers (dry, then --apply, each)

`patch_landing_jsonld` → `patch_position_blocks` → `fix_landing_read_cta` →
`patch_llms_link` → `fix_extension_hops`. Idempotent; they verify all landings
and change only what the ledger moved.

## 7. Library + Roadmap (authored surfaces)

One library card per paper in the right group; roadmap step flips/inserts where
the paper appears; tier-card docs lists. Write a tested one-shot patcher for
these (pattern: fetch the live bytes, anchor on exact strings, assert counts,
prove against the fetched copy **before** shipping). Genuinely-forthcoming
papers stay dim — never flip a paper without a live page.

## 8. Architecture map (when the paper warrants a card)

Edit `tools/UCT_Architecture_Map_v4.jsx` only, then:
```
bash tools/build_architecture.sh tools/UCT_Architecture_Map_v4.jsx
python3 tools/check_operator.py public/architecture.html
```
node is required (installed 2026-07-27; `tools/_arch_build/` is gitignored).
**If the build fails, everything downstream is checking yesterday's page** —
§10. Never hand-edit `public/architecture.html`.

## 9. Gates — all three, every time

```
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
python3 tools/lint_doi_shadow.py
python3 tools/check_operator.py public/read/<each-new-slug>.html
```
Page count grows by **+2N**. Warnings are adjudication items (the
`check_conversion.py` queue), never hand-fixes. Errors are stops. Without
`--papers-from`, the lint silently checks nothing that matters.

## 10. Render-verify, ship, verify from outside

Open every new landing and read page in a browser. Then:
```
git add -A && git status --short   # review — nothing unexpected
git commit -m "…" && git push      # must print: main -> main
```
After deploy (~2 min): sweep the new URLs live (200s, citation tags, DOI,
PhilArchive presence/absence as designed, zero `C_K`), and
`git show origin/main:<path>` when you need cache-proof truth (§1).

---

*The failure mode this file prevents is not ignorance of any single step — it is
improvising the sequence. Run it in order, read every gate, and the repo will
tell you when you're wrong before the public ever sees it.*
