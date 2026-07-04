---
phase: 04-refresh-dev-tooling
plan: 03
subsystem: docs
tags: [docs, cleanup, python-version, ruff]

# Dependency graph
requires:
  - phase: 04-01
    provides: pyproject.toml dev-tool floor+ceiling bounds (shares the file, different region)
provides:
  - README.md fully aligned to the Phase 3 3.10 Python floor (no surviving 3.9 reference)
  - pyproject.toml ruff UP035/UP006 ignore-list comment text aligned to 3.10+
affects: [phase-04-plan-04 (final push-and-observe gate)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase 3 D-04 per-surface-commit pattern reused for a tiny doc/comment cleanup folded into the tooling PR (D-06 commit 3)"

key-files:
  created: []
  modified:
    - README.md
    - pyproject.toml

key-decisions:
  - "No new decisions — executed exactly as specified in 04-CONTEXT.md D-04 and 04-PATTERNS.md target-state excerpts"

patterns-established: []

requirements-completed: [TOOL-01]

coverage:
  - id: D1
    description: "README.md Python-version references (requirements bullet line 36, version footer line 323) updated from 3.9 to 3.10"
    requirement: "TOOL-01"
    verification:
      - kind: other
        ref: "grep -q 'Python 3.10 or higher' README.md && grep -q '**Python**: 3.10+' README.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "pyproject.toml ruff UP035/UP006 ignore-list comment text updated from 'Python 3.9+ support' to 'Python 3.10+ support', with rule codes unchanged and lint verified inert"
    requirement: "TOOL-01"
    verification:
      - kind: other
        ref: "grep -q 'UP035.*Python 3.10+ support' pyproject.toml && grep -q 'UP006.*Python 3.10+ support' pyproject.toml"
        status: pass
      - kind: other
        ref: "uv run tox -e lint (black --check .) + nix run nixpkgs#ruff -- check . (NixOS local-execution workaround, Phase 3/04-01 precedent)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-07-04
status: complete
---

# Phase 04 Plan 03: Fold in Phase-3 Python 3.9 doc/comment leftover Summary

**Closed out the last two stale `Python 3.9` text references (README requirements bullet + version footer) and the stale ruff `UP035`/`UP006` ignore-list comment in `pyproject.toml`, aligning all documentation and comment text to the 3.10 floor Phase 3 already shipped in code.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-07-04T15:59:57Z
- **Completed:** 2026-07-04T16:05:00Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments
- `README.md` line 36 now reads `- Python 3.10 or higher`; line 323's version footer now reads `**Python**: 3.10+ | **Sphinx**: 5.0+ | **Typst**: 0.11.1+` — no surviving `3.9` reference in the top-level README.
- `pyproject.toml`'s `[tool.ruff.lint] ignore` list `UP035`/`UP006` trailing comments now read `(Python 3.10+ support)` — rule codes and every other ignore entry left untouched.
- Confirmed the comment-only pyproject.toml change is functionally inert: `black --check .` (via `uv run tox -e lint`) reports 50 files unchanged; `ruff check .` (via the NixOS `nix run nixpkgs#ruff` local-execution workaround established in 04-01) reports "All checks passed!".

## Task Commits

Each task was committed atomically:

1. **Task 1: Update the two README Python-version references to 3.10** - `6ce9889` (docs)
2. **Task 2: Update the ruff UP035/UP006 comment text in pyproject.toml** - `62b01e7` (docs)

**Plan metadata:** (this commit, following)

_Note: Both tasks were pure text/comment edits — no test-first (TDD) cycle applicable._

## Files Created/Modified
- `README.md` - Requirements bullet (line 36) and version footer (line 323) updated from Python 3.9 to 3.10
- `pyproject.toml` - Ruff `UP035`/`UP006` ignore-list comment text updated from "Python 3.9+ support" to "Python 3.10+ support" (lines 111-112)

## Decisions Made
None - plan executed exactly as specified in 04-CONTEXT.md D-04 and 04-PATTERNS.md's target-state excerpts.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched the plan's stated current-state exactly (verified via `sed`/`grep` before editing), and the edits landed byte-for-byte as specified in `<artifacts_produced>`.

## Issues Encountered

**NixOS cannot execute the uv-installed `ruff` binary directly** (pre-existing local-machine limitation, not introduced by this plan): `uv run tox -e lint`'s `ruff check .` step fails with `Could not start dynamically linked executable` because NixOS refuses generic-glibc dynamically-linked ELFs without `nix-ld`/`stub-ld`. This is the identical issue documented in Phase 3 (`03-02-SUMMARY.md`) and Phase 4 Plan 01 (`04-01-SUMMARY.md`). Resolved by reusing the established workaround verbatim: ran `nix run nixpkgs#ruff -- check .` (nixpkgs ruff 0.15.14, still within this repo's `>=0.15,<0.16` floor+ceiling) instead of the uv-managed binary for the local pre-check. `black --check .` (pure-Python, no binary-execution issue) ran fine unmodified via `uv run tox -e lint`. GitHub Actions runners (not NixOS) will execute the uv-locked ruff 0.15.20 exactly, so this local substitution has no effect on the CI-executed version. No code change was required — this is an environment note, not a deviation from the plan's file edits.

## Out-of-Scope Findings (not fixed, logged only)

A repo-wide `grep -rn "3\.9"` scan (run to satisfy the orchestrator's "verify no other stray 3.9 references remain" success criterion) found stray `Python 3.9` current-tense claims outside this plan's `files_modified` scope (`README.md`, `pyproject.toml` only):
- `examples/basic/README.md:7` — `- Python 3.9 or higher`
- `examples/advanced/README.md:30` — `- Python 3.9 or higher`

These are pre-existing, unrelated to this plan's two-file scope (Rule out-of-scope boundary: only auto-fix issues directly caused by the current task's changes). Not fixed here; flagged as a candidate follow-up if a future phase wants full repo-wide 3.9-reference parity.

Additionally, `CHANGELOG.md` contains historical `3.9` references (lines 383, 424, 512) describing past release version support (e.g., "Python 3.9, 3.10, 3.11, 3.12" for an older release entry). These are correctly left untouched — they are historical record, not a current documented requirement, and rewriting past changelog entries would misrepresent release history.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All three D-04 stale-3.9 text strings resolved; README and pyproject.toml now fully consistent with the Phase 3 3.10 floor.
- These two commits are ready to be folded into the same tooling PR as 04-01/04-02 per D-06 (per-surface commits within a single PR) — no PR has been opened yet by this plan; that is 04-04's push-and-observe gate.
- No blockers for 04-04.

---
*Phase: 04-refresh-dev-tooling*
*Completed: 2026-07-04*

## Self-Check: PASSED

- FOUND: 04-03-SUMMARY.md
- FOUND: 6ce9889 (Task 1 commit)
- FOUND: 62b01e7 (Task 2 commit)
- FOUND: 2878135 (SUMMARY.md commit)
