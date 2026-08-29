---
phase: 58-repr-format-decoupling-test-side-only
plan: 03
subsystem: testing
tags: [pytest, ast-static-analysis, repr-decoupling, path-naming, msg-01, ci, git-push]

requires:
  - phase: 58-repr-format-decoupling-test-side-only
    provides: "plan 58-02's whole-tree AST pass-criterion count reaching exactly 7 with zero path-valued sites, the exact enumeration this plan's guard locks"
provides:
  - "tests/test_repr_census_guard.py -- the AST-backed guard that re-derives the seven-site pass-criterion allowlist at run time, self-excluded, non-vacuous, observed RED once before being trusted"
  - "58-REPR-CENSUS.md -- the two-axis classified, written enumeration Phases 59 and 60 check their zero-test-edit claim against"
  - "58-DECOUPLING-EVIDENCE.md's closing sections: the D-09 falsification transcript, the phase gate, SC#4 at phase scope, and SC#5's branch-push evidence"
  - "gsd/v0.9.1-windows-path-correctness on origin, tracking"
affects: [59, 60]

actuals:
  tokens: 8800
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "AST-walk over ast.Assert(...).test (never .msg), self-excluded by resolved-path identity, locked to a recorded allowlist -- the 'derive live, compare to a recorded constant' pattern tests/test_preview_version_sync.py already established, applied to a whole-tree sweep"
    - "guard trust established by deliberate falsification: inject a real pass-criterion site into an unrelated, untouched module, observe the guard go RED attributing the failure to the right assertion, revert, re-prove green -- before the guard is committed as trusted"

key-files:
  created:
    - tests/test_repr_census_guard.py
    - .planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md
  modified:
    - .planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md

key-decisions:
  - "Reworded 58-REPR-CENSUS.md's opening sentence from 'nothing in it is an assertion' to 'nothing here decides a GREEN or RED verdict' -- the literal word 'assertion' made the line begin with a substring the acceptance criteria's 'no line beginning with assert' check would flag as a false positive; the reworded sentence carries the identical meaning."

requirements-completed: [MSG-01]

coverage:
  - id: D1
    description: "tests/test_repr_census_guard.py exists as the AST-backed census guard: a run-time sweep over tests/**/*.py, self-excluded by resolved-path identity, locked to PASS_CRITERION_REPR_ALLOWLIST (7 entries), asserting zero path-valued survivors and sweep non-vacuity, and observed RED once via a real deliberate falsification before being trusted"
    requirement: MSG-01
    verification:
      - kind: unit
        ref: "tests/test_repr_census_guard.py -- 4 tests, all passing (test_pass_criterion_repr_sites_match_recorded_allowlist, test_no_path_valued_pass_criterion_site_remains, test_sweep_is_not_vacuous, test_allowlist_entries_point_at_real_lines)"
        status: pass
      - kind: manual_procedural
        ref: "58-DECOUPLING-EVIDENCE.md ## D-09 section -- baseline 4 passed, injected line 119 of tests/test_preview_version_sync.py, RED as 1 failed/3 passed attributed to the allowlist-equality assertion naming the exact file and line, reverted with both git status --porcelain checks empty, re-proven 4 passed"
        status: pass
    human_judgment: true
    rationale: "The plan's own deliberate-falsification step requires a human-legible transcript proving the RED output is genuine pytest output attributable to the right assertion, not a reconstruction -- the same class of judgment call plans 58-01/58-02's SC#2(c) sections required."
  - id: D2
    description: "58-REPR-CENSUS.md records the whole-tree census (never derived from the two MSG-01 sites), classified on role (pass-criterion vs diagnostic-only) and value type, all nine phase-base sites, the post-phase zero-path-valued state, the third bucket (TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator, explicitly not rewritten), and a non-asserted, methodology-dependent total-occurrence figure"
    requirement: MSG-01
    verification:
      - kind: other
        ref: "grep checks confirming all eight required headings, nine pass-criterion table rows naming every required file, the third-bucket section naming _assert_no_doubled_separator, and zero lines beginning with 'assert'"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#4 is proven at phase scope (git status/diff/log all empty for typsphinx/ against the phase-base SHA), the full suite plus black are green with mypy recorded as a no-change control, and SC#5 is discharged: gsd/v0.9.1-windows-path-correctness is on origin with a tracking upstream, no decoy branch, no tag"
    requirement: MSG-01
    verification:
      - kind: integration
        ref: "uv run pytest -q -- 1437 passed, 5 skipped (all five pre-existing, environment-gated); uv run black --check . -- clean; git diff --stat/--name-only/status --porcelain over typsphinx/ -- all empty against 3b0f2b93f924f28eba94a0e92ea76996e9d743ad"
        status: pass
      - kind: other
        ref: "git push -u origin gsd/v0.9.1-windows-path-correctness; git branch -vv shows [origin/gsd/v0.9.1-windows-path-correctness]; git rev-parse --abbrev-ref '...@{upstream}' prints origin/gsd/v0.9.1-windows-path-correctness; git ls-remote --heads/--tags confirm no decoy branch and no tag"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-28
status: complete
---

# Phase 58 Plan 03: The AST-Backed Census Guard, the Written Census, and the Milestone Branch Push Summary

**A self-excluding, non-vacuous AST sweep over `tests/**/*.py` locks the `repr()`/`!r` pass-criterion count to the recorded seven-site allowlist and was observed RED against a deliberately introduced site in `tests/test_preview_version_sync.py` before being trusted; `58-REPR-CENSUS.md` writes the two-axis classified enumeration down; the full suite and `black` close green with `SC#4` proven at phase scope; and `gsd/v0.9.1-windows-path-correctness` is now on `origin`, tracking, with no decoy branch and no tag.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-28 (this session)
- **Completed:** 2026-08-28
- **Tasks:** 3 completed
- **Files modified:** 3 (2 new source/planning files, 1 evidence file appended three times)

## Accomplishments

- `tests/test_repr_census_guard.py`: the AST-backed guard for D-08/D-09. Sweeps every
  `tests/**/*.py`, walks each `ast.Assert` node's `.test` expression only (never `.msg`, which is
  where the several-hundred diagnostic-only `repr()`/`!r` occurrences live), self-excludes by
  resolved-path identity, and asserts the collected hit set equals `PASS_CRITERION_REPR_ALLOWLIST`
  — a `frozenset` of exactly seven `(relative_posix_path, lineno)` entries, each annotated with its
  D-08 value type. Three additional properties: zero path-valued survivors
  (`REWRITTEN_PATH_VALUED_MODULES`), sweep non-vacuity (`MINIMUM_FILES_SWEPT = 100`), and every
  allowlist entry pointing at a real line in a real file. No numeric total-occurrence constant
  (341 or 352) appears anywhere in the module.
- **Deliberate falsification, run and recorded (D-09).** A baseline `4 passed` was captured, then a
  single throwaway, deliberately TRUE assertion (`assert "codly" in repr(EXPECTED_PACKAGES)`) was
  appended as the last statement of `test_all_four_packages_declared` in
  `tests/test_preview_version_sync.py` (untouched by this phase otherwise) — landing at line 119,
  exactly as predicted before running anything. The guard went RED as `1 failed, 3 passed`,
  attributed specifically to `test_pass_criterion_repr_sites_match_recorded_allowlist`'s "sites
  found but not allowlisted" branch, naming `test_preview_version_sync.py:119` by name. The
  perturbation was reverted via `git checkout`, proven absent by two `git status --porcelain`
  checks (the file itself, and the whole of `tests/`), and the guard re-proven `4 passed`. Full
  transcript in `58-DECOUPLING-EVIDENCE.md` under `## D-09`.
- `58-REPR-CENSUS.md`: the written, two-axis classified census. Records all nine phase-base
  pass-criterion sites (the two MSG-01 rewrote plus the seven that remain), states the post-phase
  path-valued count is zero, records the third bucket
  (`TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator` — path-valued but
  format-asserting by design, must not be rewritten, MSG-02's own gate depends on it), and records
  a freshly measured total-occurrence figure (368) as descriptive and methodology-dependent rather
  than a test target, naming both the CONTEXT.md (341) and RESEARCH.md (352) prior figures.
- **Phase gate closed green.** `uv run pytest -q` → `1437 passed, 5 skipped` (all five skips
  pre-existing and environment-gated: `myst-parser`'s docs-extra-only tests, one
  `TYPSPHINX_CORPUS_REPORT`-gated corpus test — none introduced by this phase). `black --check .`
  clean. `ruff check .` could not execute in this worktree's NixOS venv (the same documented
  dynamic-linker hazard from plans 58-01/58-02); the `nix-shell -p ruff` fallback reported all
  checks passed, and lint authority is recorded as falling to CI. `mypy typsphinx/` recorded as a
  no-change control (`typsphinx/` has zero commits in this phase's range).
- **SC#4 proven at phase scope.** `git status --porcelain typsphinx/`, `git diff --name-only --
  typsphinx/`, `git diff --stat <phase-base-SHA>..HEAD -- typsphinx/`, and `git log --oneline
  <phase-base-SHA>..HEAD -- typsphinx/` are all empty against `3b0f2b93f924f28eba94a0e92ea76996e9d743ad`
  (the SHA plan 58-01 recorded in `## SC#2 (a)`) — no commit in this phase's whole range touches
  `typsphinx/` at all.
- **SC#5 discharged.** `git push -u origin gsd/v0.9.1-windows-path-correctness` succeeded;
  `git branch -vv` carries the `[origin/gsd/v0.9.1-windows-path-correctness]` tracking marker;
  `git rev-parse --abbrev-ref '...@{upstream}'` prints exactly
  `origin/gsd/v0.9.1-windows-path-correctness`; `git ls-remote --heads/--tags` confirm no
  `gsd/v0.9.1-milestone` decoy and no `v0.9.1*` tag, locally or on `origin`. Two honest notes
  recorded in the evidence: the pushed tip is this worktree's view as of this wave's start (this
  plan's own three commits reach `origin` only after the orchestrator merges the worktree back),
  and `.github/workflows/ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`,
  so this push dispatches no CI run (RESEARCH.md Assumption A2, resolved by re-reading SC#5's
  literal wording).

## Task Commits

Each task was committed atomically:

1. **Task 1: The AST-backed census guard — re-derive the pass-criterion set at run time and lock it to the recorded seven-site allowlist** — `4091f04e` (test)
2. **Task 2: Write the two-axis classified census Phases 59 and 60 check their zero-test-edit claim against** — `190edfd6` (docs)
3. **Task 3: Phase gate — full suite, formatting and lint recorded — then push the milestone branch to origin and prove it is tracking** — `64d0993d` (docs)

**Plan metadata:** (this commit, pending)

## Files Created/Modified

- `tests/test_repr_census_guard.py` — new: the AST-backed census guard, 4 tests, self-exclusion, non-vacuity, zero-path-valued, stale-line detection
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md` — new: the two-axis classified census
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` — appended `## D-09` (falsification transcript), `## Phase gate — full suite, formatting, lint`, `## SC#4 — no file under typsphinx/ changed by this phase`, `## SC#5 — milestone branch on origin`

## Decisions Made

- **Reworded `58-REPR-CENSUS.md`'s opening prose** to avoid a line beginning with the literal word
  "assertion" (which the acceptance criterion's "no line beginning with `assert`" check would flag
  as a substring false positive on a prose sentence, not an actual `assert` statement). The
  reworded sentence ("nothing here decides a GREEN or RED verdict") carries the identical meaning
  without tripping the check.

## Deviations from Plan

None — plan executed exactly as written. The census sweep and its guard were never narrowed: no
directory exclusion beyond `__pycache__` and the guard's own file, and no allowlist entry was
added for a newly appeared site (the deliberate falsification's injected site was reverted, never
allowlisted). No total textual occurrence count was written into any assertion. No file under
`typsphinx/` was changed. No `gsd/v0.9.1-milestone` branch was created, and no branch other than
`gsd/v0.9.1-windows-path-correctness` was pushed to `origin`. No tag was created, no pull request
was opened, no release workflow was dispatched. Evidence appended to
`58-DECOUPLING-EVIDENCE.md` was pasted verbatim from live command output, never reconstructed, and
no section written by plans 58-01 or 58-02 was edited, reordered, or removed (confirmed: all eight
prior headings remain, in original order, followed by this plan's four new sections).

## Issues Encountered

None beyond the cosmetic wording adjustment documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The `repr()`/`!r` pass-criterion enumeration is locked by a run-time AST guard
  (`tests/test_repr_census_guard.py`) and written down in `58-REPR-CENSUS.md` — Phases 59 and 60
  now have a concrete, re-derivable enumeration to check their zero-test-edit claim against, not a
  belief. Per milestone constraint 9, a plan in either phase finding the guard RED after touching a
  test file must re-derive the census, not append to the allowlist.
- The third bucket (`TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator`) is
  classified and flagged in writing: Phase 60 (MSG-02) must not rewrite or re-litigate it.
- `typsphinx/` remains byte-identical to the phase base across the whole phase — proven at phase
  scope, not merely per task — so Phase 59's product-code changes start from a genuinely
  unperturbed tree.
- `gsd/v0.9.1-windows-path-correctness` is on `origin` and tracking (milestone invariant #5
  discharged from the first phase, not deferred to the release PR), with the two honest notes about
  the pushed tip's lag and the absent CI dispatch recorded for any future reader.
- MSG-01 is complete: both call sites (`tests/test_out02_escape_target_gate.py`,
  `tests/test_builder.py`) assert meaning rather than `repr()`'s output format, each proven via a
  real recorded falsification, and the whole-tree census confirms zero path-valued pass-criterion
  sites remain anywhere in `tests/`.

## Self-Check: PASSED

- `tests/test_repr_census_guard.py` exists: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md` exists: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## D-09 — the census guard observed RED (deliberate falsification)`: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## Phase gate — full suite, formatting, lint`: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## SC#4 — no file under typsphinx/ changed by this phase`: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## SC#5 — milestone branch on origin`: FOUND
- Commit `4091f04e` found in `git log --oneline --all`: FOUND
- Commit `190edfd6` found in `git log --oneline --all`: FOUND
- Commit `64d0993d` found in `git log --oneline --all`: FOUND
- All plan-level `<verification>` commands re-run and passing:
  - `uv run pytest -q` → `1437 passed, 5 skipped`
  - `uv run pytest tests/test_repr_census_guard.py -q` → `4 passed`, and the guard was observed RED once against a deliberately introduced site (see `## D-09`)
  - Whole-tree AST pass-criterion count, guard's own file excluded → `7`
  - `uv run black --check .` → exit 0; `uv run ruff check .` exec failure recorded verbatim with the `nix-shell -p ruff` fallback (all clean), lint authority stated to fall to CI
  - `git diff --stat 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/` and `git log --oneline 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/` → both empty
  - `git rev-parse --abbrev-ref 'gsd/v0.9.1-windows-path-correctness@{upstream}'` → `origin/gsd/v0.9.1-windows-path-correctness`; `git ls-remote --heads origin 'gsd/v0.9.1-milestone'` → empty; `git ls-remote --tags origin 'v0.9.1*'` → empty
  - `58-REPR-CENSUS.md` and `58-DECOUPLING-EVIDENCE.md` both exist; no `58-VERIFICATION.md` in the phase directory: confirmed
- All task-level `<acceptance_criteria>` re-verified: PASS
- `git status --porcelain typsphinx/` empty at final check: PASS

---
*Phase: 58-repr-format-decoupling-test-side-only*
*Completed: 2026-08-28*
