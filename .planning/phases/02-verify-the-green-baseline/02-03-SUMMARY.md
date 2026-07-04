---
phase: 02-verify-the-green-baseline
plan: "03"
subsystem: testing
tags: [github-actions, tox, ci, matrix, gap-closure]

# Dependency graph
requires:
  - phase: 02-verify-the-green-baseline
    provides: "PR #104 open against main carrying the Phase 1 pin + Phase 2 fixes; the gsd-verifier's authorized gap (TEST-01, ci.yml tox-env mismatch) with a drafted-but-unmerged fix on gsd/bugfix/github-ci-tox (64cd057)"
provides:
  - "ci.yml test job matrix.include mapping python-version -> dotless tox-env (py39/py310/py311/py312), consumed by `uv run tox -e ${{ matrix.tox-env }}`"
  - "Observed-green re-pushed ci.yml run (28702240846): all 12 matrix jobs + lint + type-check + coverage + build + 2 integration jobs = success"
  - "Observed-green re-pushed docs.yml run (28702240814): build-docs job success including the PDF-copy step, confirming no DOCS-01 regression"
  - "REQUIREMENTS.md TEST-01 re-marked [x] / Complete citing the new green run ID, closing the phase's only failed observable-truth (ROADMAP success criterion 1)"
affects: [phase-03, ship, requirements-audit]

# Tech tracking
tech-stack:
  added: []
  patterns: ["GitHub Actions matrix.include for auxiliary per-lane variables (mapping a display value to a derived config value) instead of string-interpolating the display value directly"]

key-files:
  created: []
  modified:
    - .github/workflows/ci.yml
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Applied the fix via `git cherry-pick 64cd057` from the already-drafted branch gsd/bugfix/github-ci-tox rather than reimplementing by hand, since the plan authorized either approach as long as the resulting content is identical"
  - "Did not treat the CODECOV_TOKEN-absent codecov upload failure as a D-04 finding: it is pre-existing, unrelated to the tox-env fix, silenced by `fail_ci_if_error: false`, and the Code Coverage job's overall conclusion is still success — out of this plan's scope per the SCOPE BOUNDARY rule"

patterns-established:
  - "Gate a REQUIREMENTS.md re-mark on an observed CI run ID captured via `gh run view --json conclusion,jobs`, not on a local test pass — checkbox must never lead ground truth"

requirements-completed: [TEST-01]

coverage:
  - id: D1
    description: "ci.yml test job maps every matrix python-version to its dotless tox env (py39/py310/py311/py312) via matrix.include, and the run step invokes `uv run tox -e ${{ matrix.tox-env }}`"
    requirement: "TEST-01"
    verification:
      - kind: other
        ref: "grep -qF 'uv run tox -e ${{ matrix.tox-env }}' .github/workflows/ci.yml && grep -qF 'tox-env: py39/py310/py311/py312' .github/workflows/ci.yml"
        status: pass
    human_judgment: false
  - id: D2
    description: "The re-pushed ci.yml run on PR #104 (run 28702240846) is observed green across all 12 matrix jobs plus lint/type-check/coverage/build/integration"
    requirement: "TEST-01"
    verification:
      - kind: other
        ref: "gh run view 28702240846 --json conclusion,jobs -q '.conclusion, ([.jobs[].conclusion] | unique)' -> success, [\"success\"]"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs.yml run 28702240814 stays green end-to-end including the PDF-copy step, confirming no DOCS-01 regression from the ci.yml edit"
    verification:
      - kind: other
        ref: "gh run view 28702240814 --json conclusion,jobs -q '.conclusion' -> success; job log shows 'Copy PDF to multi-language build (English version)' step ran `cp docs/_build/pdf/*.pdf docs/_build/multilang/en/` without error"
        status: pass
    human_judgment: false
  - id: D4
    description: "REQUIREMENTS.md TEST-01 re-marked [x] / Complete citing the new green run ID, gated on D2/D3 both being observed green"
    requirement: "TEST-01"
    verification:
      - kind: other
        ref: "grep -qE '^- \\[x\\] \\*\\*TEST-01\\*\\*' .planning/REQUIREMENTS.md && grep -qF '| TEST-01 | Phase 2 | Complete |' .planning/REQUIREMENTS.md && grep -q RESOLVED .planning/REQUIREMENTS.md"
        status: pass
    human_judgment: false

# Metrics
duration: 6min
completed: 2026-07-04
status: complete
---

# Phase 2 Plan 03: TEST-01 tox-env matrix-mapping fix Summary

**Fixed the ci.yml/tox.ini env-name mismatch (dotted `py3.10` vs tox's dotless `py310`) via a `matrix.include` mapping, re-pushed onto PR #104, and observed all 12 test-matrix jobs go green for the first time this phase — closing the phase's only remaining failed observable-truth.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-07-04T09:38:00Z
- **Completed:** 2026-07-04T09:44:04Z
- **Tasks:** 4
- **Files modified:** 2

## Accomplishments
- `ci.yml`'s `test` job now carries a `strategy.matrix.include` list mapping each `python-version` ('3.9'/'3.10'/'3.11'/'3.12') to its dotless `tox-env` (py39/py310/py311/py312), and the `Run tests with tox` step invokes `uv run tox -e ${{ matrix.tox-env }}` instead of interpolating the dotted python-version directly.
- Re-pushed the fix onto PR #104's branch (`gsd/phase-2-verify-green-baseline`), triggering a fresh `pull_request: synchronize` CI + docs run.
- Observed the new CI run (28702240846) conclude `success` with the unique set of all 18 job conclusions being exactly `["success"]` — including the 9 previously-red 3.10/3.11/3.12 x ubuntu/windows/macos lanes that were failing with tox exit 254.
- Observed the new Documentation run (28702240814) conclude `success` end-to-end, including the `cp docs/_build/pdf/*.pdf docs/_build/multilang/en/` PDF-copy step, confirming no DOCS-01 regression.
- Re-marked `REQUIREMENTS.md` TEST-01 `[x]` / Complete (checkbox + traceability row), citing the new green run ID, only after the green run was observed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Apply the tox-env matrix-mapping fix to ci.yml** - `3e3acdf` (fix) — applied via `git cherry-pick 64cd057` from the already-drafted `gsd/bugfix/github-ci-tox` branch (diff verified identical to the plan's specified change before pick).
2. **Task 2: Commit + push the fix and capture new run IDs** - no additional commit (fix was already committed by the Task 1 cherry-pick); pushed `3e3acdf` to `origin/gsd/phase-2-verify-green-baseline`, captured new CI run `28702240846` and new Documentation run `28702240814` (both headSha `3e3acdf`, distinct from the old red run `28700980510`).
3. **Task 3: Observe the new runs green** - no commit (observation only); polled `gh run view` across several calls until both runs reported `status: completed`.
4. **Task 4: Re-mark REQUIREMENTS.md TEST-01 Complete** - `fbf02c9` (docs) — gated on Task 3's fully-green observation.

_No plan-metadata commit yet at time of this writing; this SUMMARY plus STATE/ROADMAP updates will follow in the final metadata commit per the executor's `<final_commit>` step._

## Files Created/Modified
- `.github/workflows/ci.yml` - Added `matrix.include` (python-version -> tox-env) and changed the tox run step to `uv run tox -e ${{ matrix.tox-env }}`.
- `.planning/REQUIREMENTS.md` - TEST-01 checkbox flipped `[ ]` -> `[x]` with a `RESOLVED` note citing run `28702240846`; traceability row `Blocked` -> `Complete`.

## Decisions Made
- Applied the fix via `git cherry-pick 64cd057` (the exact drafted commit on `gsd/bugfix/github-ci-tox`) rather than hand-reimplementing, since the plan authorized either approach and the diff was verified identical to the plan's spec before picking.
- Left the Codecov upload's `Token required - not valid tokenless upload` error unaddressed (see Issues Encountered) — it is pre-existing, unrelated to the tox-env fix, silenced by `fail_ci_if_error: false`, and out of this plan's scope per D-04 / the executor's scope-boundary rule.

## Deviations from Plan

None - plan executed exactly as written. Task 1 used the plan's explicitly-authorized cherry-pick option; no unplanned code changes were made.

## Issues Encountered
- **CODECOV_TOKEN not present / codecov upload fails "tokenless" (pre-existing, out of scope):** The `Code Coverage` job's `Upload coverage to Codecov` step logged `error - Upload queued for processing failed: {"message":"Token required - not valid tokenless upload"}`. This is pre-existing behavior (the repo secret `CODECOV_TOKEN` appears unset/empty — the action's own token-resolution log shows `CC_TOKEN=` empty at every branch), unrelated to this plan's tox-env-mapping change, and does not fail the job because `fail_ci_if_error: false` is already set. Per D-04 this is recorded as a finding, not patched. It does not block TEST-01/TEST-03 (the Code Coverage job's own conclusion is still `success`), but the actual Codecov dashboard/badge will not reflect real coverage until a `CODECOV_TOKEN` repo secret is added — a candidate follow-up item outside this phase's scope.

## User Setup Required

None - no external service configuration required for this plan. (Note: adding a `CODECOV_TOKEN` repo secret, if the maintainer wants live Codecov reporting, is optional follow-up work outside this plan's scope — see Issues Encountered.)

## Next Phase Readiness
- TEST-01 is now ground-truth Complete: the phase's ROADMAP success criterion 1 ("every previously-red CI job green across the full platform/Python matrix") is satisfied by an observed Actions run, not a self-marked assumption.
- PR #104 now carries a fully-green CI + docs run and is ready for phase-close / ship review.
- Remaining open item (non-blocking): `CODECOV_TOKEN` repo secret is absent, so Codecov uploads fail tokenless (job still succeeds due to `fail_ci_if_error: false`). Not required for TEST-01/TEST-03 but worth a maintainer decision in a future phase if live coverage reporting matters.

---
*Phase: 02-verify-the-green-baseline*
*Completed: 2026-07-04*
