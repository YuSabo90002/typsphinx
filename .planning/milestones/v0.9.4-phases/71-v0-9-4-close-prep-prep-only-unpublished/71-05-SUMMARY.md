---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
plan: 05
subsystem: release-prep
tags: [merge-tree, uv-lock, ruff, branch-protection, gh-cli, non-committing]

requires:
  - phase: 71-v0-9-4-close-prep-prep-only-unpublished (plans 01, 02)
    provides: "the merged wave-1 CHANGELOG.md (four bold bullets) and MILESTONE_BASE from 71-SC1-INVARIANTS.md, both required for a correct trial-merge input and its no-op comparison"
provides:
  - "71-PREFLIGHT-EVIDENCE.md: non-committing git merge-tree --write-tree trial merge of origin/main, reproduced and proven a no-op today, with the merged uv.lock validated and the merged tree lint-clean at the merged ruff/black versions"
  - "main's strict branch protection (six required checks) and the #135/#136/#143 merge-commit precedent, recorded live for 71-HANDOFF.md's conditional branch-update step (D-06)"
  - "The open-PR census at execution time (zero open, left untouched) for D-12"
  - "TRIAL_MERGE_VERDICT = MET"
affects: [71-06, 71-07]

actuals:
  tokens: 3354
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns: [non-committing trial merge via git merge-tree --write-tree + git archive + uv lock --check, reused from 69-PREFLIGHT-EVIDENCE.md]

key-files:
  created:
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md
  modified: []

key-decisions:
  - "LOCK_CHECK_UV_VERSION recorded as the bare uv version number only ('uv 0.12.13'), omitting the platform suffix in parentheses that `uv --version` prints by default — the plan's evidence-key-line contract bans any opening parenthesis on a KEY = value line, and this key is not verified against a specific format downstream, so the parenthesized platform tag was dropped rather than moved to a second line."
  - "With MAIN_MOVED = no (origin/main equals MILESTONE_BASE exactly), the trial merge is confirmed a no-op (TRIAL_IS_NOOP = yes) and this branch's own uv.lock already pins the same ruff version as the merged tree (both 0.16.6) — expected, since nothing from origin/main is being absorbed today."

requirements-completed: []

coverage:
  - id: D1
    description: "Non-committing trial merge of origin/main into the milestone branch is measured conflict-free and reproducible from its recorded inputs, a no-op today, with a valid merged uv.lock"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-05-PLAN.md Task 1 <verify><automated> (full shell predicate over 71-PREFLIGHT-EVIDENCE.md, live git merge-tree/uv lock --check re-checks)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Merged tree lints clean (ruff check ., black --check .) at the merged lock's ruff/black versions; main's strict protection, six required checks, the #135/#136/#143 merge-commit precedent, and the open-PR census are recorded live"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-05-PLAN.md Task 2 <verify><automated> (full shell predicate over 71-PREFLIGHT-EVIDENCE.md, live uv sync --locked/ruff/black/gh api/git log re-checks)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-13
status: complete
---

# Phase 71 Plan 05: REL-13 Update-Step Pre-Flight (Non-Committing Trial Merge) Summary

**`ORIGIN_MAIN_SHA = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d`, `MAIN_MOVED = no`, `MERGE_RC = 0`, `MERGE_TREE = 0fc0c03a5fc3cb730542fde7a1c11f01b90205fe`, `TRIAL_IS_NOOP = yes`, `LOCK_CHECK_EXIT = 0`, `MERGED_RUFF_LOCK_VERSION = 0.16.6`, `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0`, `PROTECTION_STRICT = true`, `PR_CENSUS_AT = 2026-09-13T08:48:59Z` (`OPEN_PRS = 0`), `TRIAL_MERGE_VERDICT = MET`.**

No `## FINDING` or `## HALT` section was written — every measurement in this plan passed.

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-13T08:45:19Z
- **Completed:** 2026-09-13T08:50:22Z
- **Tasks:** 2
- **Files modified:** 1 (`71-PREFLIGHT-EVIDENCE.md`, created)

## Accomplishments

- Measured — without committing anything to the branch (D-05) — that `origin/main` merges
  conflict-free into the milestone branch via `git merge-tree --write-tree`, reproduced the same
  tree SHA on a second run (`MERGE_TREE_REPRODUCED = yes`), and confirmed it is a no-op today
  because `origin/main` sits exactly at `MILESTONE_BASE` (`TRIAL_IS_NOOP = yes`, edge: adjacency).
- Extracted the merged `pyproject.toml`/`uv.lock` into a scratch tree outside the repository and
  proved `uv lock --check` passes there (`LOCK_CHECK_EXIT = 0`), with `pyproject.toml:7` still
  `version = "0.9.2"` and the merged CHANGELOG carrying all four `## [Unreleased]` bold bullets
  (wave 1's fourth bullet included, per the task's precondition).
- Synced a second scratch tree from the whole merged tree with `uv sync --locked`, confirmed the
  running `ruff` matches the merged lock's pinned version (0.16.6), and proved both
  `ruff check .` and `black --check .` exit 0 on the merged tree — the trial-merge half of
  ROADMAP SC#3.
- Recorded `main`'s live branch protection (`strict: true`, six named required checks), the
  `#135`/`#136`/`#143` merge-commit precedent (`MERGE_PRECEDENT_HITS = 3`), and a read-only
  open-PR census (zero open PRs at `PR_CENSUS_AT`, positive-controlled against a non-empty
  `--state all` listing) — every fact the handoff's conditional branch-update step (D-06) and its
  D-12 prohibition depend on.
- Confirmed nothing moved: HEAD and the canonical ref both stayed at `BASE_71_05`
  (`7a42bf996b1aaca24a8b17346be78459e6d41e2b`) throughout, the merge-base with `origin/main`
  stayed equal to `MILESTONE_BASE`, and no merge commit exists on the branch since the base.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — fetch, non-committing trial merge reproduced from its inputs, merged lock checked in scratch** - `f6b170e3` (feat)
2. **Task 2: Merged-tree lint at the merged lock's versions, main's protection and merge-method precedent, open-PR census** - `0545556c` (feat)

**Plan metadata:** committed separately after this SUMMARY (see final commit).

## Files Created/Modified

- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md` - the
  full pre-flight transcript: head check/provisioning, fetch/divergence, trial merge, merged
  lock, nothing-moved (Task 1); merged-tree lint, main protection, merge-method precedent,
  open-PR census, and the trial-merge verdict (Task 2)

## Decisions Made

- `LOCK_CHECK_UV_VERSION` is recorded as `uv 0.12.13` without the `(x86_64-unknown-linux-gnu)`
  platform suffix `uv --version` normally prints — the plan's evidence-key-line contract bans any
  opening parenthesis on a `KEY = value` line, and no downstream check depends on this key's exact
  format, so the parenthesized suffix was dropped from the key line rather than moved to a
  separate prose line.
- Kept the freshly-measured `MERGE_RC`/`MERGE_TREE`/lint/protection/precedent/PR-census values as
  this plan's own recorded facts, per its instruction to re-measure everything live rather than
  transcribe from `71-CONTEXT.md` or `71-RESEARCH.md`.

## Deviations from Plan

None - plan executed exactly as written. The only correction was the `LOCK_CHECK_UV_VERSION`
formatting choice described above, made before any commit (not a fix to already-committed
content) — recorded under Decisions Made rather than as a deviation, since no rule (1-4) was
triggered and no incorrect value was ever committed.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** None.

## Issues Encountered

None. Both tasks' automated `<verify>` predicates passed on every re-check; no `## FINDING` or
`## HALT` section was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The trial-merge half of ROADMAP SC#3 is proven met without touching the branch (D-05); the
  merged lock, merged-tree lint, `main` protection, merge-method precedent, and open-PR census are
  all recorded live for `71-HANDOFF.md`'s conditional branch-update step (D-06) and its D-12
  prohibition.
- `origin/main` was at `d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d` (= `MILESTONE_BASE`) at
  `ORIGIN_MAIN_SHA`'s measurement time and at `PR_CENSUS_AT`; both `ORIGIN_MAIN_SHA` and
  `MERGE_TREE` hold only for that moment, and 71-HANDOFF.md's own procedure re-runs `merge-tree`
  immediately before any real PR. The open-PR state likewise holds only at `PR_CENSUS_AT` and must
  be re-read by the handoff.
- No blockers or concerns for 71-06 or 71-07. This plan touched no shared orchestrator artifact
  (`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` are all unchanged in
  this worktree) and created no `71-VERIFICATION.md`.

## Self-Check: PASSED

- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md` exists: FOUND
- Commit `f6b170e3` (Task 1) exists in `git log --oneline --all`: FOUND
- Commit `0545556c` (Task 2) exists in `git log --oneline --all`: FOUND
- Both tasks' `<verify><automated>` predicates re-run component-by-component and all recorded
  key values (`MERGE_RC`, `MERGE_TREE`, `MERGE_TREE_REPRODUCED`, `TRIAL_IS_NOOP`, `MAIN_MOVED`,
  `LOCK_CHECK_EXIT`, `MERGED_VERSION_LINE`, `MERGED_RUFF_LOCK_VERSION`,
  `MERGED_CHANGELOG_BOLD`, `MERGED_RUFF_RUN_VERSION`, `MERGED_RUFF_EXIT`, `MERGED_BLACK_EXIT`,
  `PROTECTION_STRICT`, `PROTECTION_CONTEXTS_COUNT`, `MERGE_PRECEDENT_HITS`, `OPEN_PRS`,
  `DEPENDABOT_OPEN_PRS`, `TRIAL_MERGE_VERDICT`) matched fresh live re-measurement.
- `git diff --name-only` against `BASE_71_05` shows only `71-PREFLIGHT-EVIDENCE.md`;
  `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` all byte-unchanged.
- No key line in the evidence file carries an opening parenthesis; no `## HALT` heading present.

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Completed: 2026-09-13*
