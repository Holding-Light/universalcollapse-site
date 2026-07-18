# Session Handoff — universalcollapse.com — 2026-07-17 (v4, evening)

**Paste into a fresh window to start.** Supersedes `Session_Handoff_Site_2026_07_17_v3.md`
(the afternoon one). Everything on its "what's left" list is closed or carried forward
explicitly below.

**Read this part first:** the site is done. Not "done for now" — done. The queue below is
short, and most of it isn't site work. If this session ends with a large diff, something
went wrong. See §6.

---

## 1. First thing: confirm nothing drifted

```
git status --short | head
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/lint_doi_shadow.py
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
```

Want: clean status, `read pages : 38`, `sitemap URLs : 83`, `backlog: 6`, zero flag drift,
`no doi.org links shadowing a local page ✓`, and **82 pages — 0 errors, 5 warnings**.

The 5 warnings are known and are the only open lint items: NOTATION on `wp01` (landing) and
on read pages for `program_map`, `s3_calibration`, `soai`, `wp03`. The linter's own message
declares `wp03`/`soai` known-clean (omml=0 at source, prose-only mention). The real queue is
**three pages needing `check_conversion.py` against their docx on Jeremy's machine** —
`wp01`, `program_map`, `s3_calibration`. Notation adjudication is Jeremy's; do not "fix"
these from the site side.

**Without `--papers-from`, every ledger cross-check silently skips.** A bare `--landing` run
passes pages the full invocation fails. Use the full form above, always.

---

## 2. Where things stand (all verified live, not inferred)

| | 2 AM | Afternoon (v3) | Now |
|---|---|---|---|
| Sitemap URLs | 62 | 83 | **83** |
| Read pages live / in sitemap | 38 / 17 | 38 / 38 | **38 / 38** |
| JSON-LD — read pages | 0 | 38 | **38** |
| JSON-LD — landings | 0 | 0 | **41** ✱ |
| `citation_pdf_url` | 17 | 38 of 41 | **38 of 41** |
| `pdf_sha256` coverage | — | 36 of 41 | **38 of 41** |
| Internal `.html` extension hops | — | 167 | **0** |
| Backlog (`status.py` **and** `build_site_meta`) | 27 / 27 | 27 / 6 | **6 / 6** |
| DefinedTermSet (kernel at retrieval boundary) | — | — | **2 pages, 8 terms** |
| `/library.json` | — | — | **41 papers, 3 with relations** |
| Papers carrying `relations` | — | — | **3 of 41** |
| Lint checks | 5 | 6 | **9** |

✱ 38 `ScholarlyArticle` + 3 `SoftwareSourceCode` — the Starter Packs are runnable Python and
are correctly typed as code, not articles. They have no PDF and no read page, ever; the
`citation_pdf_url` warn is now suppressed for them by ledger lookup, not by slug.

**37 commits today.** In order: the v3 handoff closed (status.py backlog, two lint fixes, two
PDF hashes, architecture map rebuilt, registry v2.6) → CLAUDE.md brought into agreement with
the repo → tier split adjudicated → 167 hops → landing JSON-LD → DefinedTermSet → lint 7/8 →
relations schema + gate → position blocks → `isBasedOn` → `library.json` → lint 9 → marker
leak fixed → refactor reverted → CLAUDE.md ×3.

---

## 3. What's left — honestly, in order

### 3.1 Relations batch — the only real build work, and it's authoring

3 of 41 papers carry `relations`. The machinery is finished and gated; what remains is
**Jeremy's claims, paper by paper**. Each batch: draft yaml → render → he adjudicates →
ship. Roughly five approval cycles.

**`falsification_standards` (TN7Z3) goes first, and the reason is evidence.** In the
2026-07-17 cold-read test, a clean-slate model reached the Methods papers, the UIS, and SoE
— and proposed building a failure ladder that TN7Z3 already contains, in more detail. It
never surfaced TN7Z3. That paper is live with a read page and a DOI and answers the single
question a critical reader asks first. It is under-retrieved relative to its importance and
it is the one paper with direct evidence of it.

Then: (2) the spine — WPs, Records, Standards triad, UIS; (3) T1.5 bridges, the biggest
batch; (4) T16 empirical + Methods/TN, where the `tested_by` edges live; (5) Primes + AG +
CIM; (6) Starter Packs, probably `read_first` only.

Schema is closed and gated (`check_relations` in `build_site_meta`): `purpose`,
`read_first`, `supports`, `tested_by`, `related`, `do_not_read_as`. Dead edges, self-loops,
and unknown fields all fail loud. **One open schema question, Jeremy's call:**
`Supersedes / Replaced by` was trimmed from the original nine categories. `ai_synthetic` ↔
WP01 §0.7.1 is the first real instance (see §5). "Supersedes a section of a live paper" is a
stranger edge than the field was designed for.

### 3.2 `llms.txt` discoverability — 10 minutes, the only surviving item from Session D

`/llms.txt` returns **HTTP 200, 14.7 KB**, `robots.txt` is wide open — and **zero pages link
to it, zero sitemap entries**. It is reachable only by a client that already knows the
`/llms.txt` convention and tries the URL blind. A `<link rel="alternate">` in the head plus a
sitemap entry are the whole job.

**Do not "improve" llms.txt's content.** See §6. It already carries the full eight-element
kernel, both equations, the notation law spelled out, the complete inoculation paragraph, and
a `## Start here` leading with Kernel First. It is better written than a generated
replacement.

### 3.3 Corpus items — not site work

- **CoG naming.** WP01 §0.7.2 (published, v2.0, DOI VZ836) reads three ways in two lines:
  heading *"CoG (Collapse of God)"*, body *"CoG (Concept of God / Circuit of God)"*. The
  unpublished draft is titled *The Circuit of God* and its body says *"the Collapse (or
  Circuit) of God"*. A cold model reproduced the hedge **faithfully** — it read us
  correctly; we say three things. WP01 is a deposited record: **do not edit it.** The
  correction goes forward. WP07 is being retired, so there is no WP07 to fix it in.
  Symbols Reference entry if CoG stays a live concept; otherwise the paragraph is history.
- **WP06/WP07 retirement → Retired Lineage Record** (the file already exists), and publicly
  in **WP05**, which Jeremy says closes the series out. §0.7 was the roadmap; WP05 is the
  destination. See §5 — this is a good record, not a cleanup.
- **Falsification Standards v1.1 [ADJUDICATE]** — one candidate delta, in
  `Session_Insight_Cold_Read_Diagnostic_2026_07_17.md` §4: **graceful demotion** as a named,
  non-pathological outcome. The standard has *degeneration* (pathological, with narrowing as
  a symptom) but never names the honest version — which Jeremy stated himself: *"lets salvage
  the methods that tested it. But let's move on."* If it proceeds: integrate into the
  existing ten-state status vocabulary, do **not** add a parallel one (that recreates
  `tier`/`tier_label` at the claims layer), and make positive-control success an explicit
  prerequisite for the higher rungs or every failure retreats into "measurement failure."
- **WP05 seed [ADJUDICATE]** — *"Reality appears to be acts of resolution. Acts of
  actualization."* The *epistemic* half of Jeremy's private-window formulation is **already
  published** in Kernel First (*"UCT offers its own ontology — an account of what there is —
  held on trial: a candidate that aims at reality's structure and answers to records, but
  does not claim to be that structure"*). Only the **positive** characterization of reality
  is new. That is the delta.
- **`uct_lint.py` notation** on the three pages in §1.

### 3.4 Small, optional, deferred by Jeremy

- Roadmap step 3 → `6UY87` (Primes bundle, no local page) vs `/pr00_coherence`. One href.
  Explicitly his call, deferred twice.
- `lastmod` on the 41 landings that changed content today — not bumped, deliberately.
- `kernel_first`'s **read page** JSON-LD says `Tier 0 · Gateway` (env display) while its
  **landing** correctly says `Tier 0 — Orientation` (grouping). Needs a template variable
  plus a rebuild, which needs the docx locally. One line, next time `kernel_first` rebuilds.
- **Logged drift surface, not worsened today:** the kernel is stated twice in the repo —
  `patch_kernel_terms.py`'s `TERMS` (→ DefinedTermSet) and `build_llms`'s prose (→
  llms.txt). Nothing compares them. If Symbols Reference goes to v1.8, both need updating.
  A unification was built today and **reverted** (§6) because it made llms.txt no better.

---

## 4. New this session

| Tool | Does |
|---|---|
| `fix_extension_hops.py` | repeatable — rewrites internal `.html` hops to canonical URLs; only when the extensionless path is in the sitemap; self-verifies zero remaining |
| `patch_landing_jsonld.py` | repeatable — JSON-LD onto 41 landings from ledger + the page's own lint-gated citation tags; refuses on DOI disagreement |
| `patch_kernel_terms.py` | repeatable — DefinedTermSet onto homepage + gateway; self-checks payload for the canonical operator before writing |
| `patch_position_blocks.py` | repeatable — Position in the Program from `site_data` relations |

`build_site_meta.py` gained `check_tier_envs`, `check_relations`, `build_library_json`. Both
gates run on **every** invocation including `--check`. `status.py` now imports `live_backlog`
— one definition.

**Lint checks 7, 8, 9** added (landing JSON-LD honest against ledger + canonical; extension
hops; declared relations must render). All negative-tested before first trust.

---

## 5. The record worth keeping: WP06 was answered, not abandoned

WP01 §0.7.1 forward-declares *"WP06: Synthetic Collapse"* — asking whether AI could exhibit a
**new, synthetic phase of collapse**, a *"Fourth Collapse"* structurally distinct from
Biological and Conscious. There is a live deposit called **AI as Synthetic Collapse**
(4WSYR). Near-identical name. It does not answer WP06's question — it **declines** it: model
behavior as constrained actualization, explicitly not machine consciousness, and the
architecture map's recursive-CIM node says AI "participates in collapse structurally but not
volitionally."

So WP06 wasn't dropped. **It was asked, and the answer came back "no fourth phase — recursive
CIM."** The speculative version got scoped down and the work shipped under a name that
survives the narrowing. That is the program doing exactly what it advertises, and it deserves
a record *because* it is a good outcome — a forward-declared question answered in the
negative on its most speculative part, with the corpus reorganized around the better answer.
A critical reader would be impressed to find that recorded and suspicious to find it quietly
dropped.

---

## 6. Traps — all real, all cost time today

The v3 handoff logged eighteen blind instruments. Today added five, and **three were mine**.
All the same shape: **a tool encoding one assumption about a world that has two.**

- **`?v=` cache-buster is a placebo on this zone.** `cf-cache-status: HIT` returns on
  never-seen query strings — the cache key ignores them. It never busted anything.
- **`raw.githubusercontent.com` carries `cache-control: max-age=300` and can be
  self-primed.** A pre-push fetch serves you the stale copy post-push. It reported `0` on a
  completed push. **The push output IS the landing confirmation** — `old..new main -> main`
  only prints when objects are on origin. The zero-cache content check is
  `git show origin/main:path`. Every HTTP instrument used today lied at least once; the git
  object store cannot.
- **Brace expansion is concatenation, not a numeric range.** `000{7,10}` → `0007` and
  `00010`. One no-match aborts the entire zsh line. Trace every glob before handing it over;
  no `<placeholders>` either — zsh parses `<` as a redirect.
- **Marker patchers leaked +2 spaces of indent per apply** while claiming idempotence,
  because `RE_BLOCK` matched the marker *text* and not its leading whitespace. The proof
  counted markers and passed. **Idempotence is proven by a second run producing zero bytes of
  diff.**
- **A partial read is not a read.** `head -12` of `llms.txt` plus a `grep -c` returning `1`
  produced an entire session's plan to add content the file already carried in full, ten
  lines below the cutoff — the kernel, both equations, the notation law, and the complete
  inoculation paragraph. That one matched line **was** the paragraph. `grep -c` counts lines,
  not structure — the rule was written into CLAUDE.md §10 that same morning and broken twice
  the same day.

All are now in `CLAUDE.md` §10 (three CLAUDE.md commits today: 0006, 0012/0013, and the §10
additions).

---

## 7. The honest close

**Three things that looked like gaps today were all the same thing wearing different
clothes.**

- The failure ladder a cold model proposed → already in TN7Z3, in more detail than proposed.
- The program-not-reality formulation, thought to be a new WP05 seed → already published,
  nearly verbatim, in Kernel First.
- The `llms.txt` negations, the premise of a whole session → already there, complete,
  upstream, better written than the replacement.

**Work that already exists, not being reached.** That is not a build problem.

The 2026-07-17 cold-read test ran itself harder than designed: no URL supplied, and a
clean-slate model found the program and summarized it without hallucinating acceptance. But
its cold pass **never reached the site** — it found descriptions of UCT elsewhere and
summarized those. Everything fits: *"beginning around 2025,"* *"a book,"* no DOIs, no tiers,
then *"having now found the current library"* only after Jeremy steered. That is a ranking
and indexing problem, and no file written here fixes it. Cloudflare's Referral Traffic column
is still all dashes.

The corpus is machine-legible, correctly citable, and now carries its own program graph. The
piping is finished. **The next unit of progress is not a tool, a lint, or an emitter — it is
the first serious external reader who engages critically with Jeremy out of the loop, and
that isn't a build task.**

Against contact-vs-accumulation: today was, again, neither. It removed the last reasons the
accumulation couldn't be cited correctly by whatever does find it. That is a precondition,
now essentially complete.

**If the next session's diff is large, re-read §6.**
