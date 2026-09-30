---
phase: 75-v0-9-6-release-prep-prep-only
plan: 06
subsystem: infra
tags: [ci, release-prep, github-actions, git-push, workflow-dispatch]

# Dependency graph
requires:
  - phase: 75-v0-9-6-release-prep-prep-only (75-04)
    provides: SC4_LOCAL_VERDICT = MET (amended linkcheck reading, green local tree)
  - phase: 75-v0-9-6-release-prep-prep-only (75-05)
    provides: TRIAL_MERGE_VERDICT = MET (non-committing trial merge, main protection, decoy census)
  - phase: 75-v0-9-6-release-prep-prep-only (75-03)
    provides: BUMP_COMMIT_SHA (the version bump + CHANGELOG commit carried by the pushed tip)
provides:
  - Bumped milestone tip pushed to origin as a fast-forward, no tag, no decoy
  - Exactly one workflow_dispatch CI run on that tip, completed and success, every job transcribed
  - SC4_CI_VERDICT = MET
affects: [75-07]

# Actuals (#2632)
actuals:
  tokens: 3275
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: [foreground-gh-run-watch, key-line-evidence-with-halt-headings]

key-files:
  created:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "Took 75-GREEN-TREE-EVIDENCE.md's amended SC4_LOCAL_VERDICT = MET (2026-09-20 owner decision on the three linkcheck records) at face value per the upstream_gate_state briefing — did not re-run linkcheck or re-litigate the amendment."
  - "No gsd/v0.9.6-milestone decoy existed locally or on origin at the decoy census, so DECOY_ACTION = none-present and no branch deletion or main-checkout re-point was needed."
  - "gh workflow run CI returned a run URL directly on this call (unlike a bare success message); treated the returned URL and the subsequent gh run list confirmation as the single source of truth for RUN_ID rather than parsing stdout shape."

requirements-completed: []  # REL-15 is a coverage ID only; closed at /gsd-complete-milestone per plan frontmatter, not by any plan.

coverage:
  - id: D1
    description: "Bumped milestone tip pushed to origin as a fast-forward (ORIGIN_BEFORE=e54d47d0 -> PUSHED_SHA=b63e5d45), with a pre-push decoy census (none present), no tag at the tip, and the pushed tree verified to carry the bump commit, the census-guard test, both wave-2 evidence files, and read version = \"0.9.6\"."
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-06-PLAN.md Task 1 <verify><automated> block (git ls-remote/merge-base/cat-file/diff/tag assertions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one workflow_dispatch CI run (RUN_ID 35507024851) dispatched against the pushed SHA, waited on in the foreground to completion (status=completed, conclusion=success), all 12 jobs transcribed by name and conclusion (including both windows-latest and both macos-latest lanes named individually), lint job's black/ruff command lines quoted with matching lock ruff version, dispatch count 1 and zero release.yml runs at the pushed SHA, and main's required checks re-read live and unchanged from Phase 74's close."
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-06-PLAN.md Task 2 <verify><automated> block (gh run view/list + gh api branch-protection assertions)"
        status: pass
    human_judgment: false

patterns-established:
  - "Evidence key lines as bare `KEY = value` on their own line, immediately followed by explanatory prose — lets automated <verify> blocks sed-extract single values while keeping the file human-readable."

duration: 12min
completed: 2026-09-20
status: complete
---

# Phase 75 Plan 06: Push the Bumped Tip and Dispatch One CI Run Summary

**Fast-forward push of the bumped `gsd/v0.9.6-doctest-block-rendering-and-release` tip to origin, followed by exactly one `workflow_dispatch` CI run (RUN_ID 35507024851) that completed green across all 12 jobs — including both `windows-latest` and both `macos-latest` lanes — discharging SC4's CI half.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-20T11:08:08Z
- **Completed:** 2026-09-20T11:20:00Z (approx)
- **Tasks:** 2
- **Files modified:** 1 (`75-CI-EVIDENCE.md`, created)

## Accomplishments
- Gated on wave 2: read `SC4_LOCAL_VERDICT = MET` (the amended linkcheck reading) from `75-GREEN-TREE-EVIDENCE.md` and `TRIAL_MERGE_VERDICT = MET` from `75-PREFLIGHT-EVIDENCE.md`; both held, so the plan proceeded.
- Verified tip identity and fence before pushing: `PUSHED_SHA` equals this worktree's own HEAD, carries `BUMP_COMMIT_SHA` as an ancestor, carries `tests/test_docstring_rest_census_guard.py` and both wave-2 evidence files, reads `version = "0.9.6"` in `pyproject.toml`, touches only `typsphinx/pathfmt.py` and `typsphinx/translator.py` under `typsphinx/` since the milestone base, touches nothing under `.github/` or `flake.nix`, and carries no tag.
- Ran the decoy census (constraint 10) immediately before the push: no `gsd/v0.9.6-milestone` decoy exists locally or on origin, so `DECOY_ACTION = none-present`.
- Pushed `gsd/v0.9.6-doctest-block-rendering-and-release` to origin as a fast-forward (`e54d47d0..b63e5d45`), confirmed the origin head now equals `PUSHED_SHA`, and confirmed only `v0.9.2` (no `v0.9.3`–`v0.9.6`) is tagged on origin.
- Dispatched `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release` exactly once and located the resulting run (RUN_ID 35507024851, headSha matching `PUSHED_SHA`, `createdAt` after `PUSH_AT`) with no registration lag and no 5xx retry needed.
- Waited on the run in the foreground (`gh run watch`, no `run_in_background`) to `completed`/`success`; transcribed all 12 jobs, confirmed the job-name set matches Phase 74's `REFERENCE_JOB_NAMES` exactly, and named all four `windows-latest`/`macos-latest` lanes individually as success.
- Quoted the `Lint and Format Check` job's own `black --check .` and `ruff check .` command lines and its `lint: OK` result line; confirmed CI's installed ruff (0.16.7) matches the pushed tree's own `uv.lock` ruff stanza.
- Confirmed exactly one `workflow_dispatch` CI run at the pushed SHA (`DISPATCH_COUNT = 1`) and zero `release.yml` runs at that SHA (`RELEASE_RUNS_AT_PUSHED = 0`).
- Re-read `main`'s required status checks live (`strict = true`, six named contexts) and confirmed they are unchanged from Phase 74's close values (`REQUIRED_CHECKS_UNCHANGED = yes`).
- Recorded `SC4_CI_VERDICT = MET`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: gate on wave 2, tip identity and fence, decoy census, the fast-forward push, and one CI dispatch** - `4b900995` (feat)
2. **Task 2: Wait for the run in the foreground, transcribe every job, name the four Windows and macOS lanes, quote the tox lint step, and re-read the required checks at phase close** - `394b50f1` (feat)

**Plan metadata:** committed alongside this SUMMARY (worktree mode — orchestrator commits `.planning/STATE.md` / `.planning/ROADMAP.md` centrally after merge).

## Files Created/Modified
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-CI-EVIDENCE.md` - the wave-2 gate, tip identity and fence, decoy census, the push, one dispatch, the completed run with every job, the four named lanes, the tox lint step, the dispatch count, required checks at close, and `SC4_CI_VERDICT`

## Decisions Made
- Took `75-GREEN-TREE-EVIDENCE.md`'s amended `SC4_LOCAL_VERDICT = MET` (2026-09-20 owner decision on the three linkcheck records) at face value, per the upstream_gate_state briefing — did not re-run `tox -e linkcheck` or re-litigate the amendment; cited the `## AMENDED 2026-09-20` section in the evidence file for audit clarity.
- No decoy branch existed at the census point, so the constraint-10 fast-forward/re-point/delete sequence (which would require main-checkout actions) was never triggered — `DECOY_ACTION = none-present`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. The `gh workflow run CI` call printed a run URL directly to stdout rather than the more common empty/confirmation output — this is a `gh` CLI behavior variance, not an error; the subsequent `gh run list` query confirmed the correct run (matching `headSha` and post-`PUSH_AT` `createdAt`) as the single source of truth for `RUN_ID`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `origin`'s milestone branch head is `b63e5d453d604350b55c51a1a77918985d6dad7c`, reached by fast-forward, with a completed, fully green three-OS CI run of its own (RUN_ID 35507024851) and no irreversible action (no tag, no release run, no pull request) taken alongside it.
- Ready for 75-07 (fence and probe observation 2, scope fence, `75-HANDOFF.md`, the REL-16 settlement record).

## Self-Check: PASSED
- `75-CI-EVIDENCE.md` exists on disk: FOUND
- Commit `4b900995` (Task 1) exists in git log: FOUND
- Commit `394b50f1` (Task 2) exists in git log: FOUND
- Commit `05a8af01` (this SUMMARY) exists in git log: FOUND
- Both tasks' full `<verify><automated>` blocks re-run and passed (see plan-verify scripts executed during this session)
- Plan-level `<verification>` re-confirmed: origin head = `PUSHED_SHA` by fast-forward with bump + census-guard test + no tag; exactly one `workflow_dispatch` run, completed/success, all jobs transcribed, four lanes named; zero `release.yml` runs at that SHA and no PR opened; `SC4_CI_VERDICT = MET` with required checks unchanged since Phase 74's close

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Completed: 2026-09-20*
