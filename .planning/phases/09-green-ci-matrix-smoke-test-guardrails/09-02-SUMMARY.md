---
phase: 09-green-ci-matrix-smoke-test-guardrails
plan: 02
subsystem: infra
tags: [ci, github-actions, branch-protection, guardrails, release-pr, observation]

# Dependency graph
requires:
  - phase: 09-01
    provides: "tests/test_preview_smoke_gate.py (CI-02) riding the existing tox -e py312/py313 -> pytest tests/ matrix, now proven to execute inside real GitHub Actions runs"
provides:
  - "CI-03 verified as a documented no-op — pyproject.toml ceilings (sphinx>=9.1,<10 / docutils>=0.21,<0.23 / typst>=0.15.0,<0.16) are the single source of truth; drift.yml and dependabot.yml carry no conflicting hardcoded ceilings"
  - "main branch-protection required_status_checks.contexts reconciled — stale, un-producible 'Test Python 3.10/3.11 on ubuntu-latest' contexts removed, replaced with the current 3.12/3.13 ubuntu legs; all other protection settings preserved"
  - "Open, all-green observation PR release/v0.5.0 -> main (#112) — every job (12 ci.yml + 1 docs.yml build-docs) observed green; left UNMERGED for Phase 10"
affects: [10-release-pypi]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Branch-protection reconciliation via the narrowest API surface: PATCH .../protection/required_status_checks (contexts + strict only), never the full protection PUT, to avoid touching unrelated settings (enforce_admins, required_conversation_resolution, etc.)"
    - "D-02-safe pre-flight: gh workflow run ci.yml --ref <branch> against the existing workflow_dispatch trigger, watched to completion, BEFORE opening the real observation PR — surfaces cross-OS breakage in a disposable run first"

key-files:
  created: []
  modified: []

key-decisions:
  - "Branch-protection required-checks policy (delegated to executor per orchestrator authorization): required contexts = Lint and Format Check, Type Check, Code Coverage, Build Package, Test Python 3.12 on ubuntu-latest, Test Python 3.13 on ubuntu-latest. Windows/macOS legs and docs.yml build-docs deliberately left non-required (still run and observable on the PR) to avoid merge-blocking on cross-OS runner flakiness, while still gating on cross-OS execution having occurred in the pre-flight."
  - "release/v0.5.0 had never been pushed to origin (git ls-remote returned empty) — pushed it (git push -u origin release/v0.5.0) as a Rule 3 blocking-issue fix; this is a prerequisite for both the workflow_dispatch pre-flight and the PR, not a scope change."
  - "Did not touch pre-existing red Dependabot PR #108 (docutils 0.23 bump against the old pre-Phase-6 ceiling) — confirmed still open/red, informational only per RESEARCH.md Pitfall 5; superseded once v0.5.0 merges in Phase 10."
  - "PR #112 left OPEN and UNMERGED per D-03 — Phase 10 owns adding the __version__ bump and merging."

patterns-established:
  - "Repo-setting reconciliation (branch protection) is tracked in SUMMARY.md, not as a git commit — GitHub API state, not a git-tracked file, per D-02's scope boundary."

requirements-completed: [CI-01, CI-03]

coverage:
  - id: D1
    description: "CI-03 verified as a documented no-op: pyproject.toml ceilings (sphinx>=9.1,<10, docutils>=0.21,<0.23, typst>=0.15.0,<0.16) already correct; drift.yml has no hardcoded ceiling; dependabot.yml sphinx-typst-stack group is pattern-only"
    requirement: "CI-03"
    verification:
      - kind: other
        ref: "grep -E 'sphinx>=9.1,<10|docutils>=0.21,<0.23|typst>=0.15.0,<0.16' pyproject.toml && ! grep -Eq 'sphinx<|typst<|docutils<' .github/workflows/drift.yml && echo CI-03-VERIFIED-NOOP"
        status: pass
    human_judgment: false
  - id: D2
    description: "main branch-protection required_status_checks.contexts reconciled — stale 3.10/3.11 ubuntu contexts removed, replaced with current job names (Lint and Format Check, Type Check, Code Coverage, Build Package, Test Python 3.12/3.13 on ubuntu-latest); all other protection settings unchanged"
    requirement: "CI-01"
    verification:
      - kind: other
        ref: "gh api repos/YuSabo90002/typsphinx/branches/main/protection (GET after PATCH) — contexts list confirmed free of non-existent job names; enforce_admins/required_conversation_resolution/allow_force_pushes/allow_deletions unchanged from BEFORE state"
        status: pass
    human_judgment: false
  - id: D3
    description: "PR release/v0.5.0 -> main (#112) opened; every job observed green (12 ci.yml jobs + docs.yml build-docs); tests/test_preview_smoke_gate.py confirmed running and passing inside all 6 matrix legs plus Code Coverage; PR left open/unmerged; mergeStateStatus CLEAN confirms branch-protection reconciliation took effect"
    requirement: "CI-01"
    verification:
      - kind: other
        ref: "gh pr checks 112 --watch (13/13 jobs pass); gh run view <run-id> --log grep test_preview_smoke_gate (PASSED in all 6 matrix legs + coverage); gh pr view 112 --json mergeable,mergeStateStatus,state (MERGEABLE/CLEAN/OPEN)"
        status: pass
    human_judgment: false

duration: 39min
completed: 2026-07-11
status: complete
---

# Phase 9 Plan 2: CI-01 Observation + CI-03 Guardrail Verification + Branch-Protection Reconciliation Summary

**Reconciled main's stale branch-protection required-checks (removed non-producible "Test Python 3.10/3.11 on ubuntu-latest" contexts), verified CI-03's dependency-ceiling guardrails as an already-correct no-op, and opened PR #112 (release/v0.5.0 -> main) with all 13 CI jobs — including the CI-02 smoke gate — observed green for the first time ever on Sphinx 9.1/docutils 0.22/typst 0.15 across all 3 OS runners; left unmerged for Phase 10.**

## Performance

- **Duration:** 39 min (largely GitHub Actions wait time: one full pre-flight matrix run + one full PR-triggered run)
- **Started:** 2026-07-11T07:15:00Z (approx, continuing from 09-01 session handoff)
- **Completed:** 2026-07-11T07:54:00Z
- **Tasks:** 3 (1 auto, 2 checkpoint:human-verify — both pre-approved by the orchestrator's delegated authorization)
- **Files modified:** 0 (process/observation plan — no git-tracked source or config files changed)

## Accomplishments

- **CI-03 verified as a no-op (Task 1):** `pyproject.toml` confirmed to declare all three required ceilings; `.github/workflows/drift.yml` confirmed to hardcode none (its `uv lock --upgrade` derives its ceiling from `pyproject.toml`); `.github/dependabot.yml`'s `sphinx-typst-stack` group confirmed to carry only `patterns`/`exclude-patterns`, no version fields. Zero file edits made — the automated verify command (`grep ... && echo CI-03-VERIFIED-NOOP`) passed.
- **Branch protection reconciled (Task 2):** Captured the live stale `main` `required_status_checks.contexts` via `gh api repos/YuSabo90002/typsphinx/branches/main/protection`, then applied a narrow-surface `PATCH .../protection/required_status_checks` (contexts + strict only — no other protection field touched) to remove the two un-producible legacy contexts and add the current job names. GET-verified after the change.
- **release/v0.5.0 pushed to origin** — discovered it had never been pushed (blocking issue for both the pre-flight and the PR); pushed as a Rule 3 fix.
- **D-02-safe pre-flight (Task 3, step 1):** `gh workflow run ci.yml --ref release/v0.5.0` (existing `workflow_dispatch` trigger, no YAML edit) — watched to completion: **12/12 jobs green**, the first-ever GitHub Actions exercise of the Sphinx 9.1/docutils 0.22/typst 0.15 stack across ubuntu/windows/macos x Python 3.12/3.13. Local `uv run tox -e docs-pdf` (the docs.yml proxy, since docs.yml has no `workflow_dispatch`) also passed clean.
- **Observation PR #112 opened** (`release/v0.5.0 -> main`) — fires both `ci.yml` and `docs.yml` on `pull_request:[main]`.
- **All 13 jobs observed green:** Lint and Format Check, Type Check, Code Coverage, Build Package, Integration Test - basic/advanced, all 6 "Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest" legs, and docs.yml `build-docs`.
- **CI-02 confirmed running in live CI:** `tests/test_preview_smoke_gate.py::test_preview_smoke_all_four_packages_compile` confirmed PASSED in all 6 matrix legs plus Code Coverage's job log (grepped from `gh run view --log`).
- **PR merge-readiness confirmed clean:** `gh pr view 112 --json mergeable,mergeStateStatus` returns `MERGEABLE`/`CLEAN` — confirming the Task 2 branch-protection reconciliation took effect (no stuck "waiting for status" on a non-existent context).
- **PR left OPEN and UNMERGED** per D-03 — Phase 10 will add the `__version__` 0.4.3 -> 0.5.0 commit to this same PR and merge.
- **Dependabot PR #108** confirmed still open/red and untouched (informational only, per Pitfall 5 — unrelated pre-existing issue, superseded once v0.5.0 merges).

## Branch Protection: Before / After

**BEFORE** (`gh api repos/YuSabo90002/typsphinx/branches/main/protection`):
```
required_status_checks.contexts:
  - Test Python 3.10 on ubuntu-latest   <- stale, job no longer produced (dropped Phase 6)
  - Test Python 3.11 on ubuntu-latest   <- stale, job no longer produced (dropped Phase 6)
  - Test Python 3.12 on ubuntu-latest
  - Lint and Format Check
  - Type Check
  - Code Coverage
  - Build Package
  - Test Python 3.13 on ubuntu-latest
strict: true
enforce_admins: false
required_linear_history: false
allow_force_pushes: false
allow_deletions: false
required_conversation_resolution: true
```

**AFTER** (via narrow `PATCH .../protection/required_status_checks`):
```
required_status_checks.contexts:
  - Test Python 3.12 on ubuntu-latest
  - Lint and Format Check
  - Type Check
  - Code Coverage
  - Build Package
  - Test Python 3.13 on ubuntu-latest
strict: true                              <- unchanged
enforce_admins: false                      <- unchanged (verified via full GET after PATCH)
required_linear_history: false             <- unchanged
allow_force_pushes: false                  <- unchanged
allow_deletions: false                     <- unchanged
required_conversation_resolution: true     <- unchanged
```

**Policy rationale (delegated to executor):** Required = core gates (Lint/Type/Coverage/Build) + the two ubuntu 3.12/3.13 test legs — the primary, fastest, most stable signal. Windows/macOS legs and `docs.yml` `build-docs` are deliberately **not required** — they still run and are fully observable on every PR (as demonstrated: all 13 jobs green on #112), but making them required would risk merge-blocking on cross-OS runner flakiness (a known GitHub Actions characteristic, distinct from actual code regressions). Cross-OS coverage is still enforced procedurally: the D-02-safe `workflow_dispatch` pre-flight step exercises all 3 OS legs before every observation PR is trusted, even though only the ubuntu legs gate the merge button.

## CI-01 Observation: Per-Job Conclusions

**Pre-flight run** (`gh workflow run ci.yml --ref release/v0.5.0`, run id `29145145165`) — disposable, D-02-safe, run BEFORE opening the PR:

| Job | Conclusion |
|-----|-----------|
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.12 on windows-latest | success |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.13 on windows-latest | success |
| Test Python 3.13 on macos-latest | success |

Overall run conclusion: **success** (12/12).

Local `uv run tox -e docs-pdf` (docs.yml proxy, since docs.yml has no `workflow_dispatch`): **OK** — `Generated PDF: docs/_build/pdf/index.pdf`, 2 pre-existing benign warnings (empty-URL reference nodes, unrelated to this phase).

**Observation PR #112** (`https://github.com/YuSabo90002/typsphinx/pull/112`, `release/v0.5.0 -> main`) — `ci.yml` run id `29145206169`, `docs.yml` run id `29145206171`:

| Check | Conclusion |
|-------|-----------|
| Lint and Format Check | pass |
| Type Check | pass |
| Code Coverage | pass |
| Build Package | pass |
| Integration Test - basic | pass |
| Integration Test - advanced | pass |
| Test Python 3.12 on ubuntu-latest | pass |
| Test Python 3.12 on windows-latest | pass |
| Test Python 3.12 on macos-latest | pass |
| Test Python 3.13 on ubuntu-latest | pass |
| Test Python 3.13 on windows-latest | pass |
| Test Python 3.13 on macos-latest | pass |
| build-docs (docs.yml) | pass |

**13/13 pass.** `tests/test_preview_smoke_gate.py::test_preview_smoke_all_four_packages_compile` confirmed `PASSED` in the job logs of all 6 test-matrix legs and Code Coverage (grepped via `gh run view <id> --log`).

**PR state:** `state: OPEN`, `isDraft: false`, `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN` — confirms the Task 2 reconciliation resolved cleanly against the real checks; **PR NOT merged** (D-03 — Phase 10 owns the merge).

## Task Commits

This plan produces no git-tracked source changes (`files_modified: []` per plan frontmatter) — its artifacts are process/observation:

1. **Task 1: Verify CI-03 guardrails (no-op)** — no commit (verification-only, zero file edits).
2. **Task 2: Reconcile main branch-protection required_status_checks** — no git commit (GitHub repo setting via `gh api`, not a tracked file); recorded above (before/after).
3. **Task 3: Pre-flight, open PR #112, observe all-green** — no git commit for the PR itself; `git push -u origin release/v0.5.0` was the one git operation performed (pushing existing, already-committed commits — no new commits created).

**Plan metadata:** commit hash recorded below (this SUMMARY + STATE/ROADMAP/REQUIREMENTS updates).

## Files Created/Modified

None — this plan's artifacts are a GitHub PR (#112) and a GitHub repo setting (branch protection), not git-tracked files. `release/v0.5.0` was pushed to `origin` (no new commits created by this plan; all commits were already made in 09-01).

## Decisions Made

- Branch-protection required-checks policy: core gates + ubuntu 3.12/3.13 legs required; windows/macos legs and `build-docs` observable-but-not-required (see rationale above).
- Pushed `release/v0.5.0` to origin as a Rule 3 blocking-issue fix (it had never been pushed, which blocked both the `workflow_dispatch` pre-flight and PR creation).
- Left Dependabot PR #108 untouched (out of scope, pre-existing, superseded at Phase 10 merge).
- PR #112 left open and unmerged per D-03.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Pushed release/v0.5.0 to origin**
- **Found during:** Task 3, step 1 (pre-flight `workflow_dispatch`)
- **Issue:** `gh workflow run ci.yml --ref release/v0.5.0` failed with `HTTP 422: No ref found for: release/v0.5.0` — the branch existed only locally, never pushed to `origin`.
- **Fix:** `git push -u origin release/v0.5.0` (no new commits created — all commits were already made and committed in 09-01; this only made the existing branch visible to GitHub).
- **Files modified:** none (git ref operation only).
- **Verification:** Subsequent `gh workflow run ci.yml --ref release/v0.5.0` succeeded; `gh pr create --head release/v0.5.0` succeeded.
- **Committed in:** N/A (no commit; branch push only).

---

**Total deviations:** 1 auto-fixed (1 blocking — Rule 3, excluded from the "package install" carve-out since this was a `git push`, not a package install).
**Impact on plan:** Necessary prerequisite for the plan's own stated actions (pre-flight + PR creation); no scope creep.

## Issues Encountered

- `gh api --method PATCH .../protection/required_status_checks -f strict=true` initially failed (`"strict" is not a boolean` — `-f` sends a string). Resolved by using `-F strict=true` (typed boolean flag) instead. No repository state was affected by the failed attempt (422 rejected before any write).

## User Setup Required

None - no external service configuration required beyond the already-authenticated `gh` CLI (verified via `gh auth status` before starting: logged in as `YuSabo90002`, scopes include `repo`/`workflow`).

## Next Phase Readiness

- CI-01 and CI-03 are both satisfied and requirement-complete.
- PR #112 (`release/v0.5.0 -> main`) is open, all-green, and merge-ready (`MERGEABLE`/`CLEAN`) — Phase 10 can add its `__version__` bump commit directly to this PR and merge once ready.
- `main` branch protection now reflects real, producible job names — Phase 10's merge will not be blocked by phantom pending checks.
- Dependabot PR #108 remains open/red and out of scope — flagged for Phase 10 to close as superseded once v0.5.0 merges.
- No blockers carried forward from this plan.

---
*Phase: 09-green-ci-matrix-smoke-test-guardrails*
*Completed: 2026-07-11*
