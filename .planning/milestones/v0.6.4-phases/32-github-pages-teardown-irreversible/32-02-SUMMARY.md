---
phase: 32-github-pages-teardown-irreversible
plan: 02
subsystem: infra
tags: [github-actions, ci, docs-yml, guard-test, integrations-md, teardown]

# Dependency graph
requires:
  - phase: 32-github-pages-teardown-irreversible (Plan 01)
    provides: "GATE VERDICT: GREEN — fresh in-phase proof RTD serves en/ja HTML+PDF, unlocking Plans 02/03 per D-03"
provides:
  - "`.github/workflows/docs.yml` with the GitHub Pages deploy step and its two now-unused permissions removed, the Upload PDF to Release step proven byte-identical to the milestone merge-base"
  - "Two hermetic guard tests (`test_docs_workflow_has_no_github_pages_deploy`, `test_docs_workflow_still_uploads_pdf_to_release`) that make the removal permanent, proven non-vacuous by a recorded red run against the merge-base workflow"
  - "`.planning/codebase/INTEGRATIONS.md` describing the reduced workflow with no stale Phase-32 scheduling language"
  - "Four fresh milestone-invariant greps (no typsphinx/ change, single surviving github.io hit in CHANGELOG.md, CHANGELOG.md untouched, release.yml untouched) recorded in 32-EVIDENCE.md"
affects: [32-03-branch-deletion-and-pages-disable]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Targeted text Edit on docs.yml (no YAML parse-and-dump round trip) to preserve hand-authored formatting and isolate the diff to exactly the permissions block and the removed step"
    - "Raw-text substring assertions in tests/test_readthedocs_config.py (same idiom as the existing test_build_python_matches_docs_workflow), including a positive retention assertion (contents: write present), not only absence assertions"
    - "Recorded red negative-control run (Phase 31 D-09 precedent): swap in the merge-base file via a trap-protected script, run the guard expecting FAIL, restore, prove restoration with git diff --exit-code"

key-files:
  created: []
  modified:
    - .github/workflows/docs.yml
    - tests/test_readthedocs_config.py
    - .planning/codebase/INTEGRATIONS.md
    - .planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md

key-decisions:
  - "D-04 same-day re-confirmation: today (2026-07-27) matches Plan 01's gate-gathered date, so the full gate was not re-run; only the four URL statuses were re-checked (all 200) before editing docs.yml"
  - "SC#3's byte-equality proof is mechanical (sed-extracted block diff, empty + exit 0), not a visual read of the Pitfall-3 scoped diff — both are recorded in 32-EVIDENCE.md"

patterns-established: []

requirements-completed: [CI-04]

coverage:
  - id: D1
    description: "docs.yml no longer contains the peaceiris/actions-gh-pages deploy step or the pages: write / id-token: write permissions; contents: write, both tox build steps, both artifact uploads, and the Release step are all retained"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "grep -c 'peaceiris'/'pages: write'/'id-token: write' docs.yml == 0; grep -c 'contents: write'/'Upload PDF to Release'/'softprops/action-gh-release@v3'/'uv run tox -e docs-pdf'/'uv run tox -e docs-html' == 1; grep -c 'actions/upload-artifact@v7' == 2"
        status: pass
    human_judgment: false
  - id: D2
    description: "The Upload PDF to Release step is byte-identical to its form at the milestone merge-base (771ec56)"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "diff of sed-extracted step block (base vs. working tree) — empty output, exit 0, recorded verbatim in 32-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two D-06 guard tests exist, pass against the current docs.yml, and are proven non-vacuous by a recorded red run against the merge-base workflow"
    requirement: "CI-04"
    verification:
      - kind: unit
        ref: "tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy"
        status: pass
      - kind: unit
        ref: "tests/test_readthedocs_config.py::test_docs_workflow_still_uploads_pdf_to_release"
        status: pass
      - kind: other
        ref: "Recorded red run: test_docs_workflow_has_no_github_pages_deploy FAILED (exit 1) against merge-base docs.yml, then working tree restored (git diff --exit-code exits 0) — 32-EVIDENCE.md '## D-06 guard tests — recorded red negative control'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full test suite passes after the edit (workflow-shape assertions in test_build_python_matches_docs_workflow and test_readthedocs_yaml_pdf_override still hold)"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "uv run pytest (full suite) -- 647 passed, 1 skipped, 0 failed"
        status: pass
    human_judgment: false
  - id: D5
    description: "INTEGRATIONS.md no longer describes docs.yml as deploying to GitHub Pages, no longer lists peaceiris/actions-gh-pages@v4, and carries no stale 'Phase 32' scheduling language"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "grep -c 'peaceiris'/'deploys HTML to GitHub Pages'/'scheduled for removal in Phase 32'/'Phase 32' INTEGRATIONS.md == 0; grep -c 'softprops/action-gh-release' >= 1"
        status: pass
    human_judgment: false
  - id: D6
    description: "Milestone invariant #3 (no typsphinx/ change) and #4 (fresh repo-wide grep) hold, freshly measured at this plan's execution time"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "git diff --name-only <merge-base>..HEAD -- typsphinx/ CHANGELOG.md .github/workflows/release.yml -- all empty; repo-wide github.io grep excluding .planning/ shows exactly one hit (CHANGELOG.md:393) -- all recorded in 32-EVIDENCE.md '## Milestone invariants'"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-07-27
status: complete
---

# Phase 32 Plan 02: docs.yml GitHub Pages Deploy Removal Summary

**Removed the `peaceiris/actions-gh-pages@v4` deploy step and the two now-unused `pages: write` / `id-token: write` permissions from `.github/workflows/docs.yml`, proved the retained `Upload PDF to Release` step byte-identical to the milestone merge-base, and installed two guard tests proven non-vacuous by a recorded red negative-control run.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-27T14:15:00Z (approx.)
- **Completed:** 2026-07-27T14:24:08Z
- **Tasks:** 3
- **Files modified:** 3 repo files (`docs.yml`, `test_readthedocs_config.py`, `INTEGRATIONS.md`) + `32-EVIDENCE.md` (append-only, incremental across all 3 task commits)

## Accomplishments
- Re-confirmed D-04's same-day gate validity (Plan 01's `GATE VERDICT: GREEN` was gathered 2026-07-27, matching today), then re-checked all four RTD URLs (all `200`) before touching `docs.yml`.
- Removed the `Deploy to GitHub Pages` step (`peaceiris/actions-gh-pages@v4` with its `github_token`/`publish_dir`/`cname` inputs) and the `pages: write` / `id-token: write` permission keys, keeping `contents: write` for the tag-time Release attachment.
- Proved the `Upload PDF to Release` step byte-identical to the milestone merge-base (`771ec56fa3e9a863ac0bca865476bdc423fbb3e7`) via a mechanical `sed`-extraction diff — empty output, exit 0 — not by visual inspection of the Pitfall-3 scoped diff alone.
- Added `test_docs_workflow_has_no_github_pages_deploy` (asserts `peaceiris`/`pages: write`/`id-token: write` absent AND `contents: write` present — the positive retention guard) and `test_docs_workflow_still_uploads_pdf_to_release` to `tests/test_readthedocs_config.py`, reusing the existing raw-text idiom with zero new imports.
- Recorded a red negative-control run: swapped in the merge-base `docs.yml` via a `trap`-protected script, `test_docs_workflow_has_no_github_pages_deploy` FAILED (exit 1) as expected, then restored the working tree and confirmed the restore left no residue (`git diff --exit-code` exit 0).
- Full test suite: **647 passed, 1 skipped, 0 failed** (645-baseline + 2 new guard tests, no environmental-class failures — the per-worktree `uv sync` + `.venv/bin/uv` symlink fix applied cleanly).
- Updated `.planning/codebase/INTEGRATIONS.md`: the `docs.yml` bullet now describes what the workflow actually does (HTML+PDF build, artifact upload, tag-time Release attachment) with an explicit note that publishing is RTD's own build, not this workflow's; the `peaceiris/actions-gh-pages@v4` third-party action entry was deleted outright (no tombstone).
- Recorded four fresh milestone-invariant greps: (a) no `typsphinx/` diff since the merge-base, (b) exactly one `github.io` hit repo-wide outside `.planning/` (the historical `CHANGELOG.md:393` mention), (c) `CHANGELOG.md` untouched, (d) `.github/workflows/release.yml` untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-confirm the gate, remove the Pages deploy step and the two unused permissions, and prove the Release step is byte-unchanged** - `26b8053` (feat)
2. **Task 2: Add the D-06 regression guard tests and prove them non-vacuous with a recorded red run** - `a71674e` (test)
3. **Task 3: Update INTEGRATIONS.md for the reduced workflow and record the milestone-invariant greps** - `0e32109` (docs)

_Plan metadata commit deferred to worktree-mode convention — this SUMMARY.md's own commit stands in for it since STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge._

## Files Created/Modified
- `.github/workflows/docs.yml` - GitHub Pages deploy step and unused permissions removed; Release step byte-unchanged
- `tests/test_readthedocs_config.py` - two new D-06 guard test functions appended after `test_build_python_matches_docs_workflow`
- `.planning/codebase/INTEGRATIONS.md` - `docs.yml` bullet and third-party actions list updated to the reduced workflow
- `.planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md` - appended D-04 re-confirmation, SC#3 byte-unchanged proof, D-06 red negative control, and milestone-invariant grep sections
- `.planning/phases/32-github-pages-teardown-irreversible/32-02-SUMMARY.md` - this file

## Decisions Made
- Same-day D-04 re-confirmation was sufficient (today matches Plan 01's gate date); the full five-check gate from Plan 01 was not re-run, only the four URL statuses.
- SC#3's byte-equality proof used a `sed`-extraction + `diff` pair (not a visual read of the `git diff` hunk) as the authoritative mechanical proof, per the plan's explicit requirement that the byte-unchanged claim not rest on inspection alone.
- The negative-control script used a shell `trap` to guarantee the working-tree restore runs even on an aborted pytest invocation, following the Phase 31 D-09 precedent for recorded red-run evidence.

## Deviations from Plan

None - plan executed exactly as written. All acceptance criteria for all three tasks passed on the first attempt; no auto-fixes were needed.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

Plan 03 (remote `gh-pages` branch deletion + owner-manual Settings → Pages disable + SC#3 CI-run observation via the milestone draft PR) may now proceed. This plan made zero changes outside `.github/workflows/docs.yml`, `tests/test_readthedocs_config.py`, `.planning/codebase/INTEGRATIONS.md`, and `32-EVIDENCE.md` — `typsphinx/`, `CHANGELOG.md`, and `.github/workflows/release.yml` remain untouched across the whole milestone diff, freshly confirmed.

No blockers. The reduced `docs.yml` is ready to be exercised by the milestone draft PR #124's next push (Plan 03's SC#3 observation).

---
*Phase: 32-github-pages-teardown-irreversible*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: `.planning/phases/32-github-pages-teardown-irreversible/32-02-SUMMARY.md`
- FOUND: `.github/workflows/docs.yml`
- FOUND commit `26b8053` (Task 1)
- FOUND commit `a71674e` (Task 2)
- FOUND commit `0e32109` (Task 3)
- FOUND commit `cf967b8` (SUMMARY.md)
