---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
plan: 03
subsystem: testing
tags: [pytest, black, mypy, ruff, tox, sphinx, linkcheck, changelog]

# Dependency graph
requires:
  - phase: 73 (wave 1, plans 73-01/73-02)
    provides: CHANGELOG.md's two new bullets (73-01), PHASE_BASE_SHA and MILESTONE_BASE anchors (73-02)
provides:
  - "SC#3 local half MET: full pytest suite green twice (once under LC_ALL=C), format/type/lint clean, version-sync family clean, changelog page gate 0-skipped, both docs environments clean-built against 73-01's baseline with zero multiple-toctrees, tox -e linkcheck 95/95 working"
affects: [73-07 (phase handoff, compares this plan's evidence with 73-04's CI and 73-05's pre-flight)]

actuals:
  tokens: 45000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: [clean-rebuild docs baselines under LANG=C LC_ALL=C, output.json-sourced linkcheck verdicts, per-plan mktemp scratch directories for parallel worktree isolation]

key-files:
  created:
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-GREEN-TREE-EVIDENCE.md
  modified: []

key-decisions:
  - "Used PHASE_BASE_SHA from 73-CLOSEOUT-GUARD.md (not the plan's own BASE_73_03) for the product-tree delta check, per the plan's explicit read_first instruction — the delta from the phase's true starting point, not from this plan's own commit history."
  - "Both this worktree and the main checkout resolved to the identical nixpkgs Python 3.13.13 interpreter (same home path), so no interpreter-drift caveat was needed when comparing suite counts to Phase 72's."

requirements-completed: []

coverage:
  - id: D1
    description: "Full pytest suite proven green on the merged tree, twice (once under LC_ALL=C matching CI's locale)"
    requirement: REL-14
    verification:
      - kind: other
        ref: "uv run pytest -q -rs -p no:cacheprovider (1547 passed, 1 skipped, 0 failed)"
        status: pass
      - kind: other
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider (1547 passed, 1 skipped, 0 failed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "black, mypy and ruff all exit 0 on the worktree, local ruff version matches uv.lock's pin"
    requirement: REL-14
    verification:
      - kind: other
        ref: "uv run black --check . ; uv run mypy typsphinx/ ; uv run ruff check ."
        status: pass
    human_judgment: false
  - id: D3
    description: "Version-sync test family (readme, preview, extension pyproject) passes"
    requirement: REL-14
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py, tests/test_preview_version_sync.py, tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
    human_judgment: false
  - id: D4
    description: "Changelog page gate runs with the docs extra present and 0 skipped"
    requirement: REL-14
    verification:
      - kind: integration
        ref: "tests/test_changelog_page_gate.py (6 passed, 0 skipped)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both docs tox environments built clean under LANG=C LC_ALL=C match 73-01's phase-base baseline with zero multiple-toctrees lines, and the PDF is real"
    requirement: REL-14
    verification:
      - kind: other
        ref: "rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-html / docs-pdf"
        status: pass
    human_judgment: false
  - id: D6
    description: "tox -e linkcheck passes with every checked link working, read from output.json"
    requirement: REL-14
    verification:
      - kind: other
        ref: "uv run tox -e linkcheck; docs/_build/linkcheck/output.json (95/95 working)"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-09-16
status: complete
commits: 3
plan_head_before: a54a2d8a3b06b388c7ee004e5cfbe3405431421d
---

# Phase 73 Plan 03: Local Green-Tree Evidence (SC#3, local half) Summary

**Proved the phase's own merged tree green on runs executed in this worktree: full pytest suite 1547 passed/1 skipped twice (once under `LC_ALL=C`), black/mypy/ruff clean, version-sync and changelog-gate families clean, both docs environments clean-built matching 73-01's baseline with zero multiple-toctrees, and `tox -e linkcheck` 95/95 links working — `SC3_LOCAL_VERDICT = MET`.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-09-16T10:01:00Z (approx.)
- **Completed:** 2026-09-16T10:22:31Z
- **Tasks:** 3
- **Files modified:** 1 (one file created, appended to across all three tasks)

## Accomplishments

- Tree identity confirmed: `typsphinx.__file__` resolves inside this worktree (not the main
  checkout's editable install), `myst_parser` importable (docs extra present), and both this
  worktree and the main checkout run the identical nixpkgs Python 3.13.13 interpreter.
- Product-tree delta from `PHASE_BASE_SHA` (`73-CLOSEOUT-GUARD.md`) is exactly `CHANGELOG.md`
  (15 insertions, 0 deletions); `docs/source/conf.py` unchanged; merge-base of HEAD and
  `origin/main` still equals `MILESTONE_BASE` — `main` not absorbed.
- Full pytest suite: 1547 passed, 1 skipped (env-gated corpus test), 0 failed — run twice, once
  under `LC_ALL=C` to reproduce CI's locale — both runs matching Phase 72's counts exactly.
- `black --check .`, `mypy typsphinx/` and `ruff check .` all exit 0; local ruff 0.16.6 matches
  `uv.lock`'s pin. The version-sync family (readme, preview, extension pyproject) all pass. The
  changelog page gate ran with the docs extra present and 0 skipped (6 passed).
- Both docs tox environments (`docs-html`, `docs-pdf`) built clean under `LANG=C LC_ALL=C` after
  `rm -rf docs/_build`, matching 73-01's clean phase-base baseline exactly (3 and 5 warnings
  respectively), zero multiple-toctrees lines, and the rebuilt PDF begins `%PDF-`.
- `tox -e linkcheck` ran once from a clean output directory: all 95 checked links `working`
  (read from `output.json`, never console text), no `linkcheck_*` key added to
  `docs/source/conf.py`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — tree identity, product delta and non-absorption, full pytest suite** -
   `35147d05` (docs)
2. **Task 2: LC_ALL=C full suite, format/type/lint, version-sync, changelog page gate** -
   `34e79ef1` (docs)
3. **Task 3: Docs builds, linkcheck, executed-vs-skipped, SC#3 local verdict** - `451eb72c`
   (docs)

_Note: TDD is not applicable to this plan (`phase.tdd-applicable` resolved `false`)._

## Files Created/Modified

- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-GREEN-TREE-EVIDENCE.md` - all
  evidence for SC#3's local half, appended across all three tasks

## Decisions Made

- Used `PHASE_BASE_SHA` from `73-CLOSEOUT-GUARD.md` (not this plan's own `BASE_73_03`) as the
  anchor for the product-tree delta and `docs/source/conf.py`-unchanged checks, per the plan's
  explicit instruction — this measures the delta from the phase's true starting point across all
  of wave 1's commits, not merely from this plan's own commit history.
- No interpreter-drift caveat was needed: both this worktree's and the main checkout's
  `.venv/pyvenv.cfg` report the identical nixpkgs `python3-3.13.13` `home` path, so suite counts
  compared directly against Phase 72's recorded counts with no adjustment.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#3's local half is closed on runs executed in this phase (D-14): every figure was taken from a
  command quoted beside it in `73-GREEN-TREE-EVIDENCE.md`.
- This plan does not read plan 73-04's CI result or plan 73-05's pre-flight result — both run in
  parallel and share no file with this plan. Plan 73-07 sets all three evidence files side by side
  in the phase handoff.
- No blockers. `SC3_LOCAL_VERDICT = MET`.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Completed: 2026-09-16*

## Self-Check: PASSED

- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-GREEN-TREE-EVIDENCE.md` exists
  (verified with `[ -f ]` before writing this SUMMARY).
- `git log --oneline --all` contains all three task commit hashes (`35147d05`, `34e79ef1`,
  `451eb72c`), confirmed present in this worktree's own history.
- `SC3_LOCAL_VERDICT = MET` re-confirmed by `grep` against `73-GREEN-TREE-EVIDENCE.md` immediately
  before writing this SUMMARY.
- No `## HALT` heading anywhere in `73-GREEN-TREE-EVIDENCE.md`.
- Measured commit count for this plan: `git rev-list --count a54a2d8a3b06b388c7ee004e5cfbe3405431421d..HEAD` = 3, matching `commits: 3` in the frontmatter above.
