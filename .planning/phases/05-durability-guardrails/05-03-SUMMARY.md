---
phase: 05-durability-guardrails
plan: 03
subsystem: infra
tags: [github-actions, ci-cd, dependency-drift, gh-cli, uv, tox]

# Dependency graph
requires:
  - phase: 05-durability-guardrails (plan 01)
    provides: "--locked appended to all 9 uv sync call sites across ci.yml/docs.yml/release.yml"
provides:
  - "New standalone .github/workflows/drift.yml — weekly + manual dependency-drift detector"
  - "Deduplicated GitHub Issue reporting pattern (gh issue list/create/comment) for scheduled CI jobs"
affects: [05-04 (dependabot grouping + docs finalization, post-merge workflow_dispatch smoke test)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scheduled non-blocking GitHub Actions workflow (schedule: + workflow_dispatch:) kept fully separate from the blocking per-PR pipeline"
    - "uv lock --upgrade before uv sync --locked to intentionally re-resolve past the committed lock within a single job (order-dependent; --locked here validates same-job consistency, not the committed lock)"
    - "Native gh issue list --label X --state open --json number --jq dedup pattern for scheduled-failure reporting (no third-party Marketplace action)"

key-files:
  created: [.github/workflows/drift.yml]
  modified: []

key-decisions:
  - "Implemented drift.yml exactly per RESEARCH.md Pattern 2 skeleton and PATTERNS.md's synthesized version — no deviation from the plan's specified step order, permissions, or tox env selection."

patterns-established:
  - "Pattern: scheduled/advisory CI concerns live in their own standalone workflow file, never bolted onto the blocking per-PR pipeline as a continue-on-error job (D-04)."

requirements-completed: [DUR-02]

coverage:
  - id: D1
    description: "drift.yml exists, is valid YAML, triggers on both schedule (weekly Monday 00:00 UTC) and workflow_dispatch"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "python -c \"import yaml; ...\" (frontmatter YAML-parse assertion on on.schedule/on.workflow_dispatch/on.schedule[0].cron)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Root permissions block scoped to exactly contents:read + issues:write (least-privilege)"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "python -c \"assert w['permissions']=={'contents':'read','issues':'write'}\""
        status: pass
    human_judgment: false
  - id: D3
    description: "uv lock --upgrade precedes uv sync ... --locked (Pitfall 2 step order)"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "grep -n line-number comparison: 'uv lock --upgrade' (line 29) < 'uv sync .*--locked' (line 32)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Re-resolved dependency set exercised via uv run tox -e cov,docs-pdf"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "grep -q 'tox -e cov,docs-pdf' .github/workflows/drift.yml"
        status: pass
    human_judgment: false
  - id: D5
    description: "On failure, deduplicated GitHub Issue reporting via native gh issue list/create/comment keyed on open drift-labelled issue"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "grep -q for 'if: failure()', 'gh issue list', 'gh issue create', 'gh issue comment' all present"
        status: pass
    human_judgment: false
  - id: D6
    description: "No version-control write-back of uv.lock anywhere in the workflow (D-05)"
    requirement: "DUR-02"
    verification:
      - kind: other
        ref: "grep -E 'git (add|commit|push)' .github/workflows/drift.yml returns empty"
        status: pass
    human_judgment: false
  - id: D7
    description: "Live runtime smoke test (workflow_dispatch trigger, gh run watch, forced-failure dedup behavior) — requires drift.yml on the default branch"
    requirement: "DUR-02"
    verification: []
    human_judgment: true
    rationale: "workflow_dispatch cannot be triggered until this file is merged to the default branch; deferred to plan 05-04 post-merge per the plan's own <verification> section and D-10."

duration: 3min
completed: 2026-07-05
status: complete
---

# Phase 5 Plan 3: Weekly Dependency Drift Detector Summary

**New standalone `.github/workflows/drift.yml`: weekly + manually-dispatchable job that re-resolves latest allowed dependency versions via `uv lock --upgrade`, exercises them against `tox -e cov,docs-pdf`, and files/updates a single deduplicated GitHub Issue on failure — closing DUR-02 without ever blocking a merge or altering the committed lock.**

## Performance

- **Duration:** 3 min
- **Completed:** 2026-07-05T05:18:42Z
- **Tasks:** 1
- **Files modified:** 1 (new file)

## Accomplishments
- Created `.github/workflows/drift.yml` as a fully standalone workflow (not folded into `ci.yml`), satisfying D-04
- Weekly `schedule: cron: '0 0 * * 1'` trigger plus `workflow_dispatch:` for manual D-10 validation
- Root-level `permissions: {contents: read, issues: write}` — least-privilege, mirroring docs.yml/release.yml's explicit-permissions convention rather than ci.yml's unset default
- Correct step order: `uv lock --upgrade` (line 29) strictly precedes `uv sync --extra dev --extra docs --locked` (line 32), avoiding RESEARCH Pitfall 2 (reversed order would make the job always fail)
- Exercises the re-resolved dependency set via `uv run tox -e cov,docs-pdf` — full pytest+coverage plus the historically-fragile PDF path that produced the `kai`-class break
- On failure, native `gh issue list --label drift --state open --json number --jq '.[0].number'` dedup lookup: comments on an existing open `drift`-labelled issue if found, else creates a new one with a link to the failing run URL
- No `git add`/`commit`/`push` of `uv.lock` anywhere in the workflow (D-05 — verified via negative grep)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create drift.yml — weekly + dispatch drift detector with deduplicated issue reporting (DUR-02 / D-04, D-05, D-06, D-07, D-10)** - `9b8b2ff` (feat)

**Plan metadata:** (this commit, docs(05-03): complete plan)

## Files Created/Modified
- `.github/workflows/drift.yml` - New standalone weekly + workflow_dispatch drift-detection workflow (52 lines): checkout → setup-uv → python install 3.10 → `uv lock --upgrade` → `uv sync --extra dev --extra docs --locked` → `uv run tox -e cov,docs-pdf` → `if: failure()` deduplicated `gh issue` reporting step

## Decisions Made
None — the plan's specified file content (adapted directly from RESEARCH.md §Pattern 2 and PATTERNS.md's synthesized skeleton) was implemented verbatim with no deviation.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. `nix-shell -p python3Packages.pyyaml --run "python3 -c ..."` was used for the YAML-parse verification assertions (the bare local `python3` lacks `pyyaml`, consistent with the same NixOS workaround plan 05-02 documented). No workflow runtime execution was attempted locally, per the plan's explicit deferral of live `workflow_dispatch` smoke testing to plan 05-04 post-merge.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `.github/workflows/drift.yml` is ready to merge; all static/config-level acceptance criteria pass (valid YAML, both triggers, exact minimal permissions, correct step order, `cov,docs-pdf` present, dedup `gh issue` logic, no lockfile write-back, not coupled to `ci.yml`).
- Live runtime verification (a manual `workflow_dispatch` trigger via `gh workflow run drift.yml && gh run watch`, plus branch-protection confirmation that `drift-check` is NOT a required status check per D-07) is explicitly deferred to plan 05-04, since `workflow_dispatch` requires the file to exist on the default branch first (a post-merge prerequisite, not a blocker for this plan).
- No blockers for proceeding to plan 05-04 (DUR-03 Dependabot grouping + DUR-04 README badge + phase finalization).

---
*Phase: 05-durability-guardrails*
*Completed: 2026-07-05*

## Self-Check: PASSED

- FOUND: `.github/workflows/drift.yml`
- FOUND: `9b8b2ff` (task commit)
