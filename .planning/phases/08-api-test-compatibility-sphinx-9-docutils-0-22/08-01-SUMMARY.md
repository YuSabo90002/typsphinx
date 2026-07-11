---
phase: 08-api-test-compatibility-sphinx-9-docutils-0-22
plan: 01
subsystem: testing
tags: [docutils, sphinx, deprecation, findall, frontend, pytest]

# Dependency graph
requires:
  - phase: 07-bump-preview-packages-typst-0-15-kai-fix
    provides: typst 0.15.0 + @preview package pins confirmed compiling clean, unblocking the Sphinx 9 / docutils 0.22 API sweep
provides:
  - "typsphinx/template_engine.py toctree traversal modernized: doctree.traverse() -> doctree.findall() (API-01, locked)"
  - "tests/test_translator.py's 3 docutils settings-construction sites modernized: OptionParser(...).get_default_values() -> frontend.get_default_settings(RstParser) (part of API-02)"
  - "Suite proven green under -W error::DeprecationWarning -W error::PendingDeprecationWarning for the two touched test files, ahead of the permanent filterwarnings guard landing in Plan 03"
affects: [08-02-test-compatibility-sweep, 08-03-filterwarnings-guard]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "doctree.findall(NodeClass) is the drop-in replacement for the deprecated doctree.traverse(NodeClass) generator (mirrors builder.py:151's existing usage)"
    - "docutils.frontend.get_default_settings(*components) is the blessed replacement for frontend.OptionParser(components=...).get_default_values() ahead of docutils 2.0's argparse rewrite"

key-files:
  created: []
  modified:
    - typsphinx/template_engine.py
    - tests/test_translator.py

key-decisions:
  - "Followed the plan's locked scope exactly: only the single traverse()->findall() source fix and the 3 OptionParser->frontend.get_default_settings test sites; did not touch test_builder.py/test_pdf_generation.py/test_documentation_configuration.py/test_documentation_usage.py (reserved for Plan 08-02) and did not enable the pyproject.toml filterwarnings guard (reserved for Plan 08-03)."

patterns-established:
  - "Docutils/Sphinx deprecation-sweep fixes are pure 1-2 line mechanical substitutions per RESEARCH.md's empirically-verified fix catalogue - no compatibility shims, no version branching (latest-only forward-port)."

requirements-completed: [API-01, API-02]

coverage:
  - id: D1
    description: "template_engine.py:239 toctree collection uses findall() instead of deprecated traverse(); zero traverse tokens remain in typsphinx/"
    requirement: "API-01"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py -W error::DeprecationWarning -W error::PendingDeprecationWarning (39 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_translator.py's 3 settings-construction sites use frontend.get_default_settings(RstParser) instead of the deprecated OptionParser(...).get_default_values(); definition-list handling unaffected"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "tests/test_translator.py -W error::DeprecationWarning -W error::PendingDeprecationWarning (98 passed)"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py -k definition_list (2 passed)"
        status: pass
    human_judgment: false

# Metrics
duration: 8min
completed: 2026-07-11
status: complete
---

# Phase 08 Plan 01: API-01 traverse()->findall() fix + test_translator.py frontend modernization Summary

**Landed the locked `traverse()`→`findall()` toctree-collection fix in `template_engine.py` and modernized all 3 `docutils.frontend.OptionParser` settings-construction sites in `test_translator.py` to `frontend.get_default_settings()`, both verified warning-free under escalated `DeprecationWarning`/`PendingDeprecationWarning` filters.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-07-11T11:38:00+09:00
- **Completed:** 2026-07-11T11:46:00+09:00
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `typsphinx/template_engine.py:239` toctree collection now calls `doctree.findall(addnodes.toctree)`, mirroring `builder.py:151`'s existing pattern, with the `list(...)` eager-materialization wrapper preserved for downstream `toctree_nodes[0]` indexing.
- `tests/test_translator.py`'s 3 identical settings-construction sites (table dedup test ~line 1647, comment-skip test ~line 1725, raw-multiple-formats test ~line 1845) now use `frontend.get_default_settings(RstParser)` instead of the deprecated `frontend.OptionParser(components=(RstParser,)).get_default_values()`.
- Both files verified zero-deprecation-warning under `-W error::DeprecationWarning -W error::PendingDeprecationWarning`: `test_template_engine.py` (39 passed), `test_translator.py` (98 passed), plus the definition-list subset specifically re-confirmed (`-k definition_list`, 2 passed).

## Task Commits

Each task was committed atomically:

1. **Task 1: Swap template_engine.py toctree traverse() -> findall() (API-01, locked)** - `89888f9` (feat)
2. **Task 2: Modernize test_translator.py 3x OptionParser -> frontend.get_default_settings (API-02)** - `519771a` (test)

**Plan metadata:** (pending — this SUMMARY's own commit)

## Files Created/Modified
- `typsphinx/template_engine.py` - Single-line swap: `list(doctree.traverse(addnodes.toctree))` -> `list(doctree.findall(addnodes.toctree))` at line 239.
- `tests/test_translator.py` - 3x paired substitution: `from docutils.frontend import OptionParser` -> `from docutils import frontend`, and `OptionParser(components=(RstParser,)).get_default_values()` -> `frontend.get_default_settings(RstParser)`.

## Decisions Made
- Scoped strictly to this plan's locked boundary: did not touch `test_builder.py`, `test_pdf_generation.py`, `test_documentation_configuration.py`, or `test_documentation_usage.py` (the remaining 4 deprecation-fix sites from RESEARCH.md's 5-site catalogue) — those are reserved for Plan 08-02 per the phase's wave ordering.
- Did not add the `filterwarnings` guard to `pyproject.toml` — that is Plan 08-03's responsibility, landing after all fix sites are in place (D-02 ordering constraint: guard must find the suite green, not turn it red).

## Deviations from Plan

None - plan executed exactly as written. Both grep-based acceptance criteria and both pytest verification commands passed on the first attempt with no auto-fixes needed.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `template_engine.py` and `test_translator.py` are now clean of `traverse()`/`OptionParser` deprecation warnings, unblocking Plan 08-02 (the remaining 4 test-file fix sites: `builder.app`, `publish_string(writer_name=...)`) and Plan 08-03 (enabling the permanent `filterwarnings` guard).
- No blockers identified for the next plan in this phase.

---
*Phase: 08-api-test-compatibility-sphinx-9-docutils-0-22*
*Completed: 2026-07-11*

## Self-Check: PASSED

- FOUND: typsphinx/template_engine.py
- FOUND: tests/test_translator.py
- FOUND: .planning/phases/08-api-test-compatibility-sphinx-9-docutils-0-22/08-01-SUMMARY.md
- FOUND commit: 89888f9 (Task 1)
- FOUND commit: 519771a (Task 2)
- FOUND commit: ccbd453 (SUMMARY.md)
