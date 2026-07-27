---
phase: 31-published-url-cutover-repo-wide-link-guard
plan: 02
subsystem: infra
tags: [github-api, repository-settings, read-the-docs, http-verification]

# Dependency graph
requires:
  - phase: 30.1-japanese-rtd-site-translations-repo
    provides: the live typsphinx.readthedocs.io RTD project (English + ja) this plan points the About link at
provides:
  - Repository `homepage` field set to the Read the Docs bare root (https://typsphinx.readthedocs.io/)
  - Real-HTTP evidence file proving the About -> Website link resolves (200, via a documented 302 hop)
affects: [phase-31-plan-05-issue-119-close-reply, phase-33-release-prep-default-version-flip]

# Tech tracking
tech-stack:
  added: []
  patterns: ["gh api -X PATCH single-field repository metadata write with before/after read-back verification"]

key-files:
  created: [.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ABOUT-EVIDENCE.md]
  modified: []

key-decisions:
  - "Used the gh api PATCH path (not the owner-manual fallback) — the local token carries repo scope and admin:true on the repository, so the API call succeeded without owner action."
  - "Set homepage to the bare RTD root (no /en/ or /latest/ segment) per D-11, so Phase 33's Default Version flip (latest -> stable) propagates automatically with no re-edit."
  - "Left Issue #119 open and uncommented per D-15/D-16 — the close is a post-merge handoff to /gsd-complete-milestone, not part of this plan's verification window."

patterns-established: []

requirements-completed: [DOC-10]

coverage:
  - id: D1
    description: "Repository About -> Website field set to https://typsphinx.readthedocs.io/ via gh api PATCH, read back byte-identical, with unrelated fields (description/private/archived/has_issues) confirmed unchanged"
    requirement: "DOC-10"
    verification:
      - kind: other
        ref: "gh api repos/YuSabo90002/typsphinx --jq '.homepage' == https://typsphinx.readthedocs.io/ (plan Task 1 automated verify block)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Real-HTTP proof the About link resolves: bare root -> 302 -> /en/latest/ -> 200, plus ja/latest/ -> 200, recorded verbatim in 31-ABOUT-EVIDENCE.md"
    requirement: "DOC-10"
    verification:
      - kind: other
        ref: "curl -L --max-time 20 https://typsphinx.readthedocs.io/ -> 200 (plan Task 2 automated verify block)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-26
status: complete
---

# Phase 31 Plan 02: Published-URL Cutover - About Website Field Summary

**Repository About -> Website field flipped from null to the Read the Docs bare root via `gh api PATCH`, with a real-HTTP curl transcript proving the link a visitor clicks now resolves through a documented 302 -> 200 redirect chain.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-26T13:49:00Z
- **Completed:** 2026-07-26T13:51:18Z
- **Tasks:** 2 completed
- **Files modified:** 1 (created)

## Accomplishments
- Repository `homepage` metadata field set to `https://typsphinx.readthedocs.io/` (confirmed `null` beforehand, matching the planning-time reading), discharging DOC-10's "About set" half.
- Real-HTTP verification recorded: the bare root answers `302` to `https://typsphinx.readthedocs.io/en/latest/`, which answers `200` — the exact chain a visitor following the About panel link now traverses, resolving Issue #119's reported 404.
- Japanese documentation root (`https://typsphinx.readthedocs.io/ja/latest/`) independently confirmed `200` in the same measurement pass, for Plan 05's later reuse.
- `31-ABOUT-EVIDENCE.md` written with verbatim commands/outputs (before-value, PATCH command, read-back, both curl invocations, headers, timestamp) and an explicit closing statement of what this plan deliberately does not discharge.

## Task Commits

Each task was committed atomically:

1. **Task 1: Set the repository Website field to the Read the Docs root** - no file commit (GitHub repository metadata mutation only; verified via `gh api` read-back, no working-tree change to stage)
2. **Task 2: Verify the Website link over real HTTP and record the evidence** - `a6cb142` (feat)

Tasks 1 and 2 share a single commit because Task 1 produces no repository file change (only a GitHub API side effect) — its verification evidence is captured directly in Task 2's evidence file and commit message.

**Plan metadata:** committed separately per the worktree parallel-executor protocol (STATE.md/ROADMAP.md updates deferred to the orchestrator).

_Note: this plan has no TDD tasks._

## Files Created/Modified
- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ABOUT-EVIDENCE.md` - Verbatim before/after `gh api` transcript, PATCH command, both curl invocations (with/without redirects), the Japanese-root reading, the UTC measurement timestamp, and the explicit DOC-10 deferred-close note.
- Repository metadata (not a tracked file): `homepage` field on `YuSabo90002/typsphinx`, `null` -> `https://typsphinx.readthedocs.io/`.

## Decisions Made
- Attempted the `gh api PATCH` path first per the plan's stated fallback ordering; it succeeded (token has `repo` scope + `admin: true`), so the owner-manual About-gear-icon fallback was never invoked.
- Confirmed via two independent `gh api` reads (jq and a Python `json.load` parse) that the before-value was genuinely `null`, not an empty string, before mutating it — avoids ambiguity in the evidence record.
- Verified the PATCH touched only `homepage` by snapshotting `description`/`private`/`archived`/`has_issues` before and after and asserting equality — directly satisfies threat T-31-06's mitigation.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<action>` and `<verify>` blocks ran unmodified and passed on the first attempt.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required. The plan's `user_setup` fallback path (manual About-gear-icon edit) was not needed because the `gh api PATCH` call succeeded directly.

## Next Phase Readiness
- DOC-10's "About set + resolving" half is fully discharged and evidenced; ready for Plan 05 to draft the Issue #119 close-reply referencing this evidence.
- No blockers for Plan 03 (README/pyproject rewrite) — this plan touched no repository files, so there is no collision risk with Plan 03's edits to `README.md`/`pyproject.toml`.
- Outstanding, by design (not a gap): Issue #119 stays `OPEN` until `/gsd-complete-milestone`; the close-reply draft itself belongs to Plan 05.

---
*Phase: 31-published-url-cutover-repo-wide-link-guard*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ABOUT-EVIDENCE.md`
- FOUND: commit `a6cb142` in `git log --oneline --all`
