---
phase: 260720-p2w
plan: 01
subsystem: docs
tags: [worktree, uv, editable-install, ci-guidance]

requires: []
provides:
  - "CLAUDE.md documents how a gsd-executor provisions its own venv when running inside an isolated git worktree"
affects: [future phases run with workflow.use_worktrees enabled]

tech-stack:
  added: []
  patterns:
    - "Worktree detection via `.git` being a file (gitdir pointer) vs. a directory"

key-files:
  created: []
  modified: [CLAUDE.md]

key-decisions:
  - "Documented as a new `### Worktree-isolated execution` subsection at the end of `## Conventions & gotchas`, matching the file's existing `###`-subsection style"

patterns-established:
  - "Worktree executors must run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then use `uv run` for all commands, to avoid the PEP-660 editable finder binding imports to the main checkout"

requirements-completed: [QUICK-260720-p2w]

coverage:
  - id: D1
    description: "CLAUDE.md gains a 'Worktree-isolated execution' subsection with detection rule, both exact commands, and PEP-660 rationale"
    requirement: "QUICK-260720-p2w"
    verification:
      - kind: other
        ref: "grep -q 'uv sync --extra dev' CLAUDE.md && grep -q 'VIRTUAL_ENV' CLAUDE.md && grep -q 'worktree' CLAUDE.md && grep -q 'uv run' CLAUDE.md && grep -q 'Worktree-isolated execution' CLAUDE.md"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-20
status: complete
---

# Quick Task 260720-p2w: Worktree-isolated execution guidance Summary

**Added a "Worktree-isolated execution" subsection to CLAUDE.md documenting the `.git`-is-a-file detection rule, the required `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run` provisioning steps, and the PEP-660 editable-finder rationale.**

## Performance

- **Duration:** ~5 min
- **Tasks:** 1 completed
- **Files modified:** 1 (CLAUDE.md)

## Accomplishments
- Added `### Worktree-isolated execution` subsection at the end of `## Conventions & gotchas` in `CLAUDE.md`, matching the existing `###`-subsection style (e.g. "The `@preview` version-sync hazard")
- Documented the detection rule: `.git` is a FILE (gitdir pointer), checkable via `test -f .git`
- Documented both required steps verbatim: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and running all commands via `uv run`
- Explained the rationale: the main `.venv`'s PEP-660 editable finder (`__editable__.typsphinx-*.pth`) resolves `import typsphinx` to the main checkout's absolute path, and `.venv` is gitignored, so a fresh worktree needs its own venv or pytest silently imports the unchanged main-tree package
- Noted applicability: currently moot since `workflow.use_worktrees` is `false`; relevant when worktrees are re-enabled for parallel-wave phases

## Task Commits

1. **Task 1: Add "Worktree-isolated execution" subsection to CLAUDE.md** - `cc21f47` (docs)

_No plan-metadata commit — quick-task orchestrator handles the docs commit separately per task constraints._

## Files Created/Modified
- `CLAUDE.md` - Added `### Worktree-isolated execution` subsection documenting detection rule, provisioning commands, and PEP-660 rationale

## Decisions Made
- Placed the new subsection at the end of `## Conventions & gotchas` (immediately after the CI bullet) rather than creating a new top-level section, to match the plan's instruction and the file's existing structural convention.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

CLAUDE.md now has durable guidance for any future gsd-executor running under `workflow.use_worktrees: true`; no code or config changed, so this has no effect until worktrees are re-enabled.

---
*Phase: 260720-p2w*
*Completed: 2026-07-20*
