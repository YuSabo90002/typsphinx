---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 01
subsystem: docs
tags: [claude-md, typing, ruff, doc-22]

# Dependency graph
requires: []
provides:
  - "CLAUDE.md:75 rewritten to an annotation-style instruction (builtin generics + collections.abc), with no flip-dependent claim"
  - "70-DOC22-EVIDENCE.md recording BASE_70_01, the before/after diff, D-04 lint/test neutrality, the pending-path census, and a two-sided (pre-flip/post-flip) reading against D-01..D-03"
affects: [70-04, 70-05, 70-06, 70-07, 70-08, 70-09, 70-10]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 2326
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CLAUDE.md rewrite confined to a single bullet, verified by masking the rest of the file (sed '75d' hash-equal to base) rather than reviewing the whole diff by eye"

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOC22-EVIDENCE.md
  modified:
    - CLAUDE.md

key-decisions:
  - "Wording of the rewritten bullet (Claude's discretion within D-01..D-03): kept the Python-floor sentence, added one instruction naming builtin generics and collections.abc.Iterator, dropped every ruff-state/history/todo-path claim, added no __future__/PEP 604 rule."

patterns-established: []

requirements-completed: [DOC-22]

coverage:
  - id: D1
    description: "CLAUDE.md:75 rewritten so it states the annotation-style instruction (D-01), carries no flip-dependent claim (D-02), no __future__/PEP 604 prohibition (D-03), and is the only line changed in the file (D-04), landed in a commit touching only CLAUDE.md"
    requirement: DOC-22
    verification:
      - kind: other
        ref: "Task 1 <verify><automated> — grep/token/hash/commit-count assertions in 70-DOC22-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "70-DOC22-EVIDENCE.md records D-04's lint/test neutrality (ruff, black, and the CLAUDE-mentioning pytest files all exit 0), the pending-path census (one citation after this plan vs. two at BASE_70_01), and a prose reading of the bullet against D-01..D-03 for both the pre-flip and post-flip state"
    requirement: DOC-22
    verification:
      - kind: other
        ref: "Task 2 <verify><automated> — pytest/ruff/black exit codes, git grep counts, and section-presence checks in 70-DOC22-EVIDENCE.md"
        status: pass
    human_judgment: true
    rationale: "The 'Reading against D-01..D-03' section is a prose classification (does the bullet read true on both sides of the flip) that the automated checks support but do not themselves adjudicate; 70-10 re-verifies this reading mechanically at the pre-flip and post-flip commits."

duration: 25min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 01: DOC-22 CLAUDE.md Rewrite Summary

**Rewrote `CLAUDE.md:75` from a ruff-deferral notice into a standing annotation-style instruction (builtin generics + `collections.abc`), landed alone ahead of every conversion plan, with evidence proving it lint-neutral, test-neutral, and true on both sides of the coming ignore-flip.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-13T04:00:00Z (approx.)
- **Completed:** 2026-09-13T04:27:02Z
- **Tasks:** 2
- **Files modified:** 2 (1 modified, 1 created)

## Accomplishments
- `CLAUDE.md:75` now instructs contributors to use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and `collections.abc` for abstract types like `Iterator`, instead of `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator` — with no claim about ruff's current ignore state, no history note, and no `__future__`/PEP 604 prohibition (D-01, D-02, D-03).
- The rewrite is the only change to `CLAUDE.md`: `sed '75d'` of the file hashes identically to the base, the line count is unchanged, and exactly one commit in this plan touches `CLAUDE.md` (D-04).
- `70-DOC22-EVIDENCE.md` records the before/after bullet text, the one-line diff, `BASE_70_01`, the D-04 lint/test-neutrality run (ruff, black, and the CLAUDE-mentioning pytest files all pass), the pending-todo-path census (one citation left, in `pyproject.toml`, versus two at the base), and a two-sided prose reading showing the bullet is true both before and after the 70-09 ignore-flip.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: rewrite the CLAUDE.md:75 bullet to D-01's annotation-style instruction and commit it alone** - `3c5e281c` (docs)
2. **Task 2: Record D-04's lint and test neutrality, the pending-path census and the two-sided reading, then commit the evidence** - `14837ce2` (docs)

_Note: this plan carries no `tdd="true"` tasks, so each task is a single commit._

## Files Created/Modified
- `CLAUDE.md` - line 75 rewritten from a ruff-deferral notice to an annotation-style instruction
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOC22-EVIDENCE.md` - before/after transcript, D-04 neutrality run, pending-path census, two-sided D-01..D-03 reading

## Decisions Made
- The exact wording of the rewritten bullet was left to Claude's discretion (per CONTEXT.md), within the bounds of D-01 (keep the Python-floor fact, add the annotation-style instruction), D-02 (no flip-dependent claim, no history, no todo path) and D-03 (no `__future__`/PEP 604 prohibition). The wording chosen matches the shape recommended in `70-PATTERNS.md` § `CLAUDE.md:75`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `CLAUDE.md:75` is now merged (in this worktree branch) and ready to be the base every wave 2-3 conversion executor forks from, per ROADMAP constraint 1(i).
- `70-DOC22-EVIDENCE.md`'s `BASE_70_01` and pending-path census give 70-09 (the ignore-flip plan) the "one citation left, in pyproject.toml" fact it needs to confirm the todo-move-with-flip constraint (constraint 2).
- No blockers. This plan touched only `CLAUDE.md` and its own evidence file, per the plan's declared `files_modified` and the orchestrator's scope note.

## Self-Check: PASSED

- `test -f CLAUDE.md` → FOUND
- `test -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOC22-EVIDENCE.md` → FOUND
- `git log --oneline --all | grep -q 3c5e281c` → FOUND
- `git log --oneline --all | grep -q 14837ce2` → FOUND
- Re-ran both tasks' `<verify><automated>` blocks: both printed their `_VERIFY_PASSED` sentinel with exit 0.
- Re-ran the plan-level `<verification>`: CLAUDE.md:75 carries the D-01 instruction and no D-02/D-03 content, the rest of the file is byte-identical, and the rewrite is a single commit touching only CLAUDE.md.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
