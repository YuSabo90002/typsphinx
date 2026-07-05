---
phase: 02-verify-the-green-baseline
plan: 02
subsystem: testing
tags: [github-actions, ci, docs.yml, codecov, tox, black]

# Dependency graph
requires:
  - phase: 02-verify-the-green-baseline
    provides: "Plan 01's committed sync-guard test (tests/test_preview_version_sync.py) and the Phase 1 pinned uv.lock, pushed together as the observed ref"
provides:
  - "Real GitHub Actions observation (PR #104, gsd/phase-2-verify-green-baseline -> main) confirming the Phase 1 pin resolves the kai break: lint, type-check, coverage, build, integration, and the Python-3.9 matrix lane are green, and docs.yml is fully green end-to-end including the PDF-copy step"
  - "A D-04 finding: 9 of 12 test-matrix jobs (Python 3.10/3.11/3.12 x 3 OS) fail for a pre-existing, unrelated reason (tox env-name mismatch) with an unmerged fix already sitting on branch gsd/bugfix/github-ci-tox"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PR-to-main as the low-side-effect trigger that exercises both ci.yml and docs.yml while keeping Pages-deploy/release-upload skipped (D-02)"

key-files:
  created: []
  modified:
    - tests/test_preview_version_sync.py

key-decisions:
  - "Auto-fixed (Rule 1) a black-formatting violation in tests/test_preview_version_sync.py that broke the Lint job, since it is this phase's own deliverable file and the fix is a trivial reformat"
  - "Did NOT auto-fix the tox env-name mismatch (py3.10 vs py310) that fails 9/12 matrix jobs, per this plan's explicit D-04 instruction — surfaced as a finding instead, noting the pre-existing unmerged fix on gsd/bugfix/github-ci-tox"
  - "Did NOT treat the absent CODECOV_TOKEN as a failure, per TEST-03 — the coverage job is green because fail_ci_if_error:false, and the token's absence is recorded as an observation, not a defect"

requirements-completed: [TEST-01, TEST-02, TEST-03, TEST-04, DOCS-01]

coverage:
  - id: D1
    description: "PR #104 (gsd/phase-2-verify-green-baseline -> main) opened; both ci.yml and docs.yml triggered in PR mode with Pages-deploy/release-upload skipped (D-02)"
    requirement: "DOCS-01"
    verification:
      - kind: other
        ref: "gh pr view 104 (state: OPEN, base: main, head: gsd/phase-2-verify-green-baseline)"
        status: pass
      - kind: other
        ref: "gh run view 28700980497 --json jobs (Deploy to GitHub Pages: skipped, Upload PDF to Release: skipped)"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs.yml build-docs job green end-to-end including the PDF-copy step that previously errored on a missing PDF (DOCS-01)"
    requirement: "DOCS-01"
    verification:
      - kind: e2e
        ref: "gh run view 28700980497 (conclusion: success; step 'Build PDF documentation (English only)': success; step 'Copy PDF to multi-language build (English version)': success)"
        status: pass
    human_judgment: false
  - id: D3
    description: "ci.yml lint, type-check, coverage, build, and both integration jobs green (TEST-04); coverage job green with Codecov upload attempted, CODECOV_TOKEN absence recorded (TEST-03)"
    requirement: "TEST-03"
    verification:
      - kind: e2e
        ref: "gh run view 28700980510 --json jobs (Lint and Format Check: success, Type Check: success, Code Coverage: success, Build Package: success, Integration Test - basic: success, Integration Test - advanced: success)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The 3 Python-3.9 matrix jobs (ubuntu/macos/windows) pass, running the full 402-test suite including the Plan 01 sync-guard test (TEST-01, TEST-02)"
    requirement: "TEST-01"
    verification:
      - kind: e2e
        ref: "gh run view 28700980510 --log (Test Python 3.9 on ubuntu-latest: '402 passed, 447 warnings'; macos-latest and windows-latest: success)"
        status: pass
    human_judgment: false
  - id: D5
    description: "9 of 12 matrix jobs (Python 3.10/3.11/3.12 x ubuntu/macos/windows) fail with a tox env-name mismatch unrelated to the Phase 1 pin — surfaced as a D-04 finding, not silently patched; an unmerged fix already exists on branch gsd/bugfix/github-ci-tox (commit 64cd057)"
    verification: []
    human_judgment: true
    rationale: "This is a pre-existing CI-workflow defect (ci.yml passes `tox -e py3.10` but tox.ini defines the dotless env `py310`; introduced in the tox-migration commit 063a2be, long before the Phase 1 pin). It is unrelated to typst/sphinx/docutils version pinning and is explicitly out of this plan's D-04 scope to auto-fix. A human/maintainer must decide whether to merge the existing gsd/bugfix/github-ci-tox fix (or an equivalent) in a follow-up; this plan intentionally leaves it unresolved and documents it."

# Metrics
duration: 8min
completed: 2026-07-04
status: complete
---

# Phase 2 Plan 2: Push, PR, and Observe Real CI/Docs Runs Summary

**Opened PR #104 (gsd/phase-2-verify-green-baseline -> main); confirmed via real GitHub Actions runs that the Phase 1 pin fixes the `kai` typst break (lint, type-check, coverage, build, integration, and the Python-3.9 matrix lane all green; docs.yml fully green including the PDF-copy step), while surfacing a pre-existing, unrelated tox-env-name defect that still fails 9/12 matrix jobs.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-07-04T08:42:54Z
- **Completed:** 2026-07-04T08:50:34Z
- **Tasks:** 3 completed (Task 2 completed via the "surfaced as a finding" path for the unrelated tox defect, per its explicit done-criteria)
- **Files modified:** 1 (tests/test_preview_version_sync.py, black-reformatted)

## Accomplishments
- Pushed `gsd/phase-2-verify-green-baseline` from HEAD (Phase 1 pins + Plan 01's sync-guard test) and opened [PR #104](https://github.com/YuSabo90002/typsphinx/pull/104) against `main`, triggering both a CI run and a Documentation run in PR mode
- Observed `docs.yml` run [28700980497](https://github.com/YuSabo90002/typsphinx/actions/runs/28700980497) complete **fully green end-to-end**: multi-language HTML build, PDF build (no `kai` error, `index.pdf` generated), the PDF-copy step (previously the failure point) succeeded, and Pages-deploy/release-upload both `skipped` as expected in PR mode (D-02, DOCS-01 confirmed)
- Observed `ci.yml` run [28700980510](https://github.com/YuSabo90002/typsphinx/actions/runs/28700980510) (post-fix) green for: Lint and Format Check, Type Check, Code Coverage (upload attempted, `CODECOV_TOKEN` absent and recorded per TEST-03), Build Package, Integration Test - basic, Integration Test - advanced, and all 3 Python-3.9 matrix jobs (ubuntu/macos/windows), each running the full 402-test suite including the Plan 01 sync-guard test
- Found and auto-fixed (Rule 1) a black-formatting bug in `tests/test_preview_version_sync.py` that broke the initial CI run's Lint job
- Found and surfaced (D-04, not patched) a pre-existing tox env-name mismatch that fails the 9 remaining matrix jobs (Python 3.10/3.11/3.12 x 3 OS), unrelated to the Phase 1 pin, with a ready but unmerged fix already on `gsd/bugfix/github-ci-tox`

## Task Commits

1. **Task 1: Push a work branch and open a PR targeting main (D-02)** - no commit (git branch/push/PR operations only; `files_modified: []` per plan)
2. **Task 2: Observe ci.yml green** - `69ffeda` (fix) — in-scope black-formatting auto-fix required to get the Lint job green before the rest of the run could be meaningfully observed
3. **Task 3: Observe docs.yml green end-to-end (DOCS-01)** - no commit (observation-only task; docs.yml was green on the first run, no fix needed)

**Plan metadata:** pending (this docs commit, made after this SUMMARY)

## Files Created/Modified
- `tests/test_preview_version_sync.py` - Reformatted with `black` (no logic change) to satisfy the Lint and Format Check job; this file was added in Plan 01 and had not been run through black before that plan's commit

## Decisions Made
- Auto-fixed the black-formatting violation (Rule 1: bug directly blocking this phase's own deliverable from going green) rather than treating it as a D-04 finding, since it is this phase's own file (added in Plan 01) and the fix was a trivial, verified reformat with no behavior change
- Left the tox env-name mismatch (9/12 matrix jobs) unpatched per this plan's explicit D-04 instruction, documenting it as coverage item D5 and recommending the existing `gsd/bugfix/github-ci-tox` branch (commit `64cd057`) as the candidate fix for a future decision
- Treated the absent `CODECOV_TOKEN` as an observation, not a failure, consistent with TEST-03's explicit `fail_ci_if_error: false` semantics
- Did not act on a secondary, non-blocking observation: `codecov/codecov-action@v5` warns `Unexpected input(s) 'file', valid inputs are [... 'files' ...]` because `ci.yml`'s coverage step still uses the deprecated singular `file:` input key. This is cosmetic (the step still runs and its failure is solely the missing-token rejection) and unrelated to the Phase 1 pin; noted here for awareness but out of this plan's scope to fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed black-formatting violation in the Plan 01 sync-guard test, which broke the Lint job**
- **Found during:** Task 2 (first CI run observation, run `28700878049`)
- **Issue:** `tests/test_preview_version_sync.py` (added in Phase 2 Plan 1) was not black-formatted; the CI Lint and Format Check job's `black --check .` reported "would reformat tests/test_preview_version_sync.py" and exited 1, failing the job.
- **Fix:** Ran `uv run black tests/test_preview_version_sync.py` to reformat (a single multi-line `assert` statement's wrapping changed; no logic change). Verified `uv run black --check .` passes clean across all 50 tracked files afterward.
- **Files modified:** tests/test_preview_version_sync.py
- **Verification:** Re-pushed the branch; the new CI run (`28700980510`) shows `Lint and Format Check: success`.
- **Committed in:** `69ffeda`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary correctness fix confined to this phase's own newly-added test file; no scope creep, no production code touched.

## Issues Encountered

- **9/12 test-matrix jobs fail for a reason unrelated to the Phase 1 pin (D-04 finding, not patched):** `ci.yml`'s test-matrix step runs `uv run tox -e py${{ matrix.python-version }}`, which for `matrix.python-version: '3.10'/'3.11'/'3.12'` produces `tox -e py3.10`/`py3.11`/`py3.12`. `tox.ini`'s `env_list` defines the dotless names `py310`/`py311`/`py312`. tox's generative-environment name matching does not recognize the dotted two-digit-minor form, so it errors with `provided environments not found in configuration file: py3.10 - did you mean py310?` (exit 254). The three `'3.9'` jobs pass only because `py3.9`'s single-digit-minor dotted form happens to be recognized by tox as an implicit environment (falling back to the base `[testenv]` config running whatever Python the prior `uv sync` step already set up), which is a coincidence of tox's naming convention, not intentional design. This bug pre-dates the Phase 1 pin — `git log` shows it was introduced when CI migrated to tox (`063a2be refactor: migrate CI to tox`) — and a fix already exists, unmerged, on local/remote branch `gsd/bugfix/github-ci-tox` (commit `64cd057 fix(ci): correct tox environment names in GitHub Actions matrix`, which adds an explicit `matrix.include` mapping `python-version` -> `tox-env`). Per this plan's explicit D-04 instruction, this was surfaced as a finding rather than patched in this plan. **Recommendation:** a follow-up (Phase 3 or a dedicated fix plan) should merge that branch's fix (or an equivalent) and re-observe the full 12-job matrix.
- **Codecov `file` vs `files` input warning (non-blocking, unrelated):** `codecov/codecov-action@v5`'s log shows `##[warning]Unexpected input(s) 'file', valid inputs are [...'files'...]` because `ci.yml` still passes the deprecated singular `file:` key. The step's actual (harmless, per TEST-03) failure is the separate, expected `Token required - not valid tokenless upload` message from the absent `CODECOV_TOKEN`; the job is green regardless due to `fail_ci_if_error: false`. Noted for awareness, not fixed (cosmetic, pre-existing, out of this plan's scope).
- **Absent `CODECOV_TOKEN` confirmed (expected, TEST-03):** the Codecov upload step logs `Upload queued for processing failed: {"message":"Token required - not valid tokenless upload"}`. This is the expected behavior for a repo secret that has not been configured; the job's overall conclusion remains `success` because of `fail_ci_if_error: false`. No repo secret was added or modified by this plan — the plan's `user_setup` note asked to *confirm presence/absence*, not to configure it.
- **Benign docutils docstring warning in docs.yml (unrelated, non-blocking):** both the HTML and PDF docs-build steps log `translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]`. This is a docutils parse warning inside a docstring, not a build failure — the build completes and the PDF is generated regardless. Unrelated to the Phase 1 pin; not fixed (out of scope, cosmetic).

## User Setup Required
None - `CODECOV_TOKEN`'s absence was confirmed and recorded per the plan's instructions; the plan explicitly treats an absent token as an observation, not a required action.

## Next Phase Readiness
- **D-01 (authoritative definition of done) is substantially confirmed:** the real GitHub Actions runs were observed directly (not a local tox run). `docs.yml` is fully green end-to-end (DOCS-01). `ci.yml` is green for lint, type-check, coverage, build, both integration jobs, and the full Python-3.9 lane across all 3 OS (TEST-01, TEST-02, TEST-04; TEST-03's token-absence behavior confirmed as expected).
- **Open finding for a follow-up:** 9/12 matrix jobs (Python 3.10/3.11/3.12 x 3 OS) remain red due to the pre-existing tox env-name mismatch, unrelated to the Phase 1 pin. A ready fix exists on `gsd/bugfix/github-ci-tox` (commit `64cd057`) and should be triaged/merged in a follow-up phase or plan before this milestone can claim "all 12 matrix jobs green" as fully proven in CI. This does not block Phase 2's core deliverable (confirming the Phase 1 pin resolves the `kai` break), since the failures are a distinct, orthogonal CI-configuration defect, not a `kai`/typst-compilation error.
- PR #104 remains open at https://github.com/YuSabo90002/typsphinx/pull/104 for continued reference; it was not merged as part of this plan (no instruction to merge was given).

---
*Phase: 02-verify-the-green-baseline*
*Completed: 2026-07-04*

## Self-Check: PASSED

- FOUND: tests/test_preview_version_sync.py
- FOUND: .planning/phases/02-verify-the-green-baseline/02-02-SUMMARY.md
- FOUND: 69ffeda (Task 2 auto-fix commit)
- FOUND: 553f4e3 (SUMMARY commit)
- FOUND: PR #104 (https://github.com/YuSabo90002/typsphinx/pull/104)
- FOUND: CI run 28700980510 (https://github.com/YuSabo90002/typsphinx/actions/runs/28700980510)
- FOUND: Docs run 28700980497 (https://github.com/YuSabo90002/typsphinx/actions/runs/28700980497)
