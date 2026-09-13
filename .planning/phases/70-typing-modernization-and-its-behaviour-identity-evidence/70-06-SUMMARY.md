---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 06
subsystem: quality
tags: [ruff, typing, mypy, ast, template-engine]

# Dependency graph
requires:
  - phase: 70-01/70-02/70-04
    provides: "CLAUDE.md:75 rewrite (pre-flip), pre-conversion baseline (PHASE_BASE_SHA, VENV_HOME/VERSION_INFO, PYTEST_RESULT_BEFORE, MYPY_STDOUT_SHA256_BEFORE), and the pinned mask harness (MASK_HARNESS_SHA256) piloted EQUAL/non-vacuous on translator.py"
provides:
  - "typsphinx/template_engine.py and typsphinx/template_registry.py converted onto builtin generics, both lint-green under and without the UP006/UP035 ignores"
  - "70-CONV-TEMPLATE-EVIDENCE.md: masked-AST leg (a) proof (TEMPLATE_ENGINE_MASK/TEMPLATE_REGISTRY_MASK = EQUAL), changed-line census (NON_TYPING_LINES_70_06 = 0), and gate parity with base (mypy stdout hash, full pytest result, @preview byte-identity)"
affects: [70-09 (the ignore-flip plan, which depends on every wave-3 conversion landing lint-green)]

# Actuals (#2632)
actuals:
  tokens: 5417
  tasks: 2
  commits: 5
plan_head_before: 6d75e9d5b9254be7f3ff3712b61878a7ae85d332

# Tech tracking
tech-stack:
  added: []
  patterns: ["ruff --fix two-pass conversion (scoped UP006/UP035 pass, then config-rule pass for the resulting F401 import-line shrink)", "masked-AST leg (a) hash harness reused verbatim from 70-04"]

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TEMPLATE-EVIDENCE.md
  modified:
    - typsphinx/template_engine.py
    - typsphinx/template_registry.py

key-decisions:
  - "Both files' typing import lines shrink in place to `from typing import Any` (neither the import-split nor import-vanish shape 70-04's ledger-gate file exercised) — both keep other `Any`-typed annotations in the body."

requirements-completed: [QUA-11, QUA-12]

coverage:
  - id: D1
    description: "typsphinx/template_engine.py and typsphinx/template_registry.py converted onto builtin generics; both exit 0 under `ruff check --select UP006,UP035` and plain `ruff check`"
    requirement: QUA-11
    verification:
      - kind: other
        ref: "uv run ruff check typsphinx/template_engine.py typsphinx/template_registry.py --select UP006,UP035"
        status: pass
      - kind: other
        ref: "uv run ruff check typsphinx/template_engine.py typsphinx/template_registry.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Masked-AST leg (a): both files structurally identical to PHASE_BASE_SHA under the annotation/import mask"
    requirement: QUA-12
    verification:
      - kind: other
        ref: "sk() masked-hash harness (MASK_HARNESS_SHA256-pinned) — TEMPLATE_ENGINE_MASK = EQUAL, TEMPLATE_REGISTRY_MASK = EQUAL"
        status: pass
    human_judgment: false
  - id: D3
    description: "Behaviour-identity gates: full pytest suite and mypy stdout unchanged from base; every changed line carries a typing name; the four @preview version-sync strings untouched"
    requirement: QUA-12
    verification:
      - kind: unit
        ref: "LC_ALL=C uv run pytest -q -rs -p no:cacheprovider — 1547 passed, 1 skipped (equal to PYTEST_RESULT_BEFORE)"
        status: pass
      - kind: other
        ref: "uv run mypy typsphinx/ — stdout sha256 equal to MYPY_STDOUT_SHA256_BEFORE"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 06: Template Engine and Registry Typing Conversion Summary

**Converted `template_engine.py` and `template_registry.py` from `typing.Dict`/`List` to builtin `dict`/`list` via a two-pass `ruff --fix`, proved structurally identical to base with the pinned masked-AST hash harness, and confirmed mypy, the full pytest suite, and the four `@preview` version-sync import strings are byte-for-byte unchanged.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-09-13T05:03:40Z
- **Completed:** 2026-09-13T05:13:05Z
- **Tasks:** 2
- **Files modified:** 2 source files + 1 new evidence file

## Accomplishments
- `typsphinx/template_engine.py` (12 findings: 2 UP035, 10 UP006) and `typsphinx/template_registry.py` (4 findings: 1 UP035, 3 UP006) both converted via `ruff check --select UP006,UP035 --fix` (pass 1) then `ruff check --fix` (pass 2, cleans up the resulting F401 import-line shrink). Both now exit 0 on both invocations, with and without `--select`.
- Both typing import lines shrink in place to `from typing import Any` — the shrink-in-place shape, distinct from 70-04's ledger-gate file which exercised import-split and import-vanish.
- Masked-AST leg (a): `TEMPLATE_ENGINE_MASK = EQUAL` and `TEMPLATE_REGISTRY_MASK = EQUAL` against `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`), using the harness extracted from `70-MASK-PILOT-EVIDENCE.md` and verified against `MASK_HARNESS_SHA256` before use.
- Changed-line census: every added/removed line in both files' diff carries a typing name (`NON_TYPING_LINES_70_06 = 0`); no changed line contains `assert` or `@preview`; `template_engine.py`'s four `@preview/` import strings and its `@preview/charged-ieee` docstring example are byte-identical between `PHASE_BASE_SHA` and HEAD.
- Full gate parity with base: `uv run black --check` on both files, repo-wide `uv run ruff check .`, `uv run mypy typsphinx/` (stdout sha256 equal to `MYPY_STDOUT_SHA256_BEFORE`), and the full suite (`LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` → `1547 passed, 1 skipped`, equal to `PYTEST_RESULT_BEFORE`) all pass unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: convert template_engine.py and template_registry.py with the two scoped ruff passes and prove leg (a) for both with the pinned mask harness** - `a7f35d33` (refactor) — the two source files alone
   - Evidence for Task 1 (Head check/provisioning, Conversion, Leg (a) sections) - `0fec0268` (docs)
2. **Task 2: Gate the conversion: changed-line census, no assert or @preview line, black, repo-wide ruff, mypy stdout and the full pytest result against the baseline** - `6e529253` (docs) — Changed-line census and Gates sections

**Plan metadata:** pending (SUMMARY commit)

_Note: Task 1 is a `type="tracer"` task; its own commit is source-only, with the evidence recorded in a separate commit immediately after, per the plan's worktree_provisioning instruction ("Commit the two files alone" then "Commit the evidence file")._

## Files Created/Modified
- `typsphinx/template_engine.py` - `Dict`/`List` annotations → `dict`/`list`; import line `from typing import Any, Dict, List` → `from typing import Any`
- `typsphinx/template_registry.py` - `Dict` annotations → `dict`; import line `from typing import Any, Dict` → `from typing import Any`
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TEMPLATE-EVIDENCE.md` - conversion transcript, leg (a) hashes, changed-line census, gate results (new file)

## Decisions Made
None beyond what the plan specified - plan executed exactly as written. The plan left the exact shape of the import-line convergence (shrink/split/vanish) to be discovered by measurement; both files landed on the shrink-in-place shape, confirmed and recorded above.

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes, no blocking issues, no architectural questions arose. Both mask hashes matched on the first attempt; no HALT condition was reached.

## Issues Encountered
None.

## Tracer Feedback Gate

Task 1 is `type="tracer"`. Its `<verify>` carries only an `<automated>` block (no `<human-check>`), `workflow.human_verify_mode` is `end-of-phase` (the project default; `.planning/config.json` does not override it), and neither `workflow._auto_chain_active` nor `workflow.auto_advance` is `true` in `.planning/config.json` — so per the tracer feedback gate's row 3 (interactive, end-of-phase, automated-only verify), the tracer's own `<verify>` automated block was re-run before expanding into Task 2, passed (`ALL PASS`), and execution continued to Task 2 with no checkpoint synthesized.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

This plan's conversion is one of four file-disjoint wave-3 conversions (alongside 70-05 `builder.py`, 70-07 `writer.py`/`__init__.py`, 70-08 the three test-gate files). `template_engine.py` and `template_registry.py` are lint-green under both the scoped `UP006`/`UP035` selection and the full ruff config, structurally unchanged under the masked-AST proof, and behaviour-identical on mypy and the full pytest suite. Ready for 70-09's ignore-flip once all four wave-3 plans land.

## Self-Check: PASSED

- `typsphinx/template_engine.py` — FOUND
- `typsphinx/template_registry.py` — FOUND
- `70-CONV-TEMPLATE-EVIDENCE.md` — FOUND
- `70-06-SUMMARY.md` — FOUND
- Commit `a7f35d33` — FOUND
- Commit `0fec0268` — FOUND
- Commit `6e529253` — FOUND
- Commit `cf705ee8` — FOUND
- All Task 1 and Task 2 acceptance criteria re-verified passing (see automated verify runs above)

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
