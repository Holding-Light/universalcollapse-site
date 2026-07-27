# Add Three Papers — Runbook (2026-07-27)

FWF · HIL · AIML → live, per `UCT_Site_Update_Note_Faith_and_New_Cards_2026_07_19.md`
§C/§D. One pass, every step gated. **Run everything from `~/universalcollapse-site`.**
Architecture map (§A/§B of the note) is a separate later pass — not here.

Landing numbers when done: **44 papers · 41 read pages · 90 sitemap URLs · 177 edges.**

---

## Phase 1 — Sweep the failed session (2 min)

```bash
cd ~/universalcollapse-site

# preserve the session's half-applied architecture cards for the later pass
git stash push tools/UCT_Architecture_Map_v4.jsx -m "session B-cards attempt 2026-07-27"

# back up its FWF landing (ours replaces it), then clear its scratch
mv public/faith_without_fideism.html /tmp/fwf_landing_session_backup.html
rm -f tools/add_papers_2026_07_27.py
rm -rf tools/oneshots

# revert its ledger edit and the stale build outputs (regenerated later)
git checkout -- tools/site_data.yaml public/library.json public/llms.txt public/sitemap.xml

# de-track macOS junk
git rm --cached .DS_Store 2>/dev/null; rm -f .DS_Store tools/.DS_Store
grep -qx '.DS_Store' .gitignore || echo '.DS_Store' >> .gitignore

git status --short
```

**KEEP untouched:** the `CLAUDE.md` modification (it is the legitimate 2026-07-20
refresh — commits with this pass), `public/read/faith_without_fideism.html`,
`public/pdf/UCT_T0_Faith_Without_Fideism_Named_Floor_v1_0_2026_07.pdf`,
`tools/faith_without_fideism.env`, `tools/uct_lint.py`.

Expected status after sweep: `M CLAUDE.md` + the kept untracked FWF trio + this
package's files once untarred. Nothing else.

## Phase 2 — Place the package + PDFs

```bash
tar xzf ~/Downloads/add3_package.tar.gz -C ~/universalcollapse-site
# → public/{faith_without_fideism,human_interface_laws,ai_meaning_layer}.html
# → tools/{human_interface_laws,ai_meaning_layer}.env
# → tools/add_three_papers.py  +  this README

# copy the two published PDFs in, EXACT names:
cp "<your published pdf folder>/UCT_T15_Human_Interface_Laws_v1_0_2026_07.pdf"  public/pdf/
cp "<your published pdf folder>/UCT_T15_AI_in_the_Meaning_Layer_v1_0_2026_05.pdf" public/pdf/
```

## Phase 3 — Apply the ledger (also fills the env hashes)

```bash
python3 tools/add_three_papers.py           # dry run — read every line it prints
python3 tools/add_three_papers.py --apply
```

Gates inside: 3 landings + 3 PDFs present (read pages come next) → pdf+docx sha256
computed; `SRC_SHA256` injected into both new envs → slugs absent (refuses
double-apply) → single anchor → post-parse: **44 papers, all edges resolve to built
slugs, AIML carries no philarchive key.**

## Phase 4 — Build read pages (HIL, AIML)

```bash
bash tools/build_paper.sh tools/human_interface_laws.env
bash tools/build_paper.sh tools/ai_meaning_layer.env
```

The hash guard now passes (Phase 3 filled `SRC_SHA256` from your actual docx).
FWF's read page already exists from the earlier session — leave it.

## Phase 5 — Meta build + patchers

```bash
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/ --check
python3 tools/build_site_meta.py --data tools/site_data.yaml --out public/
for p in patch_landing_jsonld patch_position_blocks fix_landing_read_cta \
         patch_llms_link fix_extension_hops; do
  python3 tools/$p.py            # dry-run: review
  python3 tools/$p.py --apply
done
```

## Phase 6 — Gates

```bash
python3 tools/uct_lint_html.py public/*.html public/read/*.html --landing \
    --papers-from tools/site_data.yaml --sitemap public/sitemap.xml
python3 tools/lint_doi_shadow.py
python3 tools/check_operator.py public/read/faith_without_fideism.html \
    public/read/human_interface_laws.html public/read/ai_meaning_layer.html
```

Want: **85 pages — 0 errors** (warnings: the known trio + anything NOTATION-new on
the three read pages → adjudicate via `check_conversion.py` same as the trio, do not
hand-edit); shadow ✓; operator gate clean. Then render-verify: open all three
landings and read pages in a browser; check title, DOI link, PDF link, position
block, related cards.

## Phase 7 — Ship

```bash
git add -A
git status --short        # review: nothing unexpected
git commit -m "Add FWF, HIL, AIML: landings, read pages, PDFs, ledger (+CLAUDE.md 07-20 refresh)"
git push                  # must print main -> main
git show origin/main:tools/site_data.yaml | grep -c 'slug:'   # want 44+
curl -s https://universalcollapse.com/sitemap.xml | grep -c '<loc>'   # want 90 (~2 min after push)
```

Then tell the other side of this session — the live-verification sweep runs from
there: all 90 URLs, notation law, citation tags on the three new landings, JONFWF/
JONHIL on their surfaces.

## Afterward (separate passes, not now)

- Architecture map: `git stash pop` the session attempt **or** apply §B of the
  07-19 note fresh → `bash tools/build_architecture.sh` → verify gate.
- Roadmap page: HIL status flip ×4 + AIML row + FWF row (§C7).
- Library page: three authored rows (§C1) + patchers.
- DOI Registry v2.9: FWF row (`PF5RZ` + `JONFWF`) — the registry gap found today.
