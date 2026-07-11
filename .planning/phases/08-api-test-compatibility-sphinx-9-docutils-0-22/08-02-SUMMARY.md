---
phase: 08-api-test-compatibility-sphinx-9-docutils-0-22
plan: 02
subsystem: testing
tags: [sphinx, docutils, deprecation, pytest, api-compatibility]

# Dependency graph
requires:
  - phase: 08-api-test-compatibility-sphinx-9-docutils-0-22
    provides: "Plan 08-01's traverse->findall + OptionParser->frontend.get_default_settings modernization (established the deprecation-sweep pattern)"
provides:
  - "tests/test_builder.py and tests/test_pdf_generation.py assert builder._app (Sphinx 9 RemovedInSphinx11Warning resolved)"
  - "tests/test_documentation_configuration.py and tests/test_documentation_usage.py call publish_string(writer=get_writer_class('html')()) (docutils 0.22 writer_name deprecation resolved)"
affects: ["08-03 filterwarnings guard plan (Wave 2) — this plan clears the remaining deprecation sites so the guard lands green"]

# Tech tracking
tech-stack:
  added: []
  patterns: ["docutils publish_string(writer=<instance>) instead of writer_name=<string> for forward-compat with docutils 2.0"]

key-files:
  created: []
  modified:
    - tests/test_builder.py
    - tests/test_pdf_generation.py
    - tests/test_documentation_configuration.py
    - tests/test_documentation_usage.py

key-decisions:
  - "Test-assertion-only edits, no runtime source touched (typsphinx/builder.py never accesses .app)"

patterns-established:
  - "Pattern: publish_string(writer=get_writer_class('html')()) replaces writer_name='html' string argument (docutils 0.22+ forward-compat)"

requirements-completed: [API-02]

coverage:
  - id: D1
    description: "tests/test_builder.py and tests/test_pdf_generation.py assert builder._app instead of the deprecated builder.app property"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_builder.py tests/test_pdf_generation.py -q -W error::PendingDeprecationWarning -W error::DeprecationWarning -x"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_documentation_configuration.py and tests/test_documentation_usage.py call publish_string with writer=get_writer_class('html')() instead of the deprecated writer_name string argument"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_documentation_configuration.py tests/test_documentation_usage.py -q -W error::PendingDeprecationWarning -W error::DeprecationWarning -x"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-07-11
status: complete
---

# Phase 08 Plan 02: Test-file deprecation sweep (builder.app + writer_name) Summary

**Replaced Sphinx 9's deprecated `builder.app` property with `builder._app` and docutils 0.22's deprecated `writer_name` string argument with `writer=get_writer_class(...)()` across all 4 mirror-pair test files.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-07-11T02:44:31Z
- **Completed:** 2026-07-11T02:46:19Z
- **Tasks:** 2 completed
- **Files modified:** 4

## Accomplishments
- `tests/test_builder.py` and `tests/test_pdf_generation.py` now assert `builder._app` (the non-deprecated underlying attribute), eliminating Sphinx 9's `RemovedInSphinx11Warning` on the `.app` property read.
- `tests/test_documentation_configuration.py` and `tests/test_documentation_usage.py` now call `publish_string(..., writer=get_writer_class("html")(), ...)`, eliminating docutils 0.22's `PendingDeprecationWarning` on the `writer_name="html"` string argument.
- All 4 files pass under `-W "error::PendingDeprecationWarning" -W "error::DeprecationWarning"` — the exact escalated-warning gate the Plan 08-03 `filterwarnings` guard will enforce project-wide.

## Task Commits

Each task was committed atomically:

1. **Task 1: builder.app -> builder._app in test_builder.py + test_pdf_generation.py (API-02)** - `644c3e4` (fix)
2. **Task 2: publish_string writer_name -> writer=get_writer_class in doc-example tests (API-02)** - `5b00bfb` (fix)

**Plan metadata:** commit pending (this docs commit)

## Files Created/Modified
- `tests/test_builder.py` - line 64: `assert builder.app == app` -> `assert builder._app == app`
- `tests/test_pdf_generation.py` - line 80: `assert builder.app == temp_sphinx_app` -> `assert builder._app == temp_sphinx_app`
- `tests/test_documentation_configuration.py` - added `from docutils.writers import get_writer_class` import; `writer_name="html"` -> `writer=get_writer_class("html")()`
- `tests/test_documentation_usage.py` - added `from docutils.writers import get_writer_class` import; `writer_name="html"` -> `writer=get_writer_class("html")()`

## Decisions Made
None - plan executed exactly as written. Both mirror-pairs were 1-line (Task 1) / 2-line (Task 2) drop-in fixes with no ambiguity; RHS operands (`app`, `temp_sphinx_app`, `source=content`, `settings_overrides`) were preserved unchanged per the plan's explicit instruction.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The plan's NixOS subprocess-launch caveat (Pitfall 3: `Could not start dynamically linked executable: uv`) did not manifest — `tests/test_pdf_generation.py` ran fully in-process under this environment and all 24 of its tests passed cleanly alongside `test_builder.py`'s 20 tests (44 total for Task 1's verify run; 67 total across all 4 files in the combined plan-level verification).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All 4 remaining `builder.app` / `writer_name` deprecation sites from the 08-RESEARCH.md 6-edit sweep are now resolved (the other 2 — `template_engine.py` traverse->findall and `test_translator.py` OptionParser — landed in Plan 08-01).
- The full test suite (all 4 files, 67 tests) is green under both `PendingDeprecationWarning` and `DeprecationWarning` escalated to errors — Plan 08-03 can now safely enable the `pyproject.toml` `filterwarnings` guard (Wave 2) without breaking these sites, satisfying the D-02 ordering constraint (guard lands after the full sweep).
- No blockers for Plan 08-03.

---
*Phase: 08-api-test-compatibility-sphinx-9-docutils-0-22*
*Completed: 2026-07-11*

## Self-Check: PASSED

- FOUND: tests/test_builder.py
- FOUND: tests/test_pdf_generation.py
- FOUND: tests/test_documentation_configuration.py
- FOUND: tests/test_documentation_usage.py
- FOUND: .planning/phases/08-api-test-compatibility-sphinx-9-docutils-0-22/08-02-SUMMARY.md
- FOUND: commit 644c3e4
- FOUND: commit 5b00bfb
