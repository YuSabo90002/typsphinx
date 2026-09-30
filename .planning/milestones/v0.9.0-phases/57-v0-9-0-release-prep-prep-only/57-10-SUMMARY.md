---
phase: 57-v0-9-0-release-prep-prep-only
plan: 10
subsystem: testing
tags: [pytest, windows, path-separator, ci, cross-platform]

# Dependency graph
requires:
  - phase: 57-v0-9-0-release-prep-prep-only (plan 57-02)
    provides: "CI run 31956166848 (D-12 pre-bump check run) that discovered the Windows-only path-separator defect this plan fixes, and WINDOWS.md ledger entry 9 filing it"
provides:
  - "tests/test_templates_path_collision_gate.py's resolved-path assertion made separator-portable (Path-based, not a hardcoded forward slash)"
  - "57-WINDOWS-FIX-EVIDENCE.md: cited pre-fix RED (CI run 31956166848, re-read live), whole-file classification sweep, the diff, and the post-fix local green transcript"
  - "WINDOWS.md entry 9 transitioned from bare-open to open-with-fix-landed, pointing at 57-05 for Windows-lane confirmation"
affects: [57-05]

# Actuals (#2632)
actuals:
  tokens: 7425
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-WINDOWS-FIX-EVIDENCE.md
  modified:
    - tests/test_templates_path_collision_gate.py
    - .planning/WINDOWS.md

key-decisions:
  - "The sweep was property-driven (every slash-bearing string literal in the whole file), not line-number-driven -- CI named only line 255, but the full-file grep found exactly one other slash-bearing assertion ('_typst/inner') and classified it config-echoed, correctly left untouched with an explanatory comment."
  - "WINDOWS.md entry 9's status stays 'open' rather than being flipped to 'fixed' -- this defect is Windows-only and cannot be locally re-verified, so the ship gate should keep blocking until plan 57-05's post-bump authority dispatch actually confirms the fix on windows-latest. The entry's description was updated instead, so it no longer reads as an untouched defect while the machine-readable gate state stays honest."

patterns-established: []

requirements-completed: [REL-08]

coverage:
  - id: D1
    description: "tests/test_templates_path_collision_gate.py's beta-bundle-directory assertion builds its expected substring with pathlib.Path(...) instead of a hardcoded '_templates/nested' literal, so it holds on both POSIX and Windows separators"
    requirement: REL-08
    verification:
      - kind: unit
        ref: "tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry"
        status: pass
      - kind: unit
        ref: "uv run python -m pytest -q (full suite, 1417 passed / 5 skipped / 0 failed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "57-WINDOWS-FIX-EVIDENCE.md cites CI run 31956166848 as the pre-fix RED (re-read live via gh run view, headSha and both failing windows-latest job names confirmed), records the whole-file classification sweep, and explicitly declines to claim a green Windows lane"
    requirement: REL-08
    verification:
      - kind: other
        ref: ".planning/phases/57-v0-9-0-release-prep-prep-only/57-WINDOWS-FIX-EVIDENCE.md (live gh run view 31956166848 re-read, this plan)"
        status: pass
    human_judgment: false
  - id: D3
    description: "WINDOWS.md entry 9 is neither left at bare-open nor prematurely marked fixed/verified -- its description now records the fix landing and points at 57-05 for confirmation"
    requirement: REL-08
    verification:
      - kind: other
        ref: "grep -q 57-10 .planning/WINDOWS.md; gsd-tools windows status (ledger parses, counts consistent, entry 9 status still open)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-17
status: complete
---

# Phase 57 Plan 10: Windows Path-Separator Test Fix Summary

**Made `tests/test_templates_path_collision_gate.py`'s beta-bundle-directory assertion separator-portable via `pathlib.Path`, clearing the one Windows-lane failure (both `windows-latest` py3.12/py3.13) that CI run `31956166848` recorded against the untouched phase-head commit, while leaving the sibling config-echoed assertion untouched by design.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-17
- **Tasks:** 2
- **Files modified:** 3 (1 test file fixed, 1 evidence file created, 1 ledger updated)

## Accomplishments

- Swept the whole file by property (every slash-bearing assertion), not by the single line number CI named — found exactly two candidates: beta's resolved bundle directory (`'_templates/nested'`, resolved-path, needs fixing) and gamma's colliding `templates_path` entry (`'_typst/inner'`, config-echoed, must stay a literal forward slash).
- Fixed the resolved-path assertion to build its expected substring with `str(Path("_templates") / "nested")`, so it holds on both POSIX and Windows separators instead of hardcoding POSIX.
- Left the config-echoed assertion (`'_typst/inner'`) unchanged, adding a comment explaining why — it is a `templates_path` config value echoed verbatim from the fixture's `conf.py`, not a resolved filesystem path.
- Re-read CI run `31956166848` live (`gh run view --json headSha,conclusion,jobs` and `--log-failed`), confirming `headSha` matches commit `78bd595d`, exactly two jobs failed (`Test Python 3.13 on windows-latest`, `Test Python 3.12 on windows-latest`), and pasting the verbatim `AssertionError` excerpt into the evidence file. No local RED transcript was fabricated — this defect is Windows-only and cannot reproduce on this Linux host.
- Ran the target file (12/12 pass) and the full local suite (1417 passed, 5 skipped, 0 failed — matching the wave-1 post-merge baseline exactly, no regression) after the fix.
- Transitioned `WINDOWS.md` entry 9's description to record the fix landing in plan 57-10, while deliberately keeping its `status` at `open` (not `fixed`) so the ship gate stays blocked until plan 57-05's post-bump authority CI dispatch actually confirms the fix on a real Windows lane.

## Task Commits

Each task was committed atomically:

1. **Task 1: Classify every slash-bearing assertion, then make the resolved-path one separator-portable** - `a7185a13` (fix)
2. **Task 2: Record the cited RED, the local green, and transition the WINDOWS.md ledger** - `e6430c2f` (docs)

**Plan metadata:** not applicable — this is a worktree-isolated executor; the orchestrator commits shared STATE.md/ROADMAP.md updates after the wave merges.

## Files Created/Modified

- `tests/test_templates_path_collision_gate.py` - The beta-bundle-directory assertion now builds its expected substring with `pathlib.Path("_templates") / "nested"` instead of a hardcoded `'_templates/nested'` literal; the sibling `'_typst/inner'` assertion is unchanged with an explanatory comment pinning it as config-echoed.
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-WINDOWS-FIX-EVIDENCE.md` - New file. Carries the cited pre-fix RED (CI run `31956166848`, re-read live), the full classification sweep table, the diff, the post-fix full local suite transcript, and an explicit "What this plan does NOT claim" section (no green Windows lane observed — that's 57-05's job).
- `.planning/WINDOWS.md` - Entry 9's description updated to record the fix landing in plan 57-10 and point at plan 57-05 for Windows-lane confirmation; `status` deliberately left `open` (counts unchanged: `open_count: 2`).

## Decisions Made

- **Property-driven sweep, not line-number-driven.** CI's `AssertionError` named line 255, but the search set was every slash-bearing string literal in the whole 387-line file. This found the sibling `'_typst/inner'` assertion and confirmed — by re-checking against the live CI log excerpt, which shows that entry's name portion keeps its internal forward slash even inside the Windows-resolved path — that it is config-echoed and must NOT be touched.
- **`WINDOWS.md` entry 9 stays `status: open`.** The ledger's schema supports only `open` / `waived` / `fixed`, and this defect is genuinely unverifiable from this Linux host. Marking it `fixed` would let `/gsd-ship`'s `windows_enforce` gate treat the defect as resolved before any Windows CI run has actually confirmed it — an overclaim this plan's own `must_haves.truths` explicitly forbids ("The GREEN proof is delegated to plan 57-05's post-bump authority dispatch; this plan does not claim a green Windows lane it has not seen"). The entry's description was enriched instead, so a reader sees the fix landed and where confirmation is pending, without prematurely unblocking the gate.

## Deviations from Plan

None — plan executed exactly as written. The classification sweep found exactly the two assertions the plan's `must_haves.truths` anticipated (one resolved-path, one config-echoed); no additional resolved-path assertion was discovered.

## Issues Encountered

None. `env -u VAR uv sync` and `env -u VAR -u VAR2 uv sync` were both rejected by this sandbox as "too complex to verify"; worked around with `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev` in a separate command, which achieves the same per-worktree isolation this project's `CLAUDE.md` requires (confirmed: `typsphinx==0.9.0` installed from this worktree's own path, not the main checkout).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The one Windows-lane failure standing between this milestone and a green post-bump authority CI run is fixed on the test side; `typsphinx/` and `.github/` remain untouched (`git diff --name-only -- typsphinx/ .github/` empty at plan end).
- **57-05 still owns the actual Windows-lane confirmation.** This plan explicitly does not claim a green Windows lane — `WINDOWS.md` entry 9 stays `open` until 57-05's post-bump authority dispatch (`gh run view "$RUN_ID_2" --json jobs --jq '[.jobs[].conclusion]|unique|join(",")'` == `success`) actually proves it on `windows-latest`.
- No irreversible action was taken: `git tag -l v0.9.0` and `git ls-remote --tags origin v0.9.0` both produce no output.

## Self-Check: PASSED

- FOUND: `tests/test_templates_path_collision_gate.py` (modified, 12/12 tests pass)
- FOUND: `.planning/phases/57-v0-9-0-release-prep-prep-only/57-WINDOWS-FIX-EVIDENCE.md`
- FOUND: `.planning/WINDOWS.md` (entry 9 updated, ledger parses via `gsd-tools windows status`)
- FOUND commit: `a7185a13` (task 1 fix)
- FOUND commit: `e6430c2f` (task 2 evidence + ledger)

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-17*
