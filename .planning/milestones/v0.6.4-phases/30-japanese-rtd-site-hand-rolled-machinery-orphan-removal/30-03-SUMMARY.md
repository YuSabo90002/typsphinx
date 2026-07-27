---
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
plan: 03
subsystem: docs
tags: [sphinx, rst, gettext, sphinx-intl, orphan-cleanup, i18n]

# Dependency graph
requires:
  - phase: 30.1-translations-repository-japanese-rtd-site
    provides: "typsphinx-doc-translations repository holding a live copy of the 13 ja .po catalogs, confirmed in this run"
provides:
  - "docs/usage.rst and root-level docs/installation.rst removed (819 unreachable lines), together with the 20 collateral test functions that hard-asserted their existence"
  - "docs/locale/ (26 tracked files: 13 .po + 13 .mo) removed from this repository — the catalogs' only remaining copy is typsphinx-doc-translations"
affects: ["31-published-url-cutover", "32-github-pages-teardown"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Orphan-doc deletion pattern (Phase 27 precedent, commit 90801cf): delete subject + its hard-asserting test in one atomic commit, verify full suite green after the commit, not the commit itself"

key-files:
  created: []
  modified: []
  # This plan is deletion-only; the following paths were removed, nothing created or edited.

key-decisions:
  - "D-11 salvage-nothing honored: docs/usage.rst's Continuous Integration and Build Commands Reference sections have no counterpart under docs/source/ and are accepted as permanently lost (git history retains the file)"
  - "PD-01 (STATE.md carry-forward) honored over an earlier ROADMAP SC#3 reading: docs/locale/ja/LC_MESSAGES/installation.po is deleted with the rest of docs/locale/, since the catalog that actually builds the ja RTD site lives in typsphinx-doc-translations, not this repository"

patterns-established: []

requirements-completed: [DOC-08, I18N-02]

coverage:
  - id: D1
    description: "docs/usage.rst (606 lines) and root-level docs/installation.rst (213 lines) deleted along with their two hard-asserting test files (12 + 8 = 20 test functions), in one atomic commit; docs/source/installation.rst (76 lines, toctree-live) verified byte-unchanged"
    requirement: "DOC-08"
    verification:
      - kind: unit
        ref: "uv run python -m pytest -q (full suite, post-deletion) — 641 passed, 1 skipped"
        status: pass
      - kind: other
        ref: "git show --stat 86633c4 — exactly 4 files deleted, 0 added, 0 modified; git diff --quiet HEAD~1 -- docs/source/installation.rst"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/locale/ (26 git-tracked files: 13 .po + 13 .mo) deleted after confirming the typsphinx-doc-translations repository holds 13 .po files under locale/ on its main branch; conf.py's locale_dirs / gettext_* block and .gitignore left byte-unchanged; English HTML build warning-for-warning identical to the 2-warning visit_toctree baseline"
    requirement: "I18N-02"
    verification:
      - kind: unit
        ref: "uv run python -m pytest -q (full suite, post-deletion) — 641 passed, 1 skipped"
        status: pass
      - kind: other
        ref: "gh api repos/YuSabo90002/typsphinx-doc-translations/git/trees/HEAD?recursive=1 --jq '[.tree[]|select(.path|test(\"^locale/.*[.]po$\"))]|length' -> 13"
        status: pass
      - kind: other
        ref: "uv run python -m sphinx -b html -w <warnfile> docs/source <throwaway> -> exit 0, 2 warnings, both visit_toctree"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-07-26
status: complete
---

# Phase 30 Plan 03: Orphan doc pair + relocated locale catalog removal Summary

**Deleted the unreachable `docs/usage.rst` / root `docs/installation.rst` pair with their 20 collateral test functions in one commit, then deleted the relocated `docs/locale/` catalog tree (26 tracked files) in a second commit after live-confirming 13 `.po` files survive in `typsphinx-doc-translations` — full suite green (641 passed, 1 skipped) and the English HTML build warning-for-warning identical to baseline (2 `visit_toctree` warnings) after both deletions.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-07-26T11:36:48Z
- **Tasks:** 2
- **Files modified:** 0 created/edited; 30 files deleted (4 + 26)

## Accomplishments

- Removed the two unreachable root-level documents (`docs/usage.rst`, 606 lines; `docs/installation.rst`, 213 lines) together with the two test files that hard-asserted their existence (`tests/test_documentation_usage.py`, 12 test functions; `tests/test_documentation_installation.py`, 8 test functions) — one atomic commit, matching the Phase 27 `90801cf` precedent shape exactly (N files deleted, 0 added, 0 modified).
- Removed the entire `docs/locale/` tree (13 `.po` catalogs + 13 `.mo` binaries, 26 git-tracked files) after live-confirming, in this run, that the `typsphinx-doc-translations` repository holds 13 `.po` files under `locale/` on its `main` branch — closing STATE.md's PD-01 carry-forward.
- `docs/source/installation.rst` (76 lines, toctree-live) verified byte-unchanged by both commits; `docs/source/conf.py`'s `locale_dirs` / `gettext_*` block and `.gitignore`'s `*.mo` rule verified byte-unchanged by the locale deletion.
- English HTML build re-run after the locale deletion: exit 0, exactly the 2 pre-existing `visit_toctree` docstring warnings — the absent `locale_dirs` target introduces nothing new.
- Full `pytest` suite run after each commit: 641 passed / 1 skipped both times (662 collected before Task 1, 642 after — the delta is exactly the 20 removed test functions, 12 from `test_documentation_usage.py` + 8 from `test_documentation_installation.py`).

## Task Commits

1. **Task 1: Delete the orphan document pair with its collateral tests — one commit (D-11)** - `86633c4` (docs)
2. **Task 2: Remove the relocated locale catalogs (STATE.md PD-01)** - `131ae4a` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified

Deletion-only plan — nothing created or edited. Files removed:

- `docs/usage.rst` — deleted (606 lines)
- `docs/installation.rst` — deleted (213 lines, root orphan; distinct from the toctree-live `docs/source/installation.rst`)
- `tests/test_documentation_usage.py` — deleted (153 lines, 12 test functions)
- `tests/test_documentation_installation.py` — deleted (143 lines, 8 test functions)
- `docs/locale/ja/LC_MESSAGES/**` — deleted (26 tracked files: 13 `.po` + 13 `.mo`)

## Total deletion scope of this plan: 30 files

For the owner's manual merge past `worktree.cleanup-wave`'s deletion guard: this plan's two commits together delete exactly 30 tracked paths (4 in commit `86633c4`, 26 in commit `131ae4a`) and modify or create zero paths.

## Reachability grep (Task 1, pre-deletion)

Command run:

```
grep -rn "docs/usage\.rst\|docs/installation\.rst\|usage\.rst\b" . \
  --exclude-dir=.git --exclude-dir=.planning --exclude-dir=.venv --exclude-dir=.tox \
  --exclude-dir=_build --exclude-dir=node_modules --exclude="CHANGELOG.md"
```

Output: 27 hits, every one inside `tests/test_documentation_installation.py` (2 hits) or `tests/test_documentation_usage.py` (25 hits) — the two files that left in the same commit. No toctree, README, workflow, or other `.rst` referenced either root document. `docs/source/index.rst`'s four toctrees (Getting Started: `installation`, `quickstart`; User Guide: `user_guide/*`; Examples: `examples/*`; API Reference: `api/index`; Development: `contributing`, `changelog`) list no `usage` docname and resolve their `installation` entry to `docs/source/installation.rst`, confirmed by direct read.

## Collected-test count (Task 1)

- **Before deletion:** `662 tests collected` (`uv run python -m pytest --collect-only -q`)
- **After deletion:** full-run summary `641 passed, 1 skipped` = 642 collected
- **Delta:** 662 − 642 = 20, exactly `grep -c "^def test_" tests/test_documentation_usage.py tests/test_documentation_installation.py` = 12 + 8 = 20. No other test collection changed.

## Content accepted as lost (D-11)

`docs/usage.rst`'s top-level `====` sections, per its own headings (measured via grep before deletion): `Usage` (title), `Quick Start`, `Basic Workflow`, `Common Use Cases`, `Continuous Integration`, `Build Commands Reference`, `Best Practices`. Of these, `Continuous Integration` and `Build Commands Reference` have no counterpart anywhere under `docs/source/` and are the two sections D-11 explicitly names as accepted loss — reasoning: the file had not been touched since 2026-07-04 and most likely carries the same drift-from-implementation that made `docs/configuration.rst` a liability in Phase 27 (D-11, `.planning/phases/30-.../30-CONTEXT.md`). Git history (this repository's log up to and including commit `86633c4`) retains the full original content.

## `.po` count measured in `typsphinx-doc-translations` (Task 2, pre-deletion)

Command run:

```
gh api "repos/YuSabo90002/typsphinx-doc-translations/git/trees/HEAD?recursive=1" \
  --jq '[.tree[]|select(.path|test("^locale/.*[.]po$"))]|length'
```

Output: `13`. Also confirmed the repository's `default_branch` is `main` (`gh api repos/YuSabo90002/typsphinx-doc-translations --jq '.default_branch'`), i.e. this count was taken against the branch that actually builds the ja RTD project, not an unmerged feature branch — a stronger measurement than the plan's stated fallback of checking `gsd/v0.6.4-read-the-docs-migration`. The 13 paths listed by that query:

```
locale/ja/LC_MESSAGES/api/index.po
locale/ja/LC_MESSAGES/changelog.po
locale/ja/LC_MESSAGES/contributing.po
locale/ja/LC_MESSAGES/examples/advanced.po
locale/ja/LC_MESSAGES/examples/basic.po
locale/ja/LC_MESSAGES/examples/index.po
locale/ja/LC_MESSAGES/index.po
locale/ja/LC_MESSAGES/installation.po
locale/ja/LC_MESSAGES/quickstart.po
locale/ja/LC_MESSAGES/user_guide/builders.po
locale/ja/LC_MESSAGES/user_guide/configuration.po
locale/ja/LC_MESSAGES/user_guide/index.po
locale/ja/LC_MESSAGES/user_guide/templates.po
```

This matches, name-for-name (minus the `docs/` prefix and `LC_MESSAGES` suffix segment already accounted for), the 13 `.po` files removed locally in this run (`git ls-files docs/locale | grep -c '\.po$'` = 13 before the `git rm -r`).

## 26-file breakdown of the locale deletion

`docs/locale/ja/LC_MESSAGES/` held, pre-deletion: 13 `.po` catalogs (`api/index`, `changelog`, `contributing`, `examples/advanced`, `examples/basic`, `examples/index`, `index`, `installation`, `quickstart`, `user_guide/builders`, `user_guide/configuration`, `user_guide/index`, `user_guide/templates`) and their 13 compiled `.mo` counterparts, force-added past `.gitignore`'s blanket `*.mo` rule (`.gitignore:49`). `git rm -r docs/locale/` removed all 26 in commit `131ae4a`; `git ls-files docs/locale` returns nothing afterward.

## Decisions Made

- **PD-01 wins over the earlier ROADMAP SC#3 reading**, per the plan's `<flagged_probe_assumptions>`: `docs/locale/ja/LC_MESSAGES/installation.po` is deleted along with the rest of `docs/locale/`, even though an earlier SC#3 draft said the live `docs/source/installation.rst` "and its `.po` catalog" stay byte-unchanged. The surviving catalog SC#3 was protecting is the one in `typsphinx-doc-translations`, confirmed present in this run — not the local copy, which this phase's whole purpose is to retire.
- **`docs/source/conf.py`'s `locale_dirs` / `gettext_*` block is left in place**, per the plan and D-06/D-12 of `30-CONTEXT.md`: it is shared byte-for-byte with the translations repository's own copy of `conf.py`, and the empirical English-build check in this run confirms it no-ops harmlessly with the directory absent (0 new warnings, exit 0).

## Deviations from Plan

**None** — plan executed exactly as written. One environment note, not a deviation: the plan's `<execution_environment>` block specifies `uv run --extra docs python -m sphinx` for the English HTML build; the worktree's initial `uv sync --extra dev` (per CLAUDE.md's standing provisioning instruction) did not include the `docs` extra, so the first build attempt failed with `Could not import extension sphinx_autodoc_typehints`. Re-ran `uv sync --extra dev --extra docs` (adding the extra the plan already named) before repeating the build check, which then passed. No code, test, or deletion scope changed — this was purely completing the plan's own stated provisioning step.

## Issues Encountered

None beyond the environment note above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 30's remaining plans (Plan 01: `build_multilang.py`/tox/template/CSS/conf.py machinery removal; Plan 02: `docs/Makefile` + `docs.yml` targets; Plan 04, if any) are unaffected by this plan's scope — this plan touched only the orphan doc pair and `docs/locale/`.
- Total deletion scope of this plan (30 files, 0 added, 0 modified) is ready for the owner's manual merge past `worktree.cleanup-wave`'s deletion guard, per the expected block documented in STATE.md and `30-CONTEXT.md`.
- The three post-merge flips (parent RTD Default branch → `main`, ja Default branch → `main`, `.gitmodules` `branch` → `main`) remain owed to Phase 33 and are unaffected by this plan.

## Self-Check: PASSED

- FOUND: `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-03-SUMMARY.md`
- CONFIRMED: `docs/usage.rst` absent, `docs/installation.rst` absent, `docs/locale` absent
- CONFIRMED: `docs/source/installation.rst` present (toctree-live sibling, untouched)
- FOUND commits: `86633c4`, `131ae4a`, `9f6e1d6`

---
*Phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal*
*Completed: 2026-07-26*
