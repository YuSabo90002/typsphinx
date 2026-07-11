---
phase: 10-version-string-fix-v0-5-0-release
plan: 02
subsystem: docs
tags: [changelog, release-notes, keep-a-changelog]

# Dependency graph
requires:
  - phase: 10-01
    provides: "typsphinx.__version__ single-sourced at 0.5.0 via importlib.metadata"
provides:
  - "Curated, user-facing ## [0.5.0] CHANGELOG.md entry (Changed/Fixed/Added) as the single source for the eventual GitHub Release body"
affects: [gsd-complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - CHANGELOG.md

key-decisions:
  - "Followed the file's existing ### Changed/### Fixed/### Added subsection shape (matching [0.4.3]) rather than inventing a new structure"
  - "No [0.4.4] section backfilled — v0.4.4 was internal tooling only, per RESEARCH.md Pitfall 4"

patterns-established: []

requirements-completed: [REL-01]

coverage:
  - id: D1
    description: "Curated ## [0.5.0] - 2026-07-11 CHANGELOG.md entry inserted under the top ## [Unreleased] header, above ## [0.4.3], covering the five milestone themes (Sphinx 9.1 + docutils 0.22, typst 0.15 + @preview kai fix, admonition rendering fix, Python 3.12-3.13 floor, CI smoke-gate + guardrails)"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "grep -n '## \\[0.5.0\\] - 2026-07-11' CHANGELOG.md && awk ordering check (0.5.0 before 0.4.3)"
        status: pass
    human_judgment: false
  - id: D2
    description: "[0.5.0] link reference added; [Unreleased] compare link updated to v0.5.0...HEAD; no [0.4.4] backfill"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "grep -q '^\\[0.5.0\\]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0' CHANGELOG.md; grep -q 'compare/v0.5.0...HEAD' CHANGELOG.md; grep -c '## \\[0.4.4\\]' CHANGELOG.md == 0"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-07-11
status: complete
---

# Phase 10 Plan 02: Curated v0.5.0 CHANGELOG Entry Summary

**Added a curated, user-facing `## [0.5.0]` CHANGELOG.md section (Changed/Fixed/Added) under the top `[Unreleased]` header, positioned as the single source for the eventual v0.5.0 GitHub Release body.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-11T11:01:00Z
- **Completed:** 2026-07-11T11:06:19Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Inserted `## [0.5.0] - 2026-07-11` directly under the canonical top `## [Unreleased]` header (line 8) and above `## [0.4.3]`, following the file's existing `### Changed`/`### Fixed`/`### Added` subsection convention
- Covered all five required milestone themes as user-facing prose: the Sphinx 9.1 + docutils 0.22 + typst 0.15 forward-ecosystem port (incl. the mitex `kai` fix), the Phase 8.1 admonition rendering fix, the Python 3.12-3.13 floor raise, and the CI smoke-gate + drift/Dependabot guardrails
- Added the `[0.5.0]` link reference and updated the `[Unreleased]` compare link from `v0.4.3...HEAD` to `v0.5.0...HEAD`; left the stray second `## [Unreleased]` block near end-of-file untouched
- Did not backfill a `[0.4.4]` section (v0.4.4 was internal tooling only)

## Task Commits

Each task was committed atomically:

1. **Task 1: Insert curated ## [0.5.0] CHANGELOG entry under the top Unreleased header + fix link references** - `483c77a` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified
- `CHANGELOG.md` - New `## [0.5.0] - 2026-07-11` section with `### Changed`/`### Fixed`/`### Added` subsections; new `[0.5.0]` link reference; `[Unreleased]` compare link updated to `v0.5.0...HEAD`

## Decisions Made
- Matched the `[0.4.3]` entry's subsection shape and prose style exactly (bold summary line + nested detail bullets) rather than a flat bullet list, for visual consistency with the rest of the file
- No `[0.4.4]` backfill, per RESEARCH.md Pitfall 4 and the plan's explicit instruction

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [0.5.0]` section is now ready to be passed as `release.yml`'s `body_path` at milestone close.
- REL-01's Phase-10 scope (version single-source fix in 10-01 + curated CHANGELOG entry in 10-02) is now complete. The remaining REL-01 work — merging PR #112, tagging `v0.5.0`, and `release.yml` publishing to PyPI/GitHub Releases — is explicitly deferred to `/gsd-complete-milestone`, per this plan's scope fence.
- No blockers.

---
*Phase: 10-version-string-fix-v0-5-0-release*
*Completed: 2026-07-11*

## Self-Check: PASSED
