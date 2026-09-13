---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 05
subsystem: quality
tags: [ruff, typing, builtin-generics, mypy, pytest, mask-harness]

# Dependency graph
requires:
  - phase: 70-01
    provides: CLAUDE.md:75 rewritten to authorize builtin-generics conversion
  - phase: 70-02
    provides: PHASE_BASE_SHA and pre-conversion baseline (ruff/mypy/pytest)
  - phase: 70-04
    provides: hash-pinned mask harness (MASK_HARNESS_SHA256) piloted EQUAL/DIFFER on both legs
provides:
  - "typsphinx/builder.py converted onto builtin generics (dict/list/set/tuple), typing import shrunk to `Any`, `collections.abc.Iterator` line untouched"
  - "Masked-AST proof that builder.py's non-annotation, non-import structure is unchanged from PHASE_BASE_SHA"
affects: [70-09 (pyproject.toml ignore flip needs this file clean first)]

# Actuals (#2632)
actuals:
  tokens: 3663
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-pass ruff conversion: --select UP006,UP035 --fix then plain --fix for import-line cleanup (I001/F401)"
    - "Masked-AST hash harness (ImportFrom deletion + annotation nulling) as an automated structural-identity gate"

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-BUILDER-EVIDENCE.md
  modified:
    - typsphinx/builder.py

key-decisions:
  - "Followed the plan exactly: no hand edits, ruff --fix resolved all 30 UP006/UP035 findings in builder.py across two passes."

patterns-established:
  - "Pattern established in 70-04, reused here unchanged: masked-hash equality as leg (a) proof, changed-line census as a textual auto-fix bound, mypy stdout hash + full pytest result as legs (e)/(b)."

requirements-completed: [QUA-11, QUA-12]

coverage:
  - id: D1
    description: "typsphinx/builder.py converted onto builtin generics under the still-present UP006/UP035 ignores; typing import shrinks to `from typing import Any`, `from collections.abc import Iterator` untouched"
    requirement: QUA-11
    verification:
      - kind: other
        ref: "uv run ruff check typsphinx/builder.py --select UP006,UP035 (exit 0, 0 findings)"
        status: pass
      - kind: other
        ref: "uv run ruff check typsphinx/builder.py (exit 0, config-rule clean)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Masked-AST hash proof that builder.py's non-annotation, non-import structure is byte-for-byte unchanged from PHASE_BASE_SHA (leg a)"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "70-CONV-BUILDER-EVIDENCE.md § Leg (a) — BUILDER_MASK = EQUAL, hash-pinned harness verified against MASK_HARNESS_SHA256"
        status: pass
    human_judgment: false
  - id: D3
    description: "mypy typsphinx/ stdout and the full pytest suite are unchanged from the pre-conversion baseline (legs e and b)"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "uv run mypy typsphinx/ 2>/dev/null — stdout sha256 46984ca2... equal to MYPY_STDOUT_SHA256_BEFORE"
        status: pass
      - kind: unit
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider — 1547 passed, 1 skipped, equal to PYTEST_RESULT_BEFORE"
        status: pass
    human_judgment: false

# Metrics
duration: ~15min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 05: Builder.py Builtin-Generics Conversion Summary

**Converted `typsphinx/builder.py`'s 30 `Dict`/`List`/`Set`/`Tuple` annotations to builtin generics via two scoped ruff `--fix` passes, then proved structural identity to base with the hash-pinned masked-AST harness and re-confirmed mypy/pytest unchanged.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-09-13T05:04:45Z (head check)
- **Completed:** 2026-09-13T05:12:12Z
- **Tasks:** 2
- **Files modified:** 1 source file (`typsphinx/builder.py`) + 1 evidence file created

## Accomplishments
- `typsphinx/builder.py` moved onto builtin generics (`dict`/`list`/`set`/`tuple`); its typing import line shrinks to `from typing import Any`; its pre-existing `from collections.abc import Iterator` line is untouched — both `uv run ruff check typsphinx/builder.py --select UP006,UP035` and the plain config-rule `uv run ruff check typsphinx/builder.py` exit 0.
- Leg (a) proof: the masked hash of the converted `builder.py` equals the masked hash of `git show PHASE_BASE_SHA:typsphinx/builder.py`, computed with the exact hash-pinned harness from `70-MASK-PILOT-EVIDENCE.md` (verified against `MASK_HARNESS_SHA256` before use) — `BUILDER_MASK = EQUAL`.
- Changed-line census: every non-blank changed line in the diff carries a typing name (`NON_TYPING_LINES_70_05 = 0`); no changed line contains `assert` or `@preview`.
- Gates: `black --check`, repo-wide `ruff check .`, mypy stdout hash, and the full 1548-test pytest suite are all unchanged from the pre-conversion baseline recorded in `70-BASELINE-EVIDENCE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — convert builder.py and prove leg (a)** - `3cda095a` (refactor) + `a7ac6465` (docs, evidence)
2. **Task 2: Gate the conversion — census, black, repo-wide ruff, mypy, pytest** - `62955550` (docs, evidence)

**Plan metadata:** committed alongside this SUMMARY (worktree mode — orchestrator handles STATE.md/ROADMAP.md centrally after merge).

## Files Created/Modified
- `typsphinx/builder.py` - 17 insertions / 17 deletions: every `Dict[...]`/`List[...]`/`Set[...]`/`Tuple[...]` annotation converted in place to `dict[...]`/`list[...]`/`set[...]`/`tuple[...]`; typing import line shrunk from `from typing import Any, Dict, List, Set, Tuple` to `from typing import Any`
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-BUILDER-EVIDENCE.md` - Conversion transcript, leg (a) masked-hash proof, changed-line census, and gate results

## Decisions Made
None - plan executed exactly as written. No hand edits were needed; `ruff check . --fix` (two passes) fully resolved all 30 findings, matching `70-PATTERNS.md`'s predicted shape for this file exactly.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Two sandbox guard refusals on overly-complex chained shell commands (multiple `git` invocations, or `-c` with a runtime-computed script string) were worked around by writing the equivalent logic to a scratch script file and running it with `bash <script>` — same approach the orchestrator notes anticipated (note 3). No functional impact; every value produced matched hand-verification.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `typsphinx/builder.py` is lint-green under the still-present `UP006`/`UP035` ignores, structurally proven identical to base, and mypy/pytest are unchanged — one of the four file-disjoint wave-3 conversions is ready for 70-09's pyproject.toml ignore flip.
- No blockers. This plan's branch changes only `typsphinx/builder.py`, its own evidence file, and this SUMMARY — confirmed disjoint from 70-06/70-07/70-08's declared file sets.

## Self-Check: PASSED

- `typsphinx/builder.py` exists and contains `from typing import Any` and `from collections.abc import Iterator`: confirmed.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-BUILDER-EVIDENCE.md` exists with all required sections (`## Head check and provisioning`, `## Conversion`, `## Leg (a)`, `## Changed-line census`, `## Gates`): confirmed.
- Commits `3cda095a`, `a7ac6465`, `62955550` all present in `git log --oneline`: confirmed.
- Plan-level acceptance criteria (both tasks) re-verified via the plan's own `<automated>` verify blocks, both printing their PASS sentinel with exit 0.
- `git diff --name-only BASE_70_05 HEAD` (before adding this SUMMARY) lists only `typsphinx/builder.py` and the evidence file — confirmed disjoint scope.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
