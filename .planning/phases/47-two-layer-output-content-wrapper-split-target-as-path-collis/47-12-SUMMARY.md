---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 12
subsystem: writer
tags: [dead-code-deletion, requirements-bookkeeping, pytest, black, ruff, mypy]

# Dependency graph
requires:
  - phase: 47-10
    provides: Phase 47 fully closed (10 plans executed), verification found 2 gaps (BLD-02, BLD-03) plus WR-01 dead-code finding
provides:
  - "typsphinx/writer.py with exactly one entry-element resolution route (_entry_element_value()); the superseded docname-first-match _resolve_entry_element() is gone"
  - "tests/test_entry_metadata_precedence.py retargeted onto the live resolver, with the four D-08-rejected assertions deleted and their rationale recorded in the module docstring"
  - ".planning/REQUIREMENTS.md with COMP-01..04, OUT-01, OUT-03 correctly checked (8/10 Phase 47 requirements now [x]; BLD-02/BLD-03 still open pending re-verification)"
affects: [48-cross-reference-guard, 49-per-master-include-graph]

actuals:
  tokens: 6200
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Dead-code deletion over retention-with-docstring: a superseded implementation with zero production call sites is deleted, not annotated, because a green test suite over an unreachable code path reports false confidence (WR-01 disposition)."
    - "Bookkeeping-tool fallback: when gsd-tools.cjs is unreachable from a worktree, the plan's mandated direct-edit fallback is taken and the mechanism used is recorded in the SUMMARY, with acceptance criteria identical under either route."

key-files:
  created: []
  modified:
    - typsphinx/writer.py
    - tests/test_entry_metadata_precedence.py
    - tests/test_document_metadata_render_gate.py
    - tests/fixtures/entry_title_author_render_gate/conf.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "DELETE, not retain-with-docstring: _resolve_entry_element() removed entirely from typsphinx/writer.py per the plan's locked decision — D-08 already made it a superseded implementation with no future consumer, and CONF-13 (per-entry template keys) reinforces the positional-per-entry route rather than reviving a docname search."
  - "Fixed a stray stale reference the plan's <read_first> list did not name: tests/fixtures/entry_title_author_render_gate/conf.py's comment presented _resolve_entry_element() as a still-existing (merely unused) helper. Corrected under Rule 1 (directly caused by this task's deletion, in scope of must_haves truth #4's tracked-tree-wide prohibition) even though the file is not in the plan's files_modified list."
  - "Task 2 mechanism: direct edit, not gsd-tools.cjs. Resolution was attempted in order (RUNTIME_DIR/.claude/.codex gsd-core paths, PATH) and none resolved from this worktree — the worktree has no .claude/ directory at all — so the plan's mandated fallback was taken. Acceptance criteria are identical under either route and all passed."

requirements-completed: [COMP-01, COMP-02, COMP-03, COMP-04, OUT-01, OUT-03]
# NOTE: the plan's own frontmatter lists `requirements: [BLD-02, BLD-03]`, but
# the plan's action and prohibitions explicitly forbid checking those two off
# here -- they require /gsd-verify-phase 47 re-measurement first (must_haves
# truth #5, prohibitions). The six IDs actually flipped to [x] in this plan's
# Task 2 are listed above instead; BLD-02/BLD-03 stay open by design.

coverage:
  - id: D1
    description: "The superseded docname-first-match entry resolver (_resolve_entry_element) is deleted from typsphinx/writer.py; render_wrapper()'s _entry_element_value() is the sole production entry-element resolution route"
    verification:
      - kind: unit
        ref: "grep -rc '_resolve_entry_element' typsphinx/ (0 matches, all files)"
        status: pass
      - kind: unit
        ref: "python -c \"import typsphinx.writer as w; hasattr(w, '_resolve_entry_element')\" -> False"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every entry-element semantic that survives D-08 is retargeted onto _entry_element_value() in tests/test_entry_metadata_precedence.py; the four D-08-rejected assertions are deleted with rationale recorded in the module docstring"
    verification:
      - kind: unit
        ref: "tests/test_entry_metadata_precedence.py (23 collected, 27 pre-task minus 4 deletions)"
        status: pass
    human_judgment: false
  - id: D3
    description: "No tracked docstring/comment/test prose still presents the deleted resolver as live code (writer.py, both test modules, and the entry_title_author_render_gate fixture)"
    verification:
      - kind: unit
        ref: "manual grep review of all 4 modified prose sites; historical references now name 47-12-PLAN.md as the removal point"
        status: pass
    human_judgment: false
  - id: D4
    description: ".planning/REQUIREMENTS.md's six genuinely-satisfied checkboxes (COMP-01..04, OUT-01, OUT-03) flip to [x] with matching phase-mapping rows; BLD-02/BLD-03 stay [ ]/Pending"
    verification:
      - kind: unit
        ref: "grep acceptance criteria (Task 2 <acceptance_criteria>) — all 5 checks pass"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full suite, black --check, ruff check, and mypy typsphinx/ all green (binding constraint #8)"
    verification:
      - kind: unit
        ref: "uv run pytest -q -> 1023 passed, 5 skipped; uv run black --check . -> clean; nix-shell -p ruff --run 'ruff check .' -> All checks passed; uv run mypy typsphinx/ -> Success"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 12: Dead-Code Deletion and Requirement Bookkeeping Closure Summary

**Deleted the superseded docname-first-match `_resolve_entry_element()` from `typsphinx/writer.py`, retargeted its surviving test coverage onto the live `_entry_element_value()` resolver, and corrected six stale requirement checkboxes in `REQUIREMENTS.md` (COMP-01..04, OUT-01, OUT-03) that worktree executors could not check off.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-11 (worktree provisioning + task 1)
- **Completed:** 2026-08-11T22:57:16Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- `typsphinx/writer.py::_resolve_entry_element()` — a fully-documented, extensively-tested function with **zero production call sites** — is gone. `render_wrapper()`'s `_entry_element_value()` is now the sole entry-element resolution route in the package.
- `tests/test_entry_metadata_precedence.py` Group 1 retargeted: 9 of 13 original tests converted from the deleted resolver's `(typst_documents, docname, index, default)` docname-search form to the survivor's `(entry, index, default)` positional form; 4 tests whose semantic existed only in the docname-search route (which D-08 forbids for wrappers) were deleted, with the rationale for each recorded in the module docstring. Net: 27 -> 23 collected tests, exactly 4 lower.
- Two stale docstring passages in `tests/test_document_metadata_render_gate.py` corrected to name the mechanism that actually resolves entry metadata today (`_entry_element_value()`, called by `render_wrapper()`) and to read the deleted resolver's mention as history, naming this plan as the removal point.
- `.planning/REQUIREMENTS.md`'s six genuinely-satisfied checkboxes flipped from `[ ]` to `[x]` (both the v1 list and the phase-mapping table), with `BLD-02`/`BLD-03` deliberately left open pending `/gsd-verify-phase 47` re-measurement.
- Full suite (1023 passed / 5 skipped / 0 failed), `black --check .`, `ruff check .` (via `nix-shell -p ruff` fallback — the uv-managed ruff binary is a generic-linux ELF unrunnable on NixOS, a pre-existing documented limitation), and `mypy typsphinx/` all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete the superseded entry-element resolver and retarget its surviving coverage** - `71fed7a` (feat)
2. **Task 2: Correct the six stale requirement checkboxes in REQUIREMENTS.md** - `bb82f66` (docs)

_No plan-metadata commit from this executor — worktree mode; the orchestrator makes the shared-file/final metadata commit after merge._

## Files Created/Modified

- `typsphinx/writer.py` - Deleted `_resolve_entry_element()` (function + docstring); repaired `_entry_element_value()`'s own docstring, which used to contrast itself against the deleted function; corrected the `render_wrapper()` inline comment that named the deleted function
- `tests/test_entry_metadata_precedence.py` - Retargeted 9 Group-1 tests onto `_entry_element_value()`; deleted 4 tests whose semantic was docname-search-only; corrected the module import (`_entry_element_value` instead of `_resolve_entry_element`); rewrote the module docstring to record the four deletions and their rationale; Groups 2 and 3 left byte-identical (verified via `git diff -U0` boundary check)
- `tests/test_document_metadata_render_gate.py` - Corrected the module-header "Fix:" passage and the mid-module contrast passage so neither presents the deleted resolver as live code
- `tests/fixtures/entry_title_author_render_gate/conf.py` - Corrected a comment (not in the plan's `files_modified` list) that presented the deleted resolver as a still-existing, merely-unused helper — a direct casualty of the deletion, fixed under Rule 1
- `.planning/REQUIREMENTS.md` - Flipped `COMP-01`, `COMP-02`, `COMP-03`, `COMP-04`, `OUT-01`, `OUT-03` from `[ ]` to `[x]` in both the v1 checkbox list and the phase-mapping table; `BLD-02`/`BLD-03` left `[ ]`/`Pending`; `OUT-02`/`BLD-04` untouched (already `[x]`/`Complete`); coverage tally line (`24 total`) unchanged

## Decisions Made

- **DELETE over retention-with-docstring** (locked in the plan, executed here): `_resolve_entry_element()` removed entirely rather than kept as a documented-but-dead function. D-08 had already demoted it and CONF-13 (a future milestone) reinforces the positional-per-entry route, so there is no future consumer to preserve it for.
- **Fixed an out-of-plan-scope stale reference**: `tests/fixtures/entry_title_author_render_gate/conf.py`'s comment named `_resolve_entry_element()` as a live-but-unused helper. This file was not in the plan's `files_modified` frontmatter or Task 1's `<files>` list, but must_haves truth #4 ("no docstring, comment or test prose in the tracked tree still names the deleted resolver as a live mechanism") is phrased tree-wide, not file-scoped, and the falsehood was a direct, mechanical consequence of the deletion. Fixed under deviation Rule 1.
- **Task 2 mechanism: direct edit** (plan's mandated fallback). `gsd-tools.cjs` was not resolvable from this worktree — no `.claude/` directory exists under the worktree root at all, and `gsd-tools` is not on `PATH` — so the checkbox and table-row edits were made directly with the Edit tool. All Task 2 acceptance criteria pass identically to the tool route.
- **ruff via `nix-shell -p ruff` fallback**: `uv run ruff check .` fails on this NixOS environment because the uv-managed ruff wheel is a generic-linux ELF (the pre-existing, project-acknowledged `ruff-generic-linux-elf-unrunnable-on-nixos` deferred item in `STATE.md`). Ran `nix-shell -p ruff --run "ruff check ."` instead, which passed clean, to discharge binding constraint #8 without leaving lint unverified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected a stale `_resolve_entry_element()` reference in a test fixture not named by the plan**
- **Found during:** Task 1 (deleting the resolver and sweeping for stale references)
- **Issue:** `tests/fixtures/entry_title_author_render_gate/conf.py`'s comment read "...never through the docname first-match `_resolve_entry_element()` helper..." — phrasing that presents the deleted function as a still-existing alternative route, which is exactly what must_haves truth #4 prohibits tree-wide. Not in the plan's `<read_first>` inventory or `files_modified` list.
- **Fix:** Reworded the comment to describe the docname first-match search generically, then name `_resolve_entry_element()` only as history — the function that named that scan before 47-12-PLAN.md deleted it.
- **Files modified:** `tests/fixtures/entry_title_author_render_gate/conf.py`
- **Verification:** `grep -rln '_resolve_entry_element' .` re-run after the fix; the fixture no longer implies the function exists as a live mechanism. Full suite re-run green (this fixture backs a real `sphinx-build -b typstpdf` gate in `tests/test_document_metadata_render_gate.py`, unaffected).
- **Committed in:** `71fed7a` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug, stale prose directly caused by this task's deletion)
**Impact on plan:** No scope creep — the fix is a direct, mechanical consequence of Task 1's own action, required to satisfy the plan's own must_haves truth #4 in full.

## Issues Encountered

- `uv run ruff check .` cannot execute in this worktree's NixOS sandbox (`Could not start dynamically linked executable: ruff`) — a pre-existing, documented environmental limitation (`STATE.md` Deferred Items: `ruff-generic-linux-elf-unrunnable-on-nixos`), unrelated to this plan's changes. Worked around with `nix-shell -p ruff --run "ruff check ."`, which ran the same lint rules against nixpkgs' own ruff build and passed clean, so binding constraint #8 is still fully discharged rather than left unverified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- WR-01 has a concrete disposition on disk: the dead resolver is gone, not annotated, and no test in the suite can report confidence in a code path no build executes.
- `.planning/REQUIREMENTS.md` now tells the truth about Phase 47: 8/10 requirements `[x]`, with `BLD-02` and `BLD-03` still visibly open — these are the two IDs that require `47-11`'s collision-key/self-collision code (already landed per `47-VERIFICATION.md`/`47-REVIEW.md` context) to be re-verified by `/gsd-verify-phase 47` before they can be checked.
- No blockers for the next phase. This plan touched no runtime behavior — Task 1 removed unreachable code and retargeted its tests; Task 2 edited a planning document — so nothing here changes Phase 48's starting state.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
