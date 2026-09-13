---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 08
subsystem: testing
tags: [typing, ruff, upgrade-rules, pytest, mypy]

# Dependency graph
requires:
  - phase: 70-01
    provides: "CLAUDE.md:75 rewrite authorizing the conversion under the still-present ignores"
  - phase: 70-02
    provides: "Pre-conversion baseline evidence (PHASE_BASE_SHA, VENV_HOME/VERSION_INFO, PYTEST_COLLECTED_BEFORE/RESULT_BEFORE, MYPY_STDOUT_SHA256_BEFORE)"
  - phase: 70-04
    provides: "The mask harness (Mask class + sk()) piloted EQUAL on translator.py and the ledger gate, with non-vacuity controls"
provides:
  - "tests/conftest.py, tests/test_bundle_layout_sweep_gate.py and tests/test_include_edge_derivation_unit.py on builtin generics, zero UP006/UP035 findings"
  - "Masked-AST proof (leg a) that all three files are structurally unchanged vs. PHASE_BASE_SHA"
  - "Leg (c) proof that only typing-name lines changed and no assertion was touched"
  - "Confirmation that tests/test_authors_pipeline_stage_gate.py is untouched and its line 515 ast.Dict survives"
affects: [70-09]

# Actuals (#2632)
actuals:
  tokens: 4800
  tasks: 2
  commits: 4
  plan_head_before: 6d75e9d5b9254be7f3ff3712b61878a7ae85d332

# Tech tracking
tech-stack:
  added: []
  patterns: ["masked-AST hash (Mask class from 70-04, reused verbatim) as a behaviour-identity proof for typing-only conversions"]

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TESTS-EVIDENCE.md
  modified:
    - tests/conftest.py
    - tests/test_bundle_layout_sweep_gate.py
    - tests/test_include_edge_derivation_unit.py

key-decisions:
  - "Reused 70-04's mask harness verbatim (hash-verified against MASK_HARNESS_SHA256) rather than re-deriving it, per the plan's own instruction to never retype it."
  - "The tracer feedback gate (Task 1, type=tracer) auto-continued to Task 2 without a checkpoint: HUMAN_VERIFY_MODE=end-of-phase (interactive, auto-mode inactive) and Task 1's <verify> carries only <automated>, matching row 3 of the tracer feedback gate's precedence chain."

requirements-completed: [QUA-11, QUA-12]

coverage:
  - id: D1
    description: "tests/conftest.py, tests/test_bundle_layout_sweep_gate.py and tests/test_include_edge_derivation_unit.py converted onto builtin generics; both scoped (UP006/UP035) and full ruff checks exit 0 on all three"
    requirement: QUA-11
    verification:
      - kind: other
        ref: "uv run ruff check tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py --select UP006,UP035"
        status: pass
      - kind: other
        ref: "uv run ruff check tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Masked-AST hash (leg a) equal to base for all three files, including the EXCLUDED_SWEEP_PATHS module-level annotated constant and the two files whose typing import line vanished entirely"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "sk() masked hash comparison, git show PHASE_BASE_SHA:<path> vs. working tree, all three files EQUAL"
        status: pass
    human_judgment: false
  - id: D3
    description: "Leg (c): every changed non-blank line carries a typing name, no changed line contains assert, no pre-existing assertion edited, tests/test_authors_pipeline_stage_gate.py untouched with ast.Dict intact at line 515"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "git diff line-content census: NON_TYPING_LINES_70_08 = 0, ASSERT_LINES_70_08 = 0"
        status: pass
      - kind: unit
        ref: "tests/test_authors_pipeline_stage_gate.py:515 (untouched, ast.Dict intact)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full suite: pytest collected count and result equal to base, black/ruff repo-wide/mypy all clean or hash-identical to base"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider (1547 passed, 1 skipped, exit 0)"
        status: pass
      - kind: other
        ref: "uv run black --check, uv run ruff check ., uv run mypy typsphinx/ (stdout hash equal to MYPY_STDOUT_SHA256_BEFORE)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 08: Convert the remaining tests/ files onto builtin generics Summary

**Converted `tests/conftest.py`, `tests/test_bundle_layout_sweep_gate.py` and `tests/test_include_edge_derivation_unit.py` to builtin generics via two scoped ruff `--fix` passes, proved structurally identical to base with the pinned masked-AST harness, and confirmed zero assertion drift with the full 1547-passed/1-skipped suite unchanged.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-13T05:05:15Z
- **Completed:** 2026-09-13T05:50:00Z (approx)
- **Tasks:** 2
- **Files modified:** 3 source + 1 evidence file created

## Accomplishments
- `tests/conftest.py` keeps `from typing import Any` (its `Dict[str, Any]` → `dict[str, Any]`); `tests/test_bundle_layout_sweep_gate.py` and `tests/test_include_edge_derivation_unit.py` lose their `from typing import ...` line entirely, since no other typing name remains in either file — exactly as predicted in `70-PATTERNS.md`.
- The module-level annotated constant `EXCLUDED_SWEEP_PATHS: Dict[str, str]` in `test_bundle_layout_sweep_gate.py` converts to `dict[str, str]` and is proven covered by the mask (leg a EQUAL includes this `AnnAssign` case).
- Masked-AST hashes (`sk()`, hash-verified against `MASK_HARNESS_SHA256` before use) are EQUAL to `PHASE_BASE_SHA` for all three files — no statement, expression, call or control-flow node moved, was added, or was removed outside the typing-import and annotation subtrees the mask covers.
- Leg (c) census: `NON_TYPING_LINES_70_08 = 0`, `ASSERT_LINES_70_08 = 0` — every changed non-blank line carries a typing name and none contains `assert`. `tests/test_authors_pipeline_stage_gate.py` (line 515's `ast.Dict`, the stdlib AST node that must never be touched) has zero diff against base.
- `uv run black --check`, repo-wide `uv run ruff check .`, and `uv run mypy typsphinx/` (stdout hash `46984ca2...`, equal to `MYPY_STDOUT_SHA256_BEFORE`) all pass clean. `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` collected 1548 and ran `1547 passed, 1 skipped` (both equal to the pre-conversion baseline), confirmed by two independent full-suite runs (Task 1's precondition + Task 2's own gate run).

## Task Commits

Each task was committed atomically:

1. **Task 1: Convert the three tests/ files, prove leg (a)** - `3b473894` (refactor) + `1012e783` (docs, evidence)
2. **Task 2: Gate leg (c), black/ruff/mypy/pytest** - `01a6e31b` (docs, evidence)

**Plan metadata:** (this SUMMARY's own commit, made after this file)

## Files Created/Modified
- `tests/conftest.py` - `from typing import Any, Dict` → `Any`; `Dict[str, Any]` → `dict[str, Any]`
- `tests/test_bundle_layout_sweep_gate.py` - `Dict`/`List` → `dict`/`list`; typing import line removed entirely
- `tests/test_include_edge_derivation_unit.py` - `Dict`/`List` → `dict`/`list`; typing import line removed entirely
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TESTS-EVIDENCE.md` - conversion transcript, leg (a) masked hashes, leg (c) census, and full gate results

## Decisions Made
- Reused 70-04's mask harness verbatim (never retyped), hash-checked against `MASK_HARNESS_SHA256` at the start of Task 1, per the plan's worktree_provisioning instructions.
- The tracer feedback gate after Task 1 auto-continued to Task 2 (row 3 of the precedence chain in `checkpoints.md`: interactive, `end-of-phase`, and the tracer's `<verify>` carries only `<automated>`) — no checkpoint was synthesized, since the automated verify re-ran and passed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Both tasks' automated `<verify>` blocks passed on the first run; no ruff finding, mask mismatch, assertion touch, or gate failure occurred.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The last file-disjoint wave-3 conversion (`tests/conftest.py`, `tests/test_bundle_layout_sweep_gate.py`, `tests/test_include_edge_derivation_unit.py`) lands lint-green with `TESTS_MASK = EQUAL`, `NON_TYPING_LINES_70_08 = 0`, `ASSERT_LINES_70_08 = 0`, and every gate (black/ruff/mypy/pytest) matching base. Combined with 70-04's earlier translator.py + ledger-gate conversion, `tests/` is now fully converted. Ready for 70-09's ignore flip, contingent on the other wave-3 siblings (70-05, 70-06, 70-07) landing their own file-disjoint conversions.

## Self-Check: PASSED

- `[ -f tests/conftest.py ]` → FOUND
- `[ -f tests/test_bundle_layout_sweep_gate.py ]` → FOUND
- `[ -f tests/test_include_edge_derivation_unit.py ]` → FOUND
- `[ -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TESTS-EVIDENCE.md ]` → FOUND
- `git log --oneline --all | grep -q 3b473894` → FOUND
- `git log --oneline --all | grep -q 1012e783` → FOUND
- `git log --oneline --all | grep -q 01a6e31b` → FOUND
- Task 1 acceptance criteria: all PASS (ruff clean both scopes, typing import lines match spec, all three masked hashes equal base, `TESTS_MASK = EQUAL`)
- Task 2 acceptance criteria: all PASS (`NON_TYPING_LINES_70_08 = 0`, `ASSERT_LINES_70_08 = 0`, authors pipeline gate untouched with `ast.Dict` intact, collected/result counts equal base, black/ruff/mypy clean)

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
