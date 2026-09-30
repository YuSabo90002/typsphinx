---
phase: 53-template-registry-foundation
plan: 04
subsystem: template-engine
tags: [sphinx, typst, template-engine, dataclass, TDD]

# Dependency graph
requires:
  - phase: 53-02
    provides: "typsphinx/template_registry.py, resolve_template_registry(), the registry threaded through write() and render_wrapper()"
provides:
  - "TemplateResolution.path: Path | None -- the resolved template's own file path, populated at all three resolve_template() priorities"
affects: ["53-05 (release-prep evidence)", "Phase 54 (bundle copy needs the resolved parent directory this field exposes)"]

# Actuals (#2632)
actuals:
  tokens: 1528
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Widen a frozen dataclass in place at its own construction sites rather than adding a second, independently-written lookup method (CONF-07/D-06 single-priority-walk invariant)"

key-files:
  created: []
  modified:
    - typsphinx/template_engine.py
    - tests/test_template_engine.py

key-decisions:
  - "Field docstring states the Optional typing is for a hypothetical future caller that resolves no file at all -- no branch inside resolve_template() itself ever produces None for this field, matching RESEARCH.md Q2's own reasoning verbatim."
  - "Task 2 made no code change of its own (a confirm-only task); its measured values are recorded below and its own commit is this SUMMARY.md's commit, mirroring the 53-02 plan's Task 3 precedent."

requirements-completed: [TPL-03]

coverage:
  - id: D1
    description: "TemplateResolution carries a fourth field, path: Path | None, populated inline at Priority 1 (explicit template_path), Priority 2 (search_paths candidate), and Priority 3 (bundled default) -- through the same single priority walk, no resolve_template_path() method added"
    requirement: TPL-03
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTemplateResolutionProvenance::test_resolve_template_explicit_path"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTemplateResolutionProvenance::test_resolve_template_search_path"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTemplateResolutionProvenance::test_resolve_template_default_path"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTemplateResolutionProvenance::test_resolve_template_fallthrough_path_is_never_the_missing_path"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTemplateResolutionProvenance::test_resolve_template_path_parent_directory_obtainable_at_every_priority"
        status: pass
    human_judgment: false
  - id: D2
    description: "The widening is output-neutral (full suite failure set unchanged from the pre-existing 7-test baseline), dependency-neutral (pyproject.toml diff empty), and adds no fourth @preview version-lockstep site (test_preview_version_sync.py green, _template.typ-asserting file count unchanged at 32)"
    requirement: TPL-03
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -- 1179 passed, 7 pre-existing failures (test_state_guard_shapes_gate.py baseline, unrelated FileNotFoundError), 5 skipped"
        status: pass
      - kind: unit
        ref: "uv run pytest tests/test_preview_version_sync.py -q -- 3 passed"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 04: Widen TemplateResolution With the Resolved Path Summary

**`TemplateResolution` gained a third field, `path: Path | None`, populated inline at all three of `resolve_template()`'s existing priority branches -- through the same single priority walk, with zero output change and zero new `@preview` lockstep site -- giving Phase 54's future bundle copy the resolved template's parent directory it cannot get today.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-15
- **Tasks:** 2/2
- **Files modified:** 2 (`typsphinx/template_engine.py`, `tests/test_template_engine.py`)

## Accomplishments

- Added `path: Path | None` to the frozen `TemplateResolution` dataclass, with a docstring
  explaining what it holds at each priority and why the type stays `Optional` (no branch inside
  `resolve_template()` itself ever produces `None`; the annotation is reserved for a hypothetical
  future caller that resolves no file at all).
- Populated the field inline at all three existing `TemplateResolution(...)` construction sites
  inside `resolve_template()`: `Path(self.template_path)` at Priority 1, the already-computed
  `candidate_path` at Priority 2, and `Path(default_path)` at Priority 3. `resolve_template()`
  remains the single priority walk -- no `resolve_template_path()` method was added, and the
  Priority-1 warn-and-fall-back at lines 308-315 is byte-for-byte unchanged (D-08).
- Wrote five additive assertions in the existing `TestTemplateResolutionProvenance` class covering
  each priority, the fall-through case (a missing explicit path never reports its own missing
  path), and parent-directory obtainability at every priority -- the exact capability Phase 54
  needs. Observed RED first (5 failing with `AttributeError: 'TemplateResolution' object has no
  attribute 'path'`, 86 pre-existing tests unaffected), then GREEN after the widening (91 passed).
- Confirmed output neutrality: the full suite's failure set is exactly the 7 pre-existing
  `test_state_guard_shapes_gate.py` baseline failures (unrelated `FileNotFoundError` from the
  v0.8.0 archival move), unchanged from before this plan's commits. Confirmed no fourth
  `@preview` version-lockstep site (`test_preview_version_sync.py` 3/3 green) and no new runtime
  dependency (`pyproject.toml` diff empty for this plan).

## Task 2: Measured Values (Confirm-Only Task)

Per the task's `<action>`, the following three values were re-measured (not copied from any
planning document) and are recorded here verbatim:

| Measurement | Value |
|---|---|
| `grep -rl "_template\.typ" tests/ \| wc -l` | `32` (unchanged from 53-01/53-02's own measurement at phase start) |
| `git diff --name-only -- tests/` (this plan's full commit range) | `tests/test_template_engine.py` (only file) |
| `git diff -- pyproject.toml` (this plan's full commit range) | empty (no output) |

`uv run pytest tests/ -q`: **1179 passed, 7 failed, 5 skipped** -- the 7 failures are exactly the
pre-existing `test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[*]`
`FileNotFoundError` baseline (a path relocated by the v0.8.0 archival commit `2ea4db0f`, unrelated
to this plan), matching the orchestrator's stated baseline exactly -- no new failure introduced.

`uv run pytest tests/test_preview_version_sync.py -q`: **3 passed**.

## Task Commits

Each task was committed atomically (TDD RED -> GREEN for Task 1; Task 2 is confirm-only, no
production diff of its own):

1. **Task 1 RED: add failing assertions for TemplateResolution.path** - `9024dd48` (test)
2. **Task 1 GREEN: widen TemplateResolution with the resolved path** - `fc084a08` (feat)

**Plan metadata:** this SUMMARY.md's own commit (Task 2 produced no code diff -- its job was
running and recording the measurements above, mirroring the 53-02 plan's Task 3 precedent).

## Files Created/Modified

- `typsphinx/template_engine.py` - `TemplateResolution` gained `path: Path | None`, populated at
  all three `resolve_template()` construction sites.
- `tests/test_template_engine.py` - five additive tests in `TestTemplateResolutionProvenance`
  covering the new field at each priority, the fall-through case, and parent-directory
  obtainability. No existing test in the class was restructured or renumbered.

## Decisions Made

- The new field's `Optional` typing is deliberately not exercised by any Phase 53 branch --
  documented in the field docstring as reserved for a hypothetical future caller (a package-only
  engine with a distinct entry point) that does not exist today and is not added by this plan.
- Task 2's acceptance criteria required no code change, only measurement and recording; its
  "commit" is this SUMMARY.md, following the same shape 53-02's Task 3 (also a confirm-only
  tracer-verification task) used.

## Deviations from Plan

None - plan executed exactly as written. `resolve_template()` construction-site count stayed at
exactly 3 (`grep -c 'TemplateResolution(' typsphinx/template_engine.py` returns `3`); no
`resolve_template_path` function definition was introduced (`grep -c 'def resolve_template_path'
typsphinx/template_engine.py` returns `0`).

## Issues Encountered

None. `uv run ruff check .` could not execute in the worktree's own `.venv` (NixOS's dynamic
linker cannot run the generic-linux `ruff` binary -- the same known, previously-documented
CI-only defect class noted in 53-02's SUMMARY). Per the executor's fallback instructions, ruff was
run instead via the main checkout's working binary (`/home/yuta/Documents/typsphinx/.venv/bin/ruff
check .`) from inside this worktree's cwd, and reported `All checks passed!`. `black --check .`
and `mypy typsphinx/` both ran cleanly under `uv run` with zero issues.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The resolved template path is now recoverable at every priority through the single existing
walk, with zero output change and zero call-site migration cost -- exactly the capability
Phase 54's `<outdir>/_template/<key>/` bundle copy needs (`resolution.path.parent` names the
directory to copy). No consumer reads this field yet in Phase 53 itself, matching the plan's own
objective. The 7 pre-existing `test_state_guard_shapes_gate.py` failures (tracked in
`WINDOWS.md`, unrelated to this plan) remain unresolved and out of scope.

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: `typsphinx/template_engine.py`
- FOUND: `tests/test_template_engine.py`
- FOUND commit `9024dd48` (Task 1 RED)
- FOUND commit `fc084a08` (Task 1 GREEN)
