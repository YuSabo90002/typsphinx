---
phase: 24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part
plan: 01
subsystem: config
tags: [sphinx, config-cleanup, dead-code-removal, typsphinx]

# Dependency graph
requires:
  - phase: v0.6.2 CONF-01 removal (typst_output_dir / typst_author_params)
    provides: the treatment template mirrored here (registration + docs/examples/README/test surfaces removed, historical CHANGELOG left intact)
provides:
  - Removal of the registered-but-inert typst_toctree_defaults config value from every user-facing and code surface
affects: [phase-27-docs-alignment, phase-28-release-prep]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dead-config removal pattern: delete add_config_value registration line, surgically excise docs/README/examples mentions, delete registration-only test files, leave historical CHANGELOG lines intact"

key-files:
  created: []
  modified:
    - typsphinx/__init__.py
    - README.md
    - examples/advanced/conf.py
    - examples/advanced/README.md
    - docs/configuration.rst
    - tests/test_documentation_configuration.py
  deleted:
    - tests/test_config_toctree_defaults.py

key-decisions:
  - "docs/configuration.rst surgically edited, not deleted (D-03) — whole-file orphan removal deferred to Phase 27 / DOC-06"
  - "CHANGELOG.md deliberately untouched (D-02) — the CHANGELOG.md:553 historical hit remains, matching the v0.6.2 CONF-01 precedent"
  - "No GATE-01 typst.compile() regression fixture required — pure removal with zero config-to-output change (D-04)"

patterns-established:
  - "Dead-config sweep: registration line + docs/examples/README/test surfaces removed together in one plan; historical CHANGELOG entries left as immutable release history"

requirements-completed: [CONF-05]

coverage:
  - id: D1
    description: "typst_toctree_defaults add_config_value registration removed from typsphinx/__init__.py; extension still imports and both builders (TypstBuilder, TypstPDFBuilder) still register"
    requirement: "CONF-05"
    verification:
      - kind: unit
        ref: "python -c 'import typsphinx; from typsphinx.builder import TypstBuilder, TypstPDFBuilder' (manual verification command)"
        status: pass
    human_judgment: false
  - id: D2
    description: "typst_toctree_defaults removed from README.md, examples/advanced/conf.py, examples/advanced/README.md, and surgically from docs/configuration.rst (file kept); examples/advanced still builds green via the typst builder"
    requirement: "CONF-05"
    verification:
      - kind: integration
        ref: "python -m sphinx -b typst examples/advanced /tmp/tt24-adv (manual build verification command)"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_config_toctree_defaults.py deleted (registration-only coverage of the removed value); required_configs list entry dropped in test_documentation_configuration.py; full existing suite stays green"
    requirement: "CONF-05"
    verification:
      - kind: unit
        ref: "tests/test_documentation_configuration.py::test_configuration_documents_all_config_values"
        status: pass
      - kind: unit
        ref: "clean-signal pytest run (excluding 5 pre-existing environmentally-broken integration/example files): 519 passed, 1 skipped"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-23
status: complete
---

# Phase 24 Plan 01: Delete typst_toctree_defaults dead config Summary

**Removed the registered-but-inert `typst_toctree_defaults` Sphinx config value from all seven code/doc/test surfaces (registration line, README, examples, surgically-edited docs/configuration.rst, deleted test file) while leaving the historical CHANGELOG.md entry untouched.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-23T13:15:00Z (approx)
- **Completed:** 2026-07-23T13:40:19Z
- **Tasks:** 3
- **Files modified:** 6 modified, 1 deleted

## Accomplishments
- Deleted the single `app.add_config_value("typst_toctree_defaults", …)` line from `typsphinx/__init__.py`; extension imports cleanly and both `TypstBuilder`/`TypstPDFBuilder` still register.
- Removed every `typst_toctree_defaults` mention from README.md, `examples/advanced/conf.py`, and `examples/advanced/README.md`; `examples/advanced` still builds green via `python -m sphinx -b typst`.
- Surgically excised the "Table of Contents" section and the toctree block in the combined example from `docs/configuration.rst` while keeping the file intact (D-03) — other config sections (e.g. `typst_package`, 8 mentions) remain untouched.
- Deleted `tests/test_config_toctree_defaults.py` (registration-only coverage of the now-removed value) and dropped the `"typst_toctree_defaults"` entry from `required_configs` in `test_documentation_configuration.py`.
- Confirmed CHANGELOG.md is completely untouched across all 3 task commits (D-02) — the historical `CHANGELOG.md:553` listing remains as intended.

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove the config-value registration from typsphinx/__init__.py** - `f8abfc6` (feat)
2. **Task 2: Remove the value from all user-facing docs & examples (surgical on docs/configuration.rst)** - `d55f5a5` (docs)
3. **Task 3: Delete the registration-only test file, drop the doc-list entry, prove green suite** - `d48b019` (test)

_Note: no TDD tasks in this plan — pure deletion of an inert config value, no new behavior to test-first._

## Files Created/Modified
- `typsphinx/__init__.py` - Removed the `typst_toctree_defaults` `add_config_value` registration line; other 11 registrations and both `add_builder` calls untouched
- `README.md` - Dropped the `typst_toctree_defaults` config bullet from the options list
- `examples/advanced/conf.py` - Removed the `typst_toctree_defaults = {…}` block and its comment header
- `examples/advanced/README.md` - Removed the matching doc snippet and comment header
- `docs/configuration.rst` - Surgically removed the "Table of Contents" section (heading + subsection body/example) and the toctree block inside the combined `conf.py` example; file kept, all other sections intact
- `tests/test_documentation_configuration.py` - Dropped the `"typst_toctree_defaults"` entry from `required_configs`
- `tests/test_config_toctree_defaults.py` - Deleted (registration-only test coverage, no longer applicable)

## Decisions Made
- Mirrored the v0.6.2 CONF-01 (`typst_output_dir`/`typst_author_params`) removal precedent exactly: registration line + docs/examples/README/test surfaces removed, historical CHANGELOG lines left intact.
- `docs/configuration.rst` kept as a file per D-03 — whole-file orphan deletion belongs to Phase 27 (DOC-06), not this phase.
- No GATE-01 `typst.compile()` regression fixture required per D-04 — this is a pure config-registration removal with zero consumers (`template_engine.extract_toctree_options` reads toctree options from the docutils node, never from `app.config.typst_toctree_defaults`), so there is no config→output behavior change to regression-test.

## Deviations from Plan

**1. [Documentation-only, no code impact] Plan's stated `add_config_value` line-count baseline was off by one**

- **Found during:** Task 1 verification
- **Issue:** The plan's acceptance criteria state `grep -c 'add_config_value' typsphinx/__init__.py` should return `10` ("was 11" before removal). The actual pre-removal count (confirmed via `git show HEAD:typsphinx/__init__.py`) was 12 matching lines, because 11 distinct config values are registered via 12 lines (one call, `typst_template_function`, spans 3 lines but only its opening line matches the grep pattern) plus the one `typst_toctree_defaults` line being removed. After removing exactly the one `typst_toctree_defaults` line, the count is 11, not 10.
- **Fix:** No code fix needed — this is purely a numeric assertion in the plan text being off by one line, not an execution defect. Verified correctness via the substantive checks instead: `grep -n 'typst_toctree_defaults' typsphinx/__init__.py` returns zero hits, `import typsphinx` succeeds, both builder classes still import, and a line-by-line diff (`git diff f8abfc6~1 f8abfc6`) shows exactly one line deleted with all ten other `add_config_value` calls and both `add_builder` calls untouched.
- **Files modified:** None (verification-only finding, not a code change).
- **Verification:** `git show HEAD:typsphinx/__init__.py | grep -c add_config_value` → 12 (before); `grep -c add_config_value typsphinx/__init__.py` → 11 (after) — a clean one-line delta, matching the plan's actual intent (remove exactly one registration) even though its stated absolute numbers were off.
- **Committed in:** f8abfc6 (Task 1 commit; no separate fix commit needed)

---

**Total deviations:** 1 documentation-note-only (plan miscount, not a code defect)
**Impact on plan:** None on functional correctness — the actual deletion (exactly one registration line, all else intact) was verified via `git diff`, import checks, and builder registration checks rather than the plan's slightly-off absolute count.

## Issues Encountered
None. All three tasks executed cleanly on the first attempt; no auto-fixes, no blocking issues, no auth gates.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CONF-05 is fully satisfied: grep-zero on all SC#1 enumerated surfaces (`typsphinx/__init__.py`, `README.md`, `examples/advanced/`, `docs/configuration.rst`, `tests/`), with the `CHANGELOG.md:553` historical hit intentionally remaining (D-02).
- `docs/configuration.rst` still exists with all other config sections intact, ready for Phase 27 (DOC-06) to handle the whole-file orphan deletion decision.
- CHANGELOG.md is unchanged; the `[Unreleased] → ### Removed` note for this removal is deferred to Phase 28 (release-prep), batched with the v0.6.3 version bump, per D-02.
- No blockers for subsequent phases in this milestone.

## Self-Check: PASSED

- FOUND: typsphinx/__init__.py
- FOUND: docs/configuration.rst
- FOUND (deleted as expected): tests/test_config_toctree_defaults.py
- FOUND: .planning/phases/24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part/24-01-SUMMARY.md
- FOUND commit: f8abfc6 (Task 1)
- FOUND commit: d55f5a5 (Task 2)
- FOUND commit: d48b019 (Task 3)

---
*Phase: 24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part*
*Completed: 2026-07-23*
