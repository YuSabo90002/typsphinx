---
phase: 04-refresh-dev-tooling
plan: 04
subsystem: ci
tags: [ci, verification, pr, push-observe, github-actions, branch-protection]

# Dependency graph
requires:
  - phase: 04-01
    provides: dev-tool floor+ceiling constraints (pyproject.toml [dev] + tox.ini) + regenerated uv.lock
  - phase: 04-02
    provides: upload-artifact@v7 / download-artifact@v8 node24 bumps across ci.yml/docs.yml/release.yml
  - phase: 04-03
    provides: Python 3.9->3.10 README + ruff-comment leftover cleanup
provides:
  - "Observed-green CI phase gate for the Phase 2-4 integration branch"
  - "Open PR #105 targeting main carrying the four Phase-4 per-surface commits (plus Phase 2/3 history)"
  - "Recorded gh run URLs + success conclusions for ci.yml (18 jobs) and docs.yml on the PR head"
  - "main branch-protection required-status-check set repaired (stale 3.9 check removed, 3.13 added)"
affects: [phase-05-durability-guardrails, milestone-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Push -> observe = done (D-05): observed CI matrix, not local single-Python tox, is the phase gate"
    - "Blocking human-verify gate (not auto-approvable) before marking a config-refresh phase done"
    - "Branch-protection required-status-check hygiene must track CI-matrix job-name changes"

key-files:
  created:
    - .planning/phases/04-refresh-dev-tooling/04-04-SUMMARY.md
  modified: []

key-decisions:
  - "Opened a NEW PR (#105) to main via gh pr create rather than reopening closed PR #104 (owner decision) — #105 titled to reflect the full Phases 2-4 green-baseline integration"
  - "Repaired main branch protection: removed the stale 'Test Python 3.9 on ubuntu-latest' required status check (Phase-3 leftover) and added 'Test Python 3.13 on ubuntu-latest' — this stale check was the root cause of PR #105 being un-mergeable despite all 18 jobs green"
  - "Left dependabot #96/#97 untouched (owner closes them after #105 merges); did not merge PR #105 (separate owner action)"

patterns-established:
  - "Pattern 1: push -> observe = done phase gate reused verbatim from Phase 2/3 (D-05)"
  - "Pattern 2: required-status-check set on protected branches must be reconciled whenever the CI matrix drops/adds a job (post-Phase-3 3.9->3.13 shift)"

requirements-completed: [TOOL-01, TOOL-02]

coverage:
  - id: D1
    description: "An open PR targeting main carries the four Phase-4 per-surface commits (pyproject+uv.lock; tox.ini; README+ruff-comment; workflow artifact bumps)"
    requirement: "TOOL-01"
    verification:
      - kind: integration
        ref: "gh pr view 105 --json baseRefName -q '.baseRefName' == main; git log --oneline main..HEAD shows the four surfaces"
        status: pass
    human_judgment: false
  - id: D2
    description: "ci.yml observed green on the PR head across the full 3.10-3.13 x 3-OS matrix plus lint/type-check/coverage/build/integration"
    requirement: "TOOL-01"
    verification:
      - kind: e2e
        ref: "gh run view 28711976093 --json jobs -q '[.jobs[].conclusion]|unique' == [\"success\"] (18 jobs) — https://github.com/YuSabo90002/typsphinx/actions/runs/28711976093"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs.yml observed green on the PR head end-to-end (including the PDF-copy/build step)"
    requirement: "TOOL-02"
    verification:
      - kind: e2e
        ref: "gh run view 28711976097 --json jobs -q '[.jobs[].conclusion]|unique' == [\"success\"] — https://github.com/YuSabo90002/typsphinx/actions/runs/28711976097"
        status: pass
    human_judgment: false
  - id: D4
    description: "Human-verify phase gate: developer reviewed the observed-green CI, the Node-20 straggler finding, and the dependabot overlap, then approved"
    requirement: "TOOL-02"
    verification:
      - kind: manual_procedural
        ref: "Blocking human-verify checkpoint (Task 3) — developer responded 'approved'"
        status: pass
    human_judgment: true
    rationale: "Phase-gate sign-off requires a human to open the actual run URLs and confirm no regression; per T-04-06 the checkpoint is deliberately not auto-approvable"

# Metrics
duration: 40min
completed: 2026-07-05
status: complete
---

# Phase 4 Plan 04: Push -> Observe Phase Gate Summary

**Phases 2-4 integration branch pushed to PR #105 (base=main) with ci.yml (18 jobs, full 3.10-3.13 x 3-OS matrix + lint/type/coverage/build/integration) and docs.yml both observed green on head d99748d; developer approved the blocking human-verify gate after a stale main branch-protection check was repaired.**

## Performance

- **Duration:** ~40 min (incl. blocking human-verify wait)
- **Tasks:** 3 (Task 1 + Task 2 autonomous; Task 3 blocking human-verify — approved)
- **Files modified:** 0 working-tree files (git/PR/CI observation gate + one repo-settings change)

## Accomplishments
- Pushed the Phase-4 commits (04-01/02/03) to `origin/gsd/phase-2-verify-green-baseline` and opened **PR #105** targeting `main` (https://github.com/YuSabo90002/typsphinx/pull/105), head `d99748d`.
- Observed **ci.yml** run [28711976093](https://github.com/YuSabo90002/typsphinx/actions/runs/28711976093) green — conclusion `success`, `[.jobs[].conclusion]|unique == ["success"]`, 18 jobs covering the full Python 3.10/3.11/3.12/3.13 x {ubuntu, macos, windows}-latest matrix (12 combos) plus Lint and Format Check, Type Check, Code Coverage, Build Package, and Integration Test (basic + advanced).
- Observed **docs.yml** run [28711976097](https://github.com/YuSabo90002/typsphinx/actions/runs/28711976097) green — conclusion `success`, `build-docs` job with the `sphinx-build -b typstpdf` PDF-build step confirmed executed end-to-end.
- Developer **approved** the blocking human-verify phase gate after reviewing the PR, both run URLs, the Node-20 straggler finding, and the dependabot overlap.

## Task Commits

This plan makes **no working-tree file edits** — it is the observation/verification gate. The four Phase-4 per-surface commits it verifies were produced by plans 04-01/02/03 and are already on the branch:

1. `848d964` feat(04-01): bump dev-tool floors to floor+ceiling bounds, regenerate uv.lock (pyproject.toml + uv.lock)
2. `226500e` feat(04-01): mirror dev-tool bounds into tox.ini, fix tox-uv requires parsing (tox.ini)
3. `6ce9889` + `62b01e7` docs(04-03): README Python 3.10 + ruff UP035/UP006 comment (README + ruff-comment surface)
4. `0527965` feat(04-02): bump artifact actions to node24 across workflows (ci.yml/docs.yml/release.yml)

**Plan metadata:** this SUMMARY + STATE/ROADMAP/REQUIREMENTS updates (docs commit).

## Files Created/Modified
- `.planning/phases/04-refresh-dev-tooling/04-04-SUMMARY.md` — this summary (created)
- No source/config files modified in this plan.

## Decisions Made
- **New PR, not reopen:** Opened PR #105 to `main` via `gh pr create` rather than reopening the closed PR #104 (owner decision). #104 stays closed. #105 is titled/bodied to reflect the full Phases 2-4 green-baseline integration (green baseline + Python floor 3.10-3.13 + dev-tooling refresh).
- **Branch-protection repair (see Deviations):** Repaired `main`'s required-status-check set so a Phase-3-era stale check no longer blocks merge.
- **Do not merge:** PR #105 left un-merged — merge is a separate owner action.

## Deviations from Plan

### Repo-settings fix (not a git commit — recorded here + in STATE.md for traceability)

**1. [Rule 3 - Blocking] Stale required status check on `main` branch protection**
- **Found during:** Task 3 (checkpoint) — developer attempted to confirm mergeability of PR #105.
- **Issue:** `main` branch protection required the status check **`Test Python 3.9 on ubuntu-latest`**, left over from before Phase 3 dropped Python 3.9 from the CI matrix. That job no longer runs, so GitHub reported it as a permanent "Expected — Waiting for status to be reported" pending check, making PR #105 **un-mergeable despite all 18 jobs being green**. This was the root cause of the initial PR block — not a CI regression.
- **Fix:** Orchestrator ran `gh api PATCH repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks` — removed `Test Python 3.9 on ubuntu-latest` and added `Test Python 3.13 on ubuntu-latest`. Required set is now ubuntu 3.10/3.11/3.12/3.13 + Lint / Type / Coverage / Build.
- **Verification:** PR #105 became `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, zero non-success checks.
- **Nature:** A repository-settings change, not a tracked git commit — documented here and in STATE.md so it is traceable. Recommend a Phase-5 durability guardrail to keep the required-check set in sync with the CI matrix.

---

**Total deviations:** 1 (1 blocking repo-settings fix, handled by the orchestrator).
**Impact on plan:** No scope creep and no CI regression — the tooling refresh itself was green on first observation; the only blocker was a stale branch-protection setting unrelated to any Phase-4 bump.

## Issues Encountered
- Benign non-blocking CI annotations on ci.yml (shared `setup-uv` cache-key reservation races; "no `.pytest_cache` to upload" on non-coverage jobs). These are warnings, not failures — overall run conclusion `success`.

## Tracked / Deferred Items (carried forward)
- **Node-20 straggler:** `softprops/action-gh-release@v2` (used in `docs.yml:67`, `release.yml:177/212`) still declares `runs.using: node20`, ahead of GitHub's 2026-09-16 hosted-runner Node-20 removal. Recorded (not silently closed) as a tracked/deferred TOOL-02 item; **Phase 5 (durability-guardrails) candidate**. Upstream `@v3` exists and is `node24`.
- **Dependabot overlap:** Open PRs #96 (`upload-artifact` 5->7) and #97 (`download-artifact` 6->8) duplicate plan 04-02's manual bumps. Owner will **close them after PR #105 merges** — left untouched per owner decision.
- **release.yml download-artifact@v8** is not exercised by PR #105 (release.yml fires only on a tag push) — expected, low risk (Assumption A1).

## User Setup Required
None - no external service configuration required. (One repo-settings change to `main` branch protection was performed by the orchestrator; see Deviations.)

## Next Phase Readiness
- Phase 4 verification is complete: TOOL-01 and TOOL-02 satisfied, success-criterion 3 ("CI remains green after the tooling refresh, no regression") proven by the observed green matrix.
- **PR #105 is `MERGEABLE`/`CLEAN` but intentionally NOT merged** — the owner will merge it as a separate action, then close dependabot #96/#97.
- Phase 5 (durability-guardrails) inherits two tracked items: the `softprops/action-gh-release` Node-20 bump and the branch-protection-required-check-vs-matrix drift guardrail surfaced by this plan's deviation.

## Self-Check: PASSED

- SUMMARY file exists on disk.
- ci.yml run URL (28711976093), docs.yml run URL (28711976097), PR #105 URL, and head SHA d99748d all present in the SUMMARY.

---
*Phase: 04-refresh-dev-tooling*
*Completed: 2026-07-05*
