---
phase: 44-typst-documents-default-derivation-builder-input-hardening
plan: 01
subsystem: config
tags: [sphinx, typst, config, builder, latex-parity]

# Dependency graph
requires:
  - phase: 43-table-state-correctness-nested-tables-empty-title-anchors
    provides: the "follow the builder Sphinx already ships, measured on identical input" method reused throughout
provides:
  - "_default_typst_documents(config) — the Sphinx-native callable default for typst_documents (CONF-08)"
  - "typst_documents registered as a callable default in typsphinx/__init__.py, mirroring latex_documents"
  - "Two new fixtures + a gate module proving the unset path produces a PDF and the explicit path still wins"
  - "44-GATE-EVIDENCE-01.md with RED (pre-change), GREEN (post-change), and SC#2 evidence, plus the RED commit SHA"
affects: [44-02-builder-input-hardening, 44-03-changelog-evidence, 44-04-repo-wide-test-audit, 45-documentation-currency]

# Actuals (#2632)
actuals:
  tokens: 10801
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Callable Sphinx config default (app.add_config_value(name, <callable>, ...)) mirroring sphinx.builders.latex.default_latex_documents"

key-files:
  created:
    - tests/fixtures/default_typst_documents_gate/conf.py
    - tests/fixtures/default_typst_documents_gate/index.rst
    - tests/fixtures/explicit_typst_documents_wins_gate/conf.py
    - tests/fixtures/explicit_typst_documents_wins_gate/index.rst
    - tests/test_default_typst_documents_gate.py
    - tests/test_default_typst_documents_derivation.py
  modified:
    - typsphinx/builder.py
    - typsphinx/__init__.py
    - tests/test_builder.py
    - tests/test_builder_requirement13.py
    - .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-01.md

key-decisions:
  - "D-01/D-02/D-04 implemented verbatim as measured in 44-CONTEXT.md: the derived entry is (root_doc, make_filename_from_project(project) + '.typ', project, author, 'typst'), registered as the callable default replacing the literal []."
  - "Task 2's Route 1 (rename assertion to the derived stem) was viable for both test_builder.py failures — the measured failure was purely a filename mismatch, not a template-application exception, so Route 2 (pinning typst_documents=[]) was not needed."
  - "Deviation: the planning-time repo-wide census (all 103 fixture conf.py files already set typst_documents) did not cover conf.py content written inline by a test fixture function. tests/test_builder_requirement13.py's multifile_srcdir fixture also omitted typst_documents; its 3 affected assertions were fixed the same way (rename to derived stem + CONF-08 comment) to satisfy this plan's own full-suite verification requirement."

requirements-completed: [CONF-08]

coverage:
  - id: D1
    description: "With typst_documents unset, sphinx-build -b typstpdf produces a PDF named via make_filename_from_project(project), with the full template applied to the root document"
    requirement: "CONF-08"
    verification:
      - kind: integration
        ref: "tests/test_default_typst_documents_gate.py::TestDefaultTypstDocumentsDerivationGate::test_unset_typst_documents_produces_pdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "An explicitly-set typst_documents produces exactly the targets it names and nothing else (SC#2)"
    requirement: "CONF-08"
    verification:
      - kind: integration
        ref: "tests/test_default_typst_documents_gate.py::TestDefaultTypstDocumentsDerivationGate::test_explicit_typst_documents_wins"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-01's degradation table, the derived 5-tuple shape, and the unset/explicit-empty/explicit-same-target/explicit-two-entry distinctions are pinned by unit tests"
    requirement: "CONF-08"
    verification:
      - kind: unit
        ref: "tests/test_default_typst_documents_derivation.py (13 tests, incl. TestDegradationTable::test_derived_target_name[8 rows])"
        status: pass
    human_judgment: false
  - id: D4
    description: "The two (plus 3 discovered) existing tests that encoded the old []-default are updated deliberately with the measured reason recorded"
    verification:
      - kind: unit
        ref: "tests/test_builder.py::test_write_doc_creates_output_file, tests/test_builder.py::test_write_doc_generates_typst_content, tests/test_builder_requirement13.py (3 tests)"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-08-04
status: complete
---

# Phase 44 Plan 01: `typst_documents` Default Derivation Summary

**A project following the Sphinx Quick Start with `typst_documents` unset now produces a real PDF named via `make_filename_from_project(project)` — mirroring `sphinx.builders.latex.default_latex_documents` — while an explicit `typst_documents` still wins end-to-end.**

## Performance

- **Duration:** ~15 min (RED commit 14:11 JST → final commit 14:22 JST, plus setup/read time before the first commit)
- **Started:** 2026-08-04T05:xx:xxZ (session start)
- **Completed:** 2026-08-04T05:22:45Z
- **Tasks:** 3 (all completed)
- **Files modified:** 11 (6 created, 5 modified)

## Accomplishments
- `typst_documents` now has a Sphinx-native callable default (`_default_typst_documents` in `typsphinx/builder.py`), registered in `typsphinx/__init__.py` in place of the literal `[]` — an unset config now resolves to a single derived master entry instead of silently compiling nothing.
- Real-`sphinx-build` subprocess gate (`tests/test_default_typst_documents_gate.py`) proves both directions end-to-end: the unset path produces `quickstartdefaultgate.typ`/`.pdf` with the full template applied, and an explicit `typst_documents` naming `manual.typ` produces exactly that and nothing else (SC#2).
- Unit module (`tests/test_default_typst_documents_derivation.py`, 13 tests) pins D-01's 8-row degradation table (including the three degenerate-input rows that collapse to Sphinx's own `sphinx` sentinel), the derived 5-tuple shape, and the unset/explicit-empty/explicit-same-target/explicit-two-entry distinctions through real `SphinxTestApp` config resolution.
- A full RED→GREEN evidence trail recorded in `44-GATE-EVIDENCE-01.md`, including the RED commit SHA (`eeb930429c2608c5245f2769fc6b7edbbed206c5`) that plan 44-03 consumes for its SC#4 two-build record.

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED half): "add RED gate for unset typst_documents (CONF-08)"** - `eeb9304` (test)
2. **Task 1 (GREEN half): "derive typst_documents default from root_doc/project/author"** - `1409591` (feat)
3. **Task 2: "pin D-01 degradation table and repair test_builder.py (CONF-08)"** - `dbcc07c` (test)
4. **Task 3: "prove an explicit typst_documents still wins end-to-end (SC#2)"** - `38e73b4` (test)

_Task 1's tracer verification (the RED→GREEN gate) is folded into its own two commits rather than a separate metadata commit, per the tracer feedback protocol — both the RED and GREEN sides carry real, atomic, tested work._

**Plan metadata:** _final metadata commit is the orchestrator's responsibility in worktree mode; not made by this executor._

## Files Created/Modified
- `typsphinx/builder.py` - Added `_default_typst_documents(config)`, the callable default mirroring `default_latex_documents`; extended the `sphinx.util.osutil` import with `make_filename_from_project` and added `from sphinx.config import Config` for the type hint
- `typsphinx/__init__.py` - `add_config_value("typst_documents", ...)`'s second positional argument changed from `[]` to `_default_typst_documents`
- `tests/fixtures/default_typst_documents_gate/conf.py`, `index.rst` - The repo's only fixture that deliberately omits `typst_documents`
- `tests/fixtures/explicit_typst_documents_wins_gate/conf.py`, `index.rst` - Explicit single-entry `typst_documents` naming a target the derivation could never produce
- `tests/test_default_typst_documents_gate.py` - Real-`sphinx-build` subprocess gate, 2 tests (unset-path success, explicit-wins)
- `tests/test_default_typst_documents_derivation.py` - Unit module, 13 tests (degradation table, tuple shape, unset/explicit-empty/adjacency/ordering resolution)
- `tests/test_builder.py` - `test_write_doc_creates_output_file` and `test_write_doc_generates_typst_content` renamed their assertion target from `index.typ` to `testproject.typ` with a CONF-08 traceability comment
- `tests/test_builder_requirement13.py` - 3 tests (`test_builder_generates_independent_typ_files`, `test_toctree_with_nested_paths_generates_correct_includes`, `test_toctree_with_missing_document_warning`) similarly renamed `index.typ` → `multi-filetest.typ` (see Deviations)
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-01.md` - RED (section 1), RED commit SHA (section 2), GREEN (section 3), existing-test-update audit (section 4), SC#2 evidence (section 5), and this plan's two deviations (section 6)

## Decisions Made
- Implemented D-01/D-02/D-04 exactly as measured in `44-CONTEXT.md`/`44-PATTERNS.md`: no deviation from the locked derivation shape or registration signature.
- Task 2's rename route (not the `typst_documents = []` pinning fallback) was taken for both `test_builder.py` failures, since the measured pre-change failure was a clean filename mismatch, not a template-application exception inside the unit-level harness.
- Did not touch `typst_documents` entry elements `[2]`/`[3]`/`[4]` (title/author/class) anywhere in production code, per the plan's prohibition — they remain emitted for LaTeX shape-parity only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1/3 - Planning-time measurement gap] `tests/test_builder_requirement13.py` also encoded the old `[]`-default**
- **Found during:** Task 3 (running the plan-level `<verification>`'s full-suite pass)
- **Issue:** `44-CONTEXT.md`'s repo-wide census ("all 103 `conf.py` files that mention `typst_documents` already set it") only covered `tests/fixtures/*/conf.py` files on disk. It missed `conf.py` content written inline by a test fixture function — `multifile_srcdir` in `tests/test_builder_requirement13.py` sets `project = 'Multi-File Test'` and omits `typst_documents`, so 3 of its dependent tests asserted on the old literal `index.typ` and failed once the derivation landed.
- **Fix:** Renamed the assertion target to the derived stem (`make_filename_from_project("Multi-File Test")` → `multi-filetest.typ`, confirmed live) with a CONF-08 traceability comment on each of the 3 affected tests, mirroring the exact treatment `test_builder.py`'s two tests already got in Task 2.
- **Files modified:** `tests/test_builder_requirement13.py`
- **Verification:** `uv run python -m pytest tests/test_builder_requirement13.py -q` → `5 passed`; full suite subsequently green (852 passed, 1 skipped)
- **Committed in:** `38e73b4` (Task 3 commit)

**2. [Rule 3 - Blocking, environment] Worktree venv's `uv`/`ruff` needed the documented NixOS-sandbox shim**
- **Found during:** Task 3 (running the plan-level full-suite + lint verification)
- **Issue:** `uv sync --extra dev` installs generic-linux ELF wheels for `uv` and `ruff` into a fresh worktree venv; NixOS cannot exec them directly, producing 45-48 pre-existing environmental failures in `tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` (they invoke `subprocess.run(["uv","run","sphinx-build",...])`) that were unrelated to this plan's diff but blocked getting a trustworthy full-suite signal.
- **Fix:** `ln -sf <nix-store uv> .venv/bin/uv` and `ln -sf <main-tree's already-patchelf'd ruff> .venv/bin/ruff`, each verified with `.venv/bin/<tool> --version` actually executing before re-running the suite (per this project's established runbook).
- **Files modified:** None (venv contents are gitignored; no commit needed)
- **Verification:** `uv run python -m pytest -q` → `852 passed, 1 skipped`; `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` all clean
- **Committed in:** N/A (environment-only fix, no repository change)

---

**Total deviations:** 2 auto-fixed (1 planning-time measurement gap corrected under Rule 1/3, 1 environmental blocking issue resolved under Rule 3)
**Impact on plan:** Both were necessary to satisfy this plan's own full-suite verification requirement. No scope creep — the test-file fix is the same mechanical rename pattern the plan already prescribed for `test_builder.py`; the venv shim touches no repository file.

## Issues Encountered
None beyond the two deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CONF-08 is fully implemented and evidenced. Plan 44-02 (builder input hardening, BLD-01) can proceed — it edits the same `TypstPDFBuilder.finish()` method but a different code path (the non-`str` docname guard), with no overlap with this plan's diff.
- Plan 44-03 (the SC#4 two-build CHANGELOG-source record) has its RED commit SHA (`eeb930429c2608c5245f2769fc6b7edbbed206c5`) ready to consume.
- Plan 44-04 (repo-wide existing-test audit) should be aware that the inline-`conf.py`-in-test-fixture pattern (not just `tests/fixtures/*/conf.py` files) is a real source of additional affected tests — this plan found and fixed one instance (`test_builder_requirement13.py`); a full audit should search for other `write_text(...conf.py...)` calls that omit `typst_documents`.
- No blockers.

---
*Phase: 44-typst-documents-default-derivation-builder-input-hardening*
*Completed: 2026-08-04*

## Self-Check: PASSED

All key files confirmed present on disk (`typsphinx/builder.py`,
`typsphinx/__init__.py`, both new fixture `conf.py`s, both new test
modules, `44-GATE-EVIDENCE-01.md`, this summary) and all 5 commits
(`eeb9304`, `1409591`, `dbcc07c`, `38e73b4`, `ef5c83d`) confirmed present
in `git log --oneline --all`. No missing items.
