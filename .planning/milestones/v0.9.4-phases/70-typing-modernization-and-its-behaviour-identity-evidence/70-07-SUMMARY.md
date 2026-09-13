---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 07
subsystem: quality
tags: [ruff, typing, mypy, pytest, ast-hash]

# Dependency graph
requires:
  - phase: 70-01
    provides: CLAUDE.md:75 rewritten to authorize the builtin-generics conversion
  - phase: 70-02
    provides: pre-conversion baseline (ruff/mypy/pytest keys, VENV_HOME/VENV_VERSION_INFO)
  - phase: 70-04
    provides: the pinned mask-harness (MASK_HARNESS_SHA256) and its non-vacuity controls
provides:
  - typsphinx/writer.py and typsphinx/__init__.py on builtin generics (dict/tuple), no UP006/UP035 findings
  - the one documented hand edit (typsphinx/__init__.py:15) closing the __init__.py F401 survivor
  - leg (a) proof (masked-AST hash equality to base) for both files
affects: [70-09 (the ignore-flip plan), 70-10/70-11 (repo-wide gates)]

# Actuals (#2632)
actuals:
  tokens: 3937
  tasks: 2
  commits: 5
plan_head_before: 6d75e9d5b9254be7f3ff3712b61878a7ae85d332

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The __init__.py F401 carve-out: ruff withholds unused-import fixes in __init__.py files unless --preview is enabled; the fix is a single hand-applied Edit, never sed/--preview/--unsafe-fixes."
    - "Two-pass ruff conversion: --select UP006,UP035 --fix first (annotation usages), then bare --fix (header-line import cleanup via F401/I001)."

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-WRITER-INIT-EVIDENCE.md
  modified:
    - typsphinx/writer.py
    - typsphinx/__init__.py

key-decisions:
  - "typsphinx/__init__.py:15 hand-edited with the Edit tool from `from typing import Any, Dict` to `from typing import Any` — the only manual edit in this plan, matching ROADMAP constraint 5 and the plan's must_haves."

requirements-completed: [QUA-11, QUA-12]

coverage:
  - id: D1
    description: "typsphinx/writer.py and typsphinx/__init__.py converted to builtin generics via the two scoped ruff passes, zero UP006/UP035 findings remaining"
    requirement: QUA-11
    verification:
      - kind: other
        ref: "uv run ruff check typsphinx/writer.py typsphinx/__init__.py --select UP006,UP035 (exit 0)"
        status: pass
      - kind: other
        ref: "uv run ruff check typsphinx/writer.py typsphinx/__init__.py (exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The one documented hand edit at typsphinx/__init__.py:15 closes the F401 survivor without --preview/--unsafe-fixes/sed"
    requirement: QUA-11
    verification:
      - kind: other
        ref: "sed -n 15p typsphinx/__init__.py == 'from typing import Any'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Leg (a): masked-AST hash equality between each converted file and its PHASE_BASE_SHA counterpart, using the pinned mask harness"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "70-CONV-WRITER-INIT-EVIDENCE.md ## Leg (a) (WRITER_MASK = EQUAL, INIT_MASK = EQUAL); independently re-verified from a private, non-shared scratch script after a sibling agent overwrote the shared scratchpad"
        status: pass
    human_judgment: false
  - id: D4
    description: "writer.py's four @preview import lines stay byte-identical to base; changed-line census shows every changed line carries a typing name and none contains assert or @preview"
    requirement: QUA-11
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py"
        status: pass
      - kind: other
        ref: "70-CONV-WRITER-INIT-EVIDENCE.md ## Changed-line census (NON_TYPING_LINES_70_07 = 0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "mypy and the full pytest suite are unchanged from the pre-conversion baseline"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "uv run mypy typsphinx/ stdout SHA256 == MYPY_STDOUT_SHA256_BEFORE (46984ca2...)"
        status: pass
      - kind: integration
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider — 1547 passed, 1 skipped, matches PYTEST_RESULT_BEFORE"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 07: Convert writer.py and __init__.py, close the __init__.py survivor with the one hand edit Summary

**Moved `typsphinx/writer.py` and `typsphinx/__init__.py` onto builtin generics via two scoped ruff passes, then closed the one `__init__.py:15` F401 survivor with a single Edit-tool hand edit — leg (a) masked-AST hashes, mypy stdout, and the full 1547/1-skipped pytest result all match base exactly.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-09-13T05:xx:xxZ (worktree provisioning)
- **Completed:** 2026-09-13T05:17:44Z
- **Tasks:** 2
- **Files modified:** 2 source files + 1 evidence file (+ this SUMMARY)

## Accomplishments
- `typsphinx/writer.py`'s `from typing import Any, Tuple` header line and its one `Tuple[str, ...]`
  usage (line 284) converted to `from typing import Any` and `tuple[str, ...]`.
- `typsphinx/__init__.py`'s `Dict[str, Any]` return annotation (line 29) converted to
  `dict[str, Any]` via ruff's `--select UP006,UP035 --fix`; the header line's own `Dict` import
  survived both ruff passes (the documented `__init__.py`-only F401 carve-out) and was closed with
  the one hand edit: `from typing import Any, Dict` → `from typing import Any`.
- Both files' masked-AST hashes (leg a, the pinned harness from `70-MASK-PILOT-EVIDENCE.md`) equal
  their `PHASE_BASE_SHA` counterparts — `WRITER_MASK = EQUAL`, `INIT_MASK = EQUAL` — proving the
  conversion changed only annotations/imports, no other AST structure.
- `writer.py`'s four `#import "@preview/…"` lines stayed byte-identical to base (confirmed via
  `git grep` at both commits and `tests/test_preview_version_sync.py` passing).
- `uv run mypy typsphinx/` stdout hash and the full pytest result (`1547 passed, 1 skipped`) are
  byte-identical / string-identical to the phase's pre-conversion baseline.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — convert writer.py and __init__.py, record the survivor, hand edit, leg (a)** -
   `47159f96` (refactor) — the two converted files
   `a0b1b9ad` (docs) — the Task 1 conversion-transcript evidence
2. **Task 2: Gate the conversion — changed-line census, @preview identity, black/ruff/mypy/pytest** -
   `3ab2f371` (docs) — the Task 2 gates evidence

**Plan metadata:** committed separately by the `git_commit_metadata` step (this SUMMARY.md,
`.planning/REQUIREMENTS.md` in worktree mode).

## Files Created/Modified
- `typsphinx/writer.py` - `from typing import Any, Tuple` → `from typing import Any`;
  `Tuple[str, ...]` → `tuple[str, ...]` at line 284 (`compute_content_include_path`'s `edge_keys`
  parameter)
- `typsphinx/__init__.py` - `from typing import Any, Dict` → `from typing import Any` (the one
  hand edit); `def setup(app: Sphinx) -> Dict[str, Any]:` → `-> dict[str, Any]:`
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-WRITER-INIT-EVIDENCE.md` -
  head check/provisioning, the two ruff passes and their diagnostic counts, the hand edit record
  (`INIT_LINE_15`), leg (a) masked-hash proof, changed-line census, and the black/ruff/mypy/pytest
  gates

## Decisions Made
- The one hand edit was applied with the Edit tool exactly as the plan's `must_haves.truths`
  specified — no `sed`, no `--preview`, no `--unsafe-fixes`. This matches ROADMAP constraint 5 and
  the phase-wide singleton documented in `70-PATTERNS.md` and `STACK.md`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Shared-scratchpad collision (wave-3 concurrency).** A sibling wave-3 agent overwrote a
generically-named helper script (`verify_task2.sh`) in the shared `/tmp/claude-*/scratchpad`
directory mid-run, per an orchestrator notice received during this plan's execution. Before
trusting either task's verify result, I re-created both verify scripts (and the mask harness)
under a private `mktemp -d` directory (`/tmp/p07-verify.*`, files prefixed `p07_`) and re-ran every
check — the ruff/black/mypy/pytest gates and the masked-hash equality all reproduced identically
(`P07_TASK1_VERIFY: PASS`, `P07_TASK2_VERIFY: PASS`, masked hashes byte-identical to the
first run). No evidence values changed; this only adds an independent-script confirmation layer
to the already-recorded evidence.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `typsphinx/writer.py` and `typsphinx/__init__.py` are lint-green under the still-present
  `UP006`/`UP035` ignores, ready for 70-09's ignore-flip to find zero residual findings in these
  two files.
- No blockers. This plan's branch touches only its own two source files, its own evidence file,
  and this SUMMARY — file-disjoint from 70-05/70-06/70-08 as the plan's `must_haves` required.

## Self-Check: PASSED

- FOUND: `typsphinx/writer.py`
- FOUND: `typsphinx/__init__.py`
- FOUND: `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-WRITER-INIT-EVIDENCE.md`
- FOUND: `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-07-SUMMARY.md`
- FOUND commits: `47159f96`, `a0b1b9ad`, `3ab2f371` (`git log --oneline -5`)
- Both tasks' `<acceptance_criteria>` and the plan-level `<verification>` re-run PASS, independently
  reproduced from a private, non-shared script after the shared-scratchpad collision noted above.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
