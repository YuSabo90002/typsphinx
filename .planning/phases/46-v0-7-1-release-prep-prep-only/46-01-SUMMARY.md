---
phase: 46-v0-7-1-release-prep-prep-only
plan: 01
subsystem: release-engineering
tags: [git-merge, ci, ruff, changelog, windows-ci, github-actions]

# Dependency graph
requires:
  - phase: 45.2-local-toolchain-repair-tox-uv-to-tox-uv-bare
    provides: a working local tox/uv toolchain and the tox-uv-bare dependency fix
provides:
  - origin/main (PR #131, Issue #130 fix) merged into the milestone branch
  - a platform-independent tests/test_docs_contract_claims_gate.py claim-page comparison
  - a live, green CI run proving both windows-latest lanes pass (D-23 run 1)
  - 46-CI-EVIDENCE.md with verbatim run-1 transcripts and a named run-2 placeholder
affects: [46-02, 46-03, 46-04, 46-05, 46-06]

# Actuals (#2632)
actuals:
  tokens: 3339
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Hand-resolved CHANGELOG.md merge conflicts keep both sides' content under one heading, ordered per the plan's explicit sequencing"
    - "A dispatched workflow_dispatch CI run, polled by headSha match, is this project's standing evidence mechanism for platform behavior unreproducible locally (Windows path separators)"

key-files:
  created:
    - .planning/phases/46-v0-7-1-release-prep-prep-only/46-CI-EVIDENCE.md
  modified:
    - CHANGELOG.md
    - tests/test_docs_contract_claims_gate.py
    - tests/test_toolchain_config_gate.py

key-decisions:
  - "Resolved the single CHANGELOG.md Unreleased-block conflict by hand: origin/main's Issue #130 Fixed bullet first, then the local Planned for Future Releases list, both under one Unreleased heading — no ## [0.7.1] heading created here (D-20, D-24 deferred to plan 46-03)"
  - "Repaired _discovered_claim_pages() with .as_posix() so Windows and POSIX compare on the same forward-slash keys (D-22)"
  - "Fixed three pre-existing ruff B904 violations in tests/test_toolchain_config_gate.py (a Phase 45.2 file, first exercised by this task's own CI dispatch) because the task's own acceptance criteria requires zero job failures in the live run, not merely the two windows-latest lanes"

patterns-established:
  - "When a task's CI dispatch surfaces an unrelated pre-existing failure that blocks the task's own zero-failure acceptance bar, fix it in a separate, clearly-scoped commit and re-dispatch — do not silently absorb it into the task's primary commit"

requirements-completed: [REL-06]

coverage:
  - id: D1
    description: "origin/main (9b2b76b, PR #131 merge) is merged into the milestone branch, with the single CHANGELOG.md conflict resolved by hand preserving both sides"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: "git merge-base --is-ancestor origin/main HEAD"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_docs_contract_claims_gate.py compares forward-slash claim-page keys on every platform via .as_posix()"
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "tests/test_docs_contract_claims_gate.py::TestContractClaimPageEnumerationIsClosed (8 passed locally)"
        status: pass
      - kind: e2e
        ref: "gh run view 31456868265 --json jobs -- Test Python 3.12 on windows-latest, Test Python 3.13 on windows-latest"
        status: pass
    human_judgment: false
  - id: D3
    description: "A live, dispatched CI run on the pushed commit (07b9afd) reports success for all 12 jobs, with both windows-latest lanes flipping from the failure baseline to success"
    requirement: "REL-06"
    verification:
      - kind: e2e
        ref: "gh run view 31456868265 --json conclusion,status -> success/completed"
        status: pass
    human_judgment: false
  - id: D4
    description: "46-CI-EVIDENCE.md records D-23 run 1's verbatim transcripts, baseline comparison, and an honest what-this-does-not-prove statement, plus a named run-2 placeholder"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: ".planning/phases/46-v0-7-1-release-prep-prep-only/46-CI-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "No irreversible action was taken (git tag -l v0.7.1 empty)"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: "git tag -l v0.7.1"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-11
status: complete
---

# Phase 46 Plan 01: Merge origin/main, Windows Claims-Gate Repair, and Live CI Proof Summary

**Merged PR #131 (Issue #130 fix) into the milestone branch, repaired the Windows-only path-separator defect in the contract-claims gate, and proved both fixes live against a dispatched `windows-latest` CI run that flipped from failure to success.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 2
- **Files modified:** 4 (CHANGELOG.md, tests/test_docs_contract_claims_gate.py, tests/test_toolchain_config_gate.py, 46-CI-EVIDENCE.md created)

## Accomplishments
- `origin/main` (`9b2b76b`, PR #131) is merged into the milestone branch via `git merge --no-ff`; the sole conflict (`CHANGELOG.md`) was resolved by hand, keeping both sides under one `## [Unreleased]` heading — origin/main's Issue #130 `### Fixed` bullet first, then the local `### Planned for Future Releases` list.
- `tests/test_docs_contract_claims_gate.py`'s `_discovered_claim_pages()` now normalizes to forward-slash keys via `.as_posix()`, so the comparison against `REVIEWED_CLAIM_PAGES`/`EXCLUDED_CLAIM_PAGES` is platform-independent.
- A dispatched `ci.yml` run on the pushed commit (`07b9afd`) reports `success` for all 12 jobs — including both `Test Python 3.12 on windows-latest` and `Test Python 3.13 on windows-latest`, the two lanes that were the only failures in baseline run `31445582363`.
- `46-CI-EVIDENCE.md` records the full transcript trail (merge, conflict resolution, both pushes/dispatches, both job-conclusion tables, the baseline comparison, an honest "what this run does not prove" statement, and the observation about `scripts/extract_changelog_section.py`'s stale docstring), with a named `_Pending — filled by plan 46-04._` placeholder for D-23 run 2.
- No irreversible action was taken: `git tag -l v0.7.1` is empty.

## Task Commits

Each task was committed atomically:

1. **Task 1: Merge `origin/main`, repair the Windows claim-page keys, and prove the loop on a live CI run** — `c72be91` (merge) + `07b9afd` (fix, deviation)
2. **Task 2: Record D-23 run 1's evidence and open the run-2 placeholder** — `99f4e36` (docs)

_Note: Task 1 required a second commit beyond the plan's original single-commit expectation — see Deviations below._

## Files Created/Modified
- `CHANGELOG.md` — resolved the `## [Unreleased]` merge conflict, preserving both origin/main's Issue #130 bullet and the local Planned-for-Future-Releases list
- `tests/test_docs_contract_claims_gate.py` — `_discovered_claim_pages()` now uses `.as_posix()` for platform-independent key comparison (D-22)
- `tests/test_toolchain_config_gate.py` — added `from e` to three `raise AssertionError(...)` statements inside `except Exception as e:` blocks (ruff B904 fix, deviation)
- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-CI-EVIDENCE.md` — new evidence file for D-23

## Decisions Made
- Kept `origin/main`'s Issue #130 `### Fixed` bullet before the local `### Planned for Future Releases` list in the resolved `CHANGELOG.md`, per the plan's explicit ordering instruction; did not create a `## [0.7.1]` heading here (that is plan 46-03's job).
- Fixed the three pre-existing ruff `B904` violations discovered via the live CI dispatch rather than treating them as out-of-scope, because the task's own action text and acceptance criteria require the dispatched run to show zero job failures ("a regression anywhere else is equally disqualifying at this point"), not merely the two named `windows-latest` lanes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed three pre-existing ruff B904 violations discovered by the live CI dispatch**
- **Found during:** Task 1's live CI run (first dispatch, run `31456466358`)
- **Issue:** `tests/test_toolchain_config_gate.py` (added by Phase 45.2, after the baseline CI run `31445582363` was dispatched) contains three `raise AssertionError(...)` statements inside `except Exception as e:` blocks with no `from e`/`from None` clause. `ruff check .` in the `Lint and Format Check` CI job failed on all three, a job that was `success` on the baseline. `.venv/bin/ruff` cannot run locally on this NixOS worktree (a known, filed environmental defect), so this could only surface via a live CI run — exactly what this task's dispatch is for.
- **Fix:** Added `from e` to all three `raise AssertionError(...)` statements. Test-only change, zero behavior change, no `typsphinx/` file touched (D-03/D-27's prep-only fence intact).
- **Files modified:** `tests/test_toolchain_config_gate.py`
- **Verification:** `uv run black --check tests/test_toolchain_config_gate.py` (unchanged), `uv run pytest tests/test_toolchain_config_gate.py -q` (4 passed), and the second CI dispatch (run `31456868265`) reporting `Lint and Format Check: success` plus all 12 jobs `success`.
- **Committed in:** `07b9afd` (separate commit from the merge, pushed and re-dispatched)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to satisfy the task's own zero-job-failure acceptance bar for its live CI evidence. No scope creep — test-only, unrelated to `typsphinx/`, and the root cause predates this plan (Phase 45.2).

### Premise Correction (not a deviation to code — a plan-assertion mismatch)

The plan's `<verify>` block and one `must_haves.truths` / acceptance-criteria line assert
`test -z "$(git diff origin/main..HEAD --name-only -- typsphinx/)"` (no `typsphinx/` file differs
between `origin/main` and the milestone branch HEAD). This is **not achievable** given the actual
repository state: `origin/main`'s merge-base with this milestone branch is `87f242a` (long before
Phase 43), and every phase since (43 through 45.2) has landed substantial, un-mirrored
`typsphinx/` work on this branch — confirmed live: `git diff origin/main..HEAD --name-only --
typsphinx/` lists `__init__.py`, `builder.py`, `template_engine.py`, `translator.py`, `writer.py`
(850 insertions / 210 deletions). Under `branching_strategy: milestone`, `main` only receives the
full milestone diff at `/gsd-complete-milestone`, not incrementally — so this divergence is
expected and cannot be zero without deleting five phases' worth of shipped work, which would
itself violate the prep-only fence far more severely than the literal check protects against.

The narrower, achievable acceptance criterion in the same task — `git show
HEAD:typsphinx/builder.py | grep -c _track_image` prints `4` — was verified and **passes**,
confirming PR #131's fix landed in `typsphinx/builder.py` unmodified and that the merge itself
(a pure `git merge --no-ff` with zero manual edits to any `typsphinx/` file) introduced no
tampering. T-46-02's actual protective intent — no manual alteration of `typsphinx/` source during
the merge — is fully satisfied; the broad byte-identity assertion against `origin/main` is a false
premise inherited into the plan and is flagged here rather than silently "fixed" by deleting prior
phases' work.

## Issues Encountered
None beyond the deviation and premise correction documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The milestone branch contains `origin/main`; PR #131's fix is live on the branch and proven on CI.
- `tests/test_docs_contract_claims_gate.py` is Windows-safe; the two `windows-latest` CI lanes are
  green.
- `46-CI-EVIDENCE.md` is ready for plan 46-04 to fill its `## D-23 run 2 — the authority run`
  section once the version bump and `## [0.7.1]` CHANGELOG entry land.
- No blockers for plan 46-02 (version bump) or 46-03 (curated CHANGELOG entry).

---
*Phase: 46-v0-7-1-release-prep-prep-only*
*Completed: 2026-08-11*
