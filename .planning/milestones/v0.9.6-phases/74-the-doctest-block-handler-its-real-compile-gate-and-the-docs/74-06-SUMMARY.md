---
phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
plan: 06
subsystem: ci-evidence
tags: [gates, scope-fence, sc4, api-coverage, evidence]

# Dependency graph
requires:
  - phase: 74-01
    provides: PHASE_BASE_SHA, the base census, milestone base 6cc44f22
  - phase: 74-02
    provides: RED_TREE_SHA, RED_VERDICT = MET
  - phase: 74-03
    provides: GREEN_TREE_SHA, GREEN_VERDICT = MET
  - phase: 74-04
    provides: QUA14_FIX_VERDICT = MET
provides:
  - "74-GATES-EVIDENCE.md: the wave 1-3 verdict audit, both full pytest runs (plain and LC_ALL=C),
    the lint trio, the @preview invariant, the scope fence with pathspec/widened-diff controls,
    the standing-invariant reads, the test-edit census, and SC4_LOCAL_VERDICT = MET"
  - "COVERAGE.md: the one-line no-external-API declaration, with the api-coverage.verify-pre gate
    recorded passing"
affects: [74-07]

# Actuals (#2632)
actuals:
  tokens: 2151
  tasks: 2
  commits: 2
  plan_head_before: c043950b58ed5e1030c1b17449b46a7c9b4fe85b

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Evidence-only plan: zero product-code files touched, confirmed by a diff against BASE_74_06
      excluding .planning/ being empty at both task boundaries"
    - "Bare KEY = value evidence lines with explanation on the following line, verified by a
      no-parenthesis-in-key-line grep before each commit"

key-files:
  created:
    - .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-GATES-EVIDENCE.md
    - .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/COVERAGE.md
  modified: []

key-decisions:
  - "Provisioned the worktree venv with uv sync --extra dev --extra docs --python 3.13.13 (per
    <worktree_provisioning>), confirming CHANGELOG_GATE_SKIPS = 0 across both full pytest runs --
    the docs extra is what keeps tests/test_changelog_page_gate.py from skipping in a worktree."
  - "Ran the full pytest suite twice as specified -- once plain, once under LC_ALL=C -- and recorded
    both as separate saved logs under a mktemp -d scratch dir, per-run skip reasons transcribed
    verbatim rather than summarized."
  - "Region-scoped the translator.py and pathfmt.py hunks by new-side start line against
    grep-derived anchor lines (visit_literal_block/visit_definition_list/visit_toctree/
    quote_path), matching every hunk to its scoped window before writing TRANSLATOR_HUNKS_OUTSIDE_SCOPE."

requirements-completed: [TRN-01, TRN-02, QUA-14]

coverage:
  - id: D1
    description: "SC4 local gates: lint trio, full pytest suite (plain and LC_ALL=C) and the
      @preview invariant all green on the phase tip in the provisioned worktree venv, with zero
      tests/test_changelog_page_gate.py skips"
    requirement: "TRN-01"
    verification:
      - kind: other
        ref: "74-GATES-EVIDENCE.md ## Lint trio / ## Full pytest / ## @preview invariant (RUFF_EXIT=0, BLACK_EXIT=0, MYPY_EXIT=0, FULL_PYTEST_EXIT=0, FULL_PYTEST_C_EXIT=0, PREVIEW_SYNC_EXIT=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC4 scope fence: typsphinx/ diff is exactly pathfmt.py and translator.py with
      pathspec and widened-diff controls; every hunk lies in its scoped region"
    requirement: "TRN-02"
    verification:
      - kind: other
        ref: "74-GATES-EVIDENCE.md ## Scope fence: typsphinx/ (TRANSLATOR_HUNKS_OUTSIDE_SCOPE = 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC4 standing invariants: .github/ and flake.nix absent from the milestone diff
      (with a tracked-path control), pyproject.toml/uv.lock/typsphinx/__init__.py unchanged,
      version still 0.9.2 at HEAD and at the base"
    requirement: "QUA-14"
    verification:
      - kind: other
        ref: "74-GATES-EVIDENCE.md ## Standing invariants (WORKFLOWS_FLAKE_UNTOUCHED=yes, PYPROJECT_UV_LOCK_INIT_UNTOUCHED=yes, VERSION_AT_CLOSE=0.9.2)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Zero pre-existing test edits: tests/ diff is all added files plus a
      deletion-free tests/test_translator.py; COVERAGE.md satisfies the api-coverage gate;
      SC4_LOCAL_VERDICT recorded MET for 74-07 to gate on"
    requirement: "QUA-14"
    verification:
      - kind: other
        ref: "74-GATES-EVIDENCE.md ## Test-edit census / ## API coverage declaration / ## SC4 local verdict (PREEXISTING_TEST_DELETIONS=0, API_COVERAGE_PASSED=true, SC4_LOCAL_VERDICT=MET)"
        status: pass
    human_judgment: false

duration: 17 min
completed: 2026-09-20
status: complete
---

# Phase 74 Plan 06: SC4 Local Gates and Scope Fence Summary

**FULL_PYTEST_PASSED = 1562, FULL_PYTEST_C_PASSED = 1562, skip reasons: `tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it` (one skip, identical in both runs; zero `tests/test_changelog_page_gate.py` skips), TYPSPHINX_DIFF_FILES = typsphinx/pathfmt.py|typsphinx/translator.py, VERSION_AT_CLOSE = 0.9.2, SC4_LOCAL_VERDICT = MET**

Discharged SC4's local half on the phase tip: the wave 1-3 verdict audit (RED_VERDICT, GREEN_VERDICT
and QUA14_FIX_VERDICT all read `MET`), the lint trio, the full pytest suite twice (plain and
`LC_ALL=C`), the `@preview` invariant, constraint 7's scope fence with pathspec and widened-diff
controls, the standing invariants, the zero-pre-existing-test-edit census, and `COVERAGE.md` for the
api-coverage gate — all green, all recorded in `74-GATES-EVIDENCE.md`.

## Performance

- **Duration:** 17 min
- **Started:** 2026-09-19T23:00:00Z (approx., provisioning start)
- **Completed:** 2026-09-19T23:17:00Z
- **Tasks:** 2
- **Files modified:** 2 (both new: `74-GATES-EVIDENCE.md`, `COVERAGE.md`)

## Accomplishments
- Provisioned the worktree venv with `uv sync --extra dev --extra docs --python 3.13.13`, recording
  the interpreter (`3.13.13`, uv-managed nix store path) — a strict superset that lets
  `tests/test_changelog_page_gate.py` run instead of skipping.
- Audited waves 1-3: `RED_VERDICT`, `GREEN_VERDICT` (both from `74-RED-EVIDENCE.md`) and
  `QUA14_FIX_VERDICT` (from `74-QUA14-EVIDENCE.md`) all quoted verbatim and confirmed `MET`.
- Ran `ruff check .`, `black --check .` and `mypy typsphinx/` — all exit 0.
- Ran the full pytest suite twice — plain (`1562 passed, 1 skipped in 131.39s`) and under
  `LC_ALL=C` (`1562 passed, 1 skipped in 128.42s`) — both saved to a `mktemp -d` scratch dir. Both
  report the identical single skip (`tests/test_corpus_gate.py`'s env-gated report, unrelated to
  this phase) and zero skips naming `tests/test_changelog_page_gate.py`.
- Ran `tests/test_preview_version_sync.py` (3 passed), confirmed `base.typ` declares exactly 4
  `@preview` packages, and confirmed none of the three declaration sites changed since `6cc44f22`.
- Fenced the `typsphinx/` diff: exactly `pathfmt.py` and `translator.py` changed since the
  milestone base, with a pathspec control (translator.py's own diff non-empty) and a widened-diff
  control (33 files across `.planning`/`tests`/`typsphinx`, including the new render-gate test
  module). Every translator.py hunk (7) and the one pathfmt.py hunk fall inside their scoped
  regions by new-side start line; `TRANSLATOR_HUNKS_OUTSIDE_SCOPE = 0`.
- Confirmed the standing invariants: `.github/` and `flake.nix` absent from the milestone diff
  (with both paths confirmed tracked as a control), `pyproject.toml`/`uv.lock`/
  `typsphinx/__init__.py` unchanged, and `version = "0.9.2"` at both HEAD and the base.
- Census of `tests/`: every row `A` except one `M` row for `tests/test_translator.py`, which shows
  0 deletions.
- Wrote `COVERAGE.md` with the required one-line declaration and confirmed
  `api-coverage.verify-pre` passes (`API_COVERAGE_PASSED = true`).
- Recorded `SC4_LOCAL_VERDICT = MET`.

## Task Commits

Each task was committed atomically (plain `git commit`, per this plan's `<worktree_provisioning>`
instruction — no GSD commit helper):

1. **Task 1: Tracer — audit waves 1-3, lint trio, both full pytest runs, @preview invariant** -
   `a5288822` (docs)
2. **Task 2: Scope fence, standing invariants, test-edit census, COVERAGE.md, SC4_LOCAL_VERDICT** -
   `fab94120` (docs)

## Files Created/Modified
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-GATES-EVIDENCE.md` -
  head check/provisioning, wave 1-3 audit, lint trio, full pytest (plain + LC_ALL=C), @preview
  invariant, scope fence with controls, standing invariants, test-edit census, API coverage
  declaration, SC4 local verdict
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/COVERAGE.md` -
  the one-line no-external-API-integration declaration for the api-coverage gate

## Decisions Made
- Provisioned with both `dev` and `docs` extras up front (per `<worktree_provisioning>` and
  ROADMAP constraint 11), confirming `CHANGELOG_GATE_SKIPS = 0` rather than discovering the gap
  mid-plan.
- Region-scoped every translator.py/pathfmt.py hunk by new-side start line against grep-derived
  anchor lines, rather than trusting the file-level diff --stat alone, satisfying constraint 7's
  scope fence at hunk granularity.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `SC4_LOCAL_VERDICT = MET` is recorded in `74-GATES-EVIDENCE.md` for 74-07 to gate on before the
  first push and CI dispatch.
- No product file was changed by this plan (confirmed by an empty diff against `BASE_74_06`
  excluding `.planning/` at every commit boundary).
- 74-07 can proceed to the branch census, first push, and CI dispatch.

---
*Phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-GATES-EVIDENCE.md` exists on disk: FOUND
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/COVERAGE.md` exists on disk: FOUND
- Commits `a5288822` and `fab94120` present in `git log --oneline`
- Both tasks' `<automated>` `<verify>` scripts re-run against final HEAD and both exited 0 (`TASK1_VERIFY_PASS`, `TASK2_VERIFY_PASS`)
- `git diff --diff-filter=D --name-only HEAD~2 HEAD` is empty (no deletions); `git status --short` clean
- All plan-level `<verification>` bullets hold: lint/type/full-suite (plain and C-locale) green, `@preview` invariant holds, the typsphinx/ fence lists only the two files region-scoped with both controls, workflows/flake.nix/pyproject.toml/uv.lock/`__init__.py` untouched, no pre-existing test lost a line, and `COVERAGE.md` satisfies the api-coverage gate
