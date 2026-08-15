---
phase: 51-two-layer-output-documentation
plan: 01
subsystem: docs
tags: [sphinx, typst, documentation, pytest]

# Dependency graph
requires:
  - phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
    provides: "The wrapper/content split, target-as-path resolution (_resolve_target_stem), and the wrapper-report log line this plan documents"
  - phase: 49-per-master-include-graph-with-state-guarded-includes
    provides: "The state-guarded include mechanism and the standalone-content-compile behaviour this plan cites"
provides:
  - "docs/source/user_guide/output_layout.rst — the two-layer output contract page (wrapper/content split, which file to compile, standalone-content behaviour, bare-target and explicit-path worked examples)"
  - "tests/test_output_layout_docs_gate.py — the permanent SC#3 gate binding published prose to real -b typst build output"
  - "Two new tests/fixtures/output_layout_*_gate/ Sphinx projects, literal copies of measured builds"
affects: [51-02, 51-03, 51-04, 51-05, 51-06]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 4105
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-class docs-gate shape (real -b typst build + never-skipping prose-match class), reused verbatim from tests/test_quickstart_docs_gate.py, with the typst-py import guard dropped entirely per D-12"
    - "Config-example-then-consequence prose shape (code-block immediately followed by prose naming every emitted file), matching configuration.rst"

key-files:
  created:
    - docs/source/user_guide/output_layout.rst
    - tests/test_output_layout_docs_gate.py
    - tests/fixtures/output_layout_bare_target_gate/conf.py
    - tests/fixtures/output_layout_bare_target_gate/index.rst
    - tests/fixtures/output_layout_explicit_path_gate/conf.py
    - tests/fixtures/output_layout_explicit_path_gate/index.rst
  modified:
    - docs/source/user_guide/index.rst

key-decisions:
  - "Split the plan's single conceptual page-write into two atomic task commits matching the plan's own Task 1 (bare target, tracer) / Task 2 (explicit path) structure, rather than writing the whole page in one pass, so the tracer's feedback gate had a real, isolated commit to verify against."

patterns-established:
  - "Pattern 1: Standalone-content-compile behaviour is written as plain declarative prose inside the 'which file to compile' section, never as a .. note:: or .. warning:: admonition (D-08) — this register should be matched by any later phase adding more behaviour claims to this page."

requirements-completed: [DOC-14]

coverage:
  - id: D1
    description: "docs/source/user_guide/output_layout.rst names both the wrapper and content files for the bare-target worked example, states the wrapper is the file to compile, and states the standalone-content-compile behaviour as plain prose with no admonition"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild::test_page_names_the_bare_target_file_set"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_bare_target_emits_wrapper_and_content"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/source/user_guide/output_layout.rst's 'Where the Wrapper Is Written' section publishes the explicit-path worked example (manuals/guide.typ), matching a real build's emitted file set"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild::test_page_names_the_explicit_path_file_set"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_explicit_path_target_writes_the_wrapper_under_its_path"
        status: pass
    human_judgment: false
  - id: D3
    description: "The new page is reachable from docs/source/user_guide/index.rst through both its toctree and its Main Topics definition list"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'output_layout' docs/source/user_guide/index.rst -> 2"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min (active work; excludes the interactive checkpoint wait between Task 1 and Task 2)
completed: 2026-08-15
status: complete
---

# Phase 51 Plan 01: Two-Layer Output Documentation — Bare and Explicit-Path Worked Examples Summary

**New `output_layout.rst` page and a permanent real-build gate proving the wrapper/content split, which file to compile, and target-as-path behaviour for both a bare target and an explicit-path target.**

## Performance

- **Duration:** ~20 min active work (interactive checkpoint between tasks excluded)
- **Started:** 2026-08-14T23:42:00+09:00 (approx.)
- **Completed:** 2026-08-15T00:03:40+09:00
- **Tasks:** 2 (Task 1 tracer + Task 2 expansion)
- **Files modified:** 7 (1 modified, 6 created)

## Accomplishments

- Created `docs/source/user_guide/output_layout.rst` with three sections: "Wrapper and Content Files" (the split itself), "Which File to Compile" (points at the builder's own `compile these:` log line, plus the standalone-content-compile behaviour as plain prose per D-08), and "Where the Wrapper Is Written" (bare target vs. explicit path, both worked examples taken verbatim from `51-RESEARCH.md` Part C builds 1 and 2)
- Created a new permanent gate, `tests/test_output_layout_docs_gate.py`, with two classes: `TestOutputLayoutBuildFileSets` (real `-b typst` `sys.executable -m sphinx` subprocess builds, asserting the exact emitted `.typ` file set) and `TestPublishedOutputLayoutTextMatchesBuild` (reads the page from disk, asserts the prose names the same filenames). Carries no `typst-py` import and never skips (D-10/D-11/D-12)
- Created two new fixtures under `tests/fixtures/`: `output_layout_bare_target_gate/` and `output_layout_explicit_path_gate/`, each a literal copy of a measured `51-RESEARCH.md` build
- Added `output_layout` to both `docs/source/user_guide/index.rst` lists (toctree and hand-written Main Topics definition list)

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "which file do I compile" — the bare-target path only (tracer)** - `42be4054` (feat)
2. **Task 2: Expand to an explicit path target — the wrapper lands where the user asked** - `f57f5d41` (feat)

**Plan metadata:** (this commit)

## Files Created/Modified

- `docs/source/user_guide/output_layout.rst` - New page: two-layer output contract, worked examples
- `docs/source/user_guide/index.rst` - Added `output_layout` toctree entry and Main Topics entry
- `tests/test_output_layout_docs_gate.py` - New permanent SC#3 gate (4 tests)
- `tests/fixtures/output_layout_bare_target_gate/conf.py` - Bare-target fixture config
- `tests/fixtures/output_layout_bare_target_gate/index.rst` - Bare-target fixture source
- `tests/fixtures/output_layout_explicit_path_gate/conf.py` - Explicit-path fixture config
- `tests/fixtures/output_layout_explicit_path_gate/index.rst` - Explicit-path fixture source

## Decisions Made

- Followed the plan's own task split (bare-target tracer first, explicit-path expansion second) as two separate commits rather than writing the whole page and gate in one pass — this let the tracer's mandatory feedback gate (the checkpoint between Task 1 and Task 2) verify a real, isolated commit rather than a partial in-progress diff.
- Corrected a self-inflicted acceptance-criteria miss during Task 1: the module docstring originally used the literal substrings `import typst` and `typstpdf` while *explaining* why the precedent's skip guard was NOT copied — this collided with the task's own `grep -c 'import typst'` / `grep -c 'typstpdf'` == 0 acceptance criteria. Reworded the docstring to describe the same rationale without those literal strings. [Rule 1 — self-caught before commit, no separate fix commit needed.]
- Similarly caught and fixed a duplicate `manuals/guide.typ` occurrence in the Task 2 fixture's header comment before committing, keeping the fixture's `conf.py` at exactly one occurrence of the load-bearing config line per the task's own acceptance criterion.

## Deviations from Plan

None - plan executed exactly as written. Both self-caught issues above were caught and fixed before their respective task commits, not after, so no separate deviation-fix commit was needed.

## Issues Encountered

None beyond the two self-caught acceptance-criteria misses documented above (resolved pre-commit).

## Checkpoint

Task 1 is `type="tracer"`. Per the tracer feedback gate (auto mode was off: `workflow.auto_advance=false`, `workflow._auto_chain_active=false`), the executor stopped after committing Task 1 and returned a `checkpoint:human-verify` for the tracer's proven slice (page prose + gate + fixture). The coordinator relayed the user's "verified" response with no corrections requested, and execution resumed at Task 2.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `output_layout.rst`'s "Wrapper and Content Files" and "Which File to Compile" sections are the shape later plans (51-02..51-06) extend: 51-03 adds the refusal cases, 51-04 the collision rules, 51-05 the shared-child composition. The plain-prose register D-08 established for the standalone-content-compile claim (no admonition) should be matched by any behaviour claim those later plans add to this same page.
- `tests/test_output_layout_docs_gate.py`'s two-class shape (`TestOutputLayoutBuildFileSets` / `TestPublishedOutputLayoutTextMatchesBuild`) and its module-level constants (`REPO_ROOT`, `FIXTURES_DIR`, `OUTPUT_LAYOUT_RST_PATH`, `BARE_TARGET_FIXTURE_DIR`, `EXPLICIT_PATH_FIXTURE_DIR`) are ready for 51-03/51-04/51-06 to extend with the additional constants and methods `51-01-PLAN.md`'s `<artifacts_this_phase_produces>` names (`REFUSED_PARENT_FIXTURE_DIR`, `SELF_COLLISION_FIXTURE_DIR`, `THREE_MASTER_FIXTURE_DIR`, etc.) — those constants and fixtures do not exist yet; this plan created only the two the tracer and its expansion task needed.
- Full suite verified green (1092 passed, 73 deselected) with zero lines changed under `typsphinx/`, `black --check` clean on all new/modified files, `mypy typsphinx/` clean (unaffected).

## Self-Check: PASSED

All created files confirmed present on disk (`output_layout.rst`, `test_output_layout_docs_gate.py`,
both fixture `conf.py` files, this SUMMARY.md). All three commits (`42be4054`, `f57f5d41`, `89bd1d6b`)
confirmed present in `git log`.

---
*Phase: 51-two-layer-output-documentation*
*Completed: 2026-08-15*
