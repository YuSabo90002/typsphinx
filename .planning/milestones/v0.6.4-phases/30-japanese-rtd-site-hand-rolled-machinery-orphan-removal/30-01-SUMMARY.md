---
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
plan: 01
subsystem: infra
tags: [github-actions, tox, makefile, ci, gh-pages, sphinx]

# Dependency graph
requires:
  - phase: 30.1-translations-repository-japanese-rtd-site
    provides: the RTD-served Japanese site (typsphinx-doc-translations repo) that makes the
      hand-rolled multi-language build orchestration in this repository obsolete
provides:
  - "`.github/workflows/docs.yml` repointed at a single-language `docs/_build/html` tree (D-14):
    HTML build step renamed and repointed at `tox -e docs-html`, the PDF-copy-into-multilang step
    deleted, `Upload HTML artifact` path and `peaceiris/actions-gh-pages` `publish_dir` both
    repointed to `docs/_build/html`"
  - "`tox.ini`'s `[testenv:docs-multilang]` section removed — no caller in the repo still invokes
    the `build_multilang.py` script Plan 02 deletes"
  - "`docs/Makefile` reduced to the stock two-target Sphinx skeleton (`help` + catch-all `%`);
    six i18n/multi-language targets and their comments removed (D-12, D-13)"
affects: [30-02-build-multilang-deletion, 30-04-phase-evidence]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Caller/callee cross-check: every `tox -e <env>` string in a CI workflow was verified
      against the section list actually present in `tox.ini` before commit, closing the failure
      mode where a workflow only breaks the next time it runs"

key-files:
  created: []
  modified:
    - .github/workflows/docs.yml
    - tox.ini
    - docs/Makefile

key-decisions:
  - "D-14 applied exactly as scoped: the `peaceiris/actions-gh-pages` deploy step is repointed at
    `./docs/_build/html`, not removed — Phase 32 owns the teardown behind its own freshly-taken
    gate"
  - "docs/source/contributing.rst's Translations section required no edit (confirm-only): its
    `make locale-update` / `make locale-stat` instructions run inside a cloned
    `typsphinx-doc-translations` checkout, against that repository's own Makefile — verified by
    reading lines 293-321 before editing docs/Makefile"

requirements-completed: [I18N-02]

coverage:
  - id: D1
    description: "CI workflow repointed to build/publish a single English HTML tree from
      docs/_build/html; PDF-copy-into-multilang step deleted; deploy step survives unchanged
      apart from its publish_dir value"
    requirement: "I18N-02"
    verification:
      - kind: unit
        ref: "inline python verify script (yaml-parsed docs.yml structural assertions) — task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D2
    description: "tox.ini no longer declares the multi-language testenv or references the deleted
      build script; all other sections byte-unchanged"
    requirement: "I18N-02"
    verification:
      - kind: unit
        ref: "inline python verify script (regex section-list assertions) — task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/Makefile trimmed to help + catch-all %; six i18n/multilang targets removed;
      make -n help and make -n html still resolve through the catch-all"
    requirement: "I18N-02"
    verification:
      - kind: unit
        ref: "inline python verify script (target-list + line-count assertions) — task 2 <verify>"
        status: pass
      - kind: other
        ref: "make -C docs -n help / make -C docs -n html dry-run output"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-07-26
status: complete
---

# Phase 30 Plan 01: Repoint CI and Strip Multi-Language Build Machinery Summary

**Repointed `.github/workflows/docs.yml` and `tox.ini` off the deleted multi-language build tree
onto `docs/_build/html`, and trimmed `docs/Makefile` back to the stock two-target Sphinx skeleton
— three modified files, no file deleted, no new file created.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-26T11:21:00Z
- **Completed:** 2026-07-26T11:33:11Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- `.github/workflows/docs.yml`'s `build-docs` job dropped from 11 to exactly 10 steps: the HTML
  build step is now named `Build HTML documentation` and runs `uv run tox -e docs-html`; the
  `Copy PDF to multi-language build (English version)` step is gone entirely; `Upload HTML
  artifact`'s `path` and the `peaceiris/actions-gh-pages` step's `publish_dir` both now read
  `docs/_build/html` / `./docs/_build/html` (D-14)
- The `peaceiris/actions-gh-pages` step survives byte-unchanged apart from `publish_dir`, still
  carrying `github_token` and `cname: false`; the `softprops/action-gh-release` tag-time step is
  untouched; `permissions:` and the trigger key set (`push`, `pull_request`) are unchanged
- `tox.ini`'s `[testenv:docs-multilang]` section (the sole caller of `python build_multilang.py`)
  is deleted; `[testenv:docs-html]`, `[testenv:docs-pdf]`, `[testenv:docs]`, `env_list`, and the
  `tox-uv~=1.35` pin (with its explanatory comment) are all byte-unchanged
- `docs/Makefile` is now exactly 20 lines declaring two targets — `help` and the catch-all `%` —
  with `.PHONY: help Makefile`; the six removed targets are `gettext`, `locale-init`,
  `locale-update`, `html-ja` (D-13), `multilang`, and `serve-multilang` (D-12)
- Confirmed by reading `docs/source/contributing.rst` lines 293-321 that its Translations section
  needs no edit: its `make locale-update` / `make locale-stat` instructions run inside a cloned
  `typsphinx-doc-translations` checkout (`cd typsphinx-doc-translations` at line 307), targeting
  that repository's own Makefile — the section is byte-unchanged (`git diff --quiet` exits 0)

## Task Commits

Each task was committed atomically:

1. **Task 1: Repoint the CI workflow and remove the multi-language testenv** - `20a7f9b` (feat)
2. **Task 2: Strip the i18n and multi-language targets from docs/Makefile (D-12, D-13)** - `b1269f5` (feat)

**Plan metadata:** commit will follow (docs: complete plan) — orchestrator-owned in worktree mode.

## Files Created/Modified
- `.github/workflows/docs.yml` - HTML build step renamed/repointed to `tox -e docs-html`;
  PDF-copy-into-multilang step removed; `Upload HTML artifact` path and gh-pages `publish_dir`
  repointed to `docs/_build/html`
- `tox.ini` - `[testenv:docs-multilang]` section removed
- `docs/Makefile` - reduced to `help` + catch-all `%`; six i18n/multilang targets and comments removed

## Decisions Made
- Applied D-14 exactly as scoped in the plan: repoint the deploy step's `publish_dir`, do not
  remove the step. The removal is Phase 32's single irreversible action, gated behind its own
  freshly re-taken observation.
- No edit to `docs/source/contributing.rst` — confirmed by direct read that its Translations
  section already targets the separate `typsphinx-doc-translations` repository's own Makefile,
  so this repository's target removal does not falsify anything it says.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` scripts printed
`FAILED: []` on the first attempt; no auto-fixes were needed.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - no stub patterns introduced. Both edits are pure deletions/repoints of existing CI/build
config; no new code paths or placeholder values were added.

## Threat Flags
None - this plan introduces no new security-relevant surface. All three files edited are CI/build
configuration path bookkeeping (D-14's `publish_dir` repoint, testenv/target removal), covered by
the plan's own `<threat_model>` (T-30-01 through T-30-04, all `mitigate`/low-medium, none `high`).

## Next Phase Readiness
- The surviving CI/tox/Makefile surface no longer references `docs/build_multilang.py`,
  `docs/source/_templates/language-switcher.html`, or `docs/locale/ja/` by name, so Plan 02
  (which deletes those files) will not leave any caller pointing at a now-missing target.
- The `peaceiris/actions-gh-pages` deploy step remains intact and repointed, ready for Phase 32
  to remove it behind its own gate.
- No blockers. `git status --porcelain typsphinx/` is empty throughout, honoring milestone
  invariant #3.

---
*Phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-01-SUMMARY.md`
- FOUND: `.github/workflows/docs.yml`
- FOUND: `tox.ini`
- FOUND: `docs/Makefile`
- FOUND commit: `20a7f9b` (Task 1)
- FOUND commit: `b1269f5` (Task 2)
- FOUND commit: `d0d8b1c` (SUMMARY.md)
