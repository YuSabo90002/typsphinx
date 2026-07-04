---
phase: 02-verify-the-green-baseline
plan: 01
subsystem: testing
tags: [pytest, typst, preview-packages, regex, tox, mypy, twine, docs-pdf]

# Dependency graph
requires:
  - phase: 01-pin-runtime-dependencies-to-known-good
    provides: "Pinned uv.lock (typst==0.14.9, sphinx<9, docutils<0.22) that resolves the kai break"
provides:
  - "tests/test_preview_version_sync.py — automated guard against future @preview 3-way version desync (D-03)"
  - "Recorded local pre-check results confirming the pinned tree is green before Plan 02's authoritative push (D-01)"
affects: [02-02-push-and-observe-ci]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Regex-based cross-file version-sync guard test (stdlib re + pathlib only, no new dependency)"

key-files:
  created: [tests/test_preview_version_sync.py]
  modified: []

key-decisions:
  - "Scoped the extraction regex to actual `#import \"@preview/...\"` Typst statements (not bare text matches) after discovering it matched a docstring example (`@preview/charged-ieee:0.1.0` in template_engine.py's docstring) as a false-positive divergence"
  - "Used `tox -e cov` (system Python 3.13, no interpreter pin) as the local pre-check vehicle instead of `tox -e py311`, because this NixOS dev machine cannot execute tox-uv's standalone-downloaded CPython builds (dynamically linked against a generic-Linux dynamic linker path NixOS does not provide) — documented as a local-environment-only finding, not a code regression"

patterns-established:
  - "Cross-declaration-site sync guard: parse each site with the same regex, compare dicts, fail with a diagnostic listing every file's value for the divergent key"

requirements-completed: [TEST-01, TEST-02, TEST-03, TEST-04, DOCS-01]

coverage:
  - id: D1
    description: "@preview version-sync guard test: two pytest tests (identity across 3 files, all-4-packages-present) protecting the writer.py / template_engine.py / templates/base.typ hazard (D-03)"
    requirement: "TEST-01"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_all_four_packages_declared"
        status: pass
    human_judgment: false
  - id: D2
    description: "Local pre-check: full test suite (402 tests) green via tox -e cov on system Python 3.13, including the 8 PDF-compilation integration tests and the new sync test"
    requirement: "TEST-01"
    verification:
      - kind: integration
        ref: "uv run tox -e cov (402 passed)"
        status: pass
      - kind: integration
        ref: "uv run pytest tests/test_integration_advanced.py::TestPDFGenerationIntegration tests/test_integration_nested_toctree.py::TestE2ETypstCompilation -v (8 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "mypy type check clean (TEST-04) and packaging check clean (uv build + twine check PASSED, TEST-04)"
    requirement: "TEST-04"
    verification:
      - kind: other
        ref: "uv run tox -e type (Success: no issues found in 6 source files)"
        status: pass
      - kind: other
        ref: "uv build && uv run twine check dist/* (both PASSED)"
        status: pass
    human_judgment: false
  - id: D4
    description: "docs-pdf produces a PDF locally, resolving the previously-missing-PDF failure ahead of Plan 02's authoritative docs.yml run (DOCS-01 pre-check)"
    requirement: "DOCS-01"
    verification:
      - kind: integration
        ref: "uv run tox -e docs-pdf (Generated PDF: docs/_build/pdf/index.pdf, 2.3MB)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The full tox matrix envs (py311 etc.) could not be exercised on this dev machine due to a NixOS-specific local environment limitation, unrelated to the Phase 1 pin — surfaced as an explicit finding per D-04, not silently worked around"
    verification: []
    human_judgment: true
    rationale: "This is an environment constraint of the local machine (NixOS cannot run tox-uv's generic-Linux standalone CPython downloads), not a code defect. It cannot be proven green locally; the authoritative confirmation is Plan 02's observed GitHub Actions run on standard runners (D-01), which is unaffected by this local limitation. A human/verifier should be aware this pre-check substituted `tox -e cov` (system Python) for `tox -e py311` and treat that substitution as informational, not a gap in Plan 02's authoritative check."

# Metrics
duration: 5min
completed: 2026-07-04
status: complete
---

# Phase 2 Plan 1: Version-Sync Guard Test and Local Pre-Check Summary

**Added a stdlib-only regex guard test for the 3-way `@preview` version-sync hazard and ran the full local pre-check (tests, coverage, mypy, packaging, docs-pdf, 8 PDF integration tests) green on the Phase 1 pinned tree.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-04T08:16:27Z
- **Completed:** 2026-07-04T08:20:31Z
- **Tasks:** 2 completed
- **Files modified:** 1 created (tests/test_preview_version_sync.py)

## Accomplishments
- `tests/test_preview_version_sync.py` added with two tests: an identity check comparing parsed `@preview` package-to-version mappings across `typsphinx/writer.py`, `typsphinx/template_engine.py`, and `typsphinx/templates/base.typ`, and a presence check that all four expected packages (codly, codly-languages, mitex, gentle-clues) are declared in each file
- Verified the identity test fails with a diagnostic message naming the divergent package and per-file versions, via a temporary simulated single-file desync (bumped mitex in `base.typ` only, confirmed the failure, reverted cleanly)
- Full local pre-check run on the Phase 1 pinned tree: `tox -e cov` (402 tests passed, 92% coverage), `tox -e type` (mypy clean), `uv build` + `twine check` (both PASSED), `tox -e docs-pdf` (PDF generated at `docs/_build/pdf/index.pdf`), and the named PDF-compilation integration tests (8 passed)

## Task Commits

1. **Task 1: Add the @preview version-sync guard test (D-03)** - `e97cd43` (test)
2. **Task 2: Run the local pre-check on the pinned tree (D-01)** - no commit (verification-only task; no files changed — build artifacts are gitignored and were cleaned up after inspection)

**Plan metadata:** pending (this docs commit, made after this SUMMARY)

## Files Created/Modified
- `tests/test_preview_version_sync.py` - New guard test: `_extract_preview_versions()` helper parses `#import "@preview/<name>:<version>"` Typst import statements via regex; `test_preview_versions_identical_across_declaration_sites` compares the three files against each other (not a hardcoded oracle); `test_all_four_packages_declared` guards against a vacuous pass from a dropped import

## Decisions Made
- Scoped the extraction regex to require the `#import "..."` prefix, not a bare `@preview/<name>:<version>` substring match anywhere in the file — the naive version matched a docstring example (`@preview/charged-ieee:0.1.0`) in `template_engine.py`'s docstring, which is unrelated to the four essential imports and would have produced a permanent false-positive divergence. Fixed inline as a Rule 1 auto-fix (bug in code written in this same task) before the task's commit.
- Substituted `tox -e cov` (uses the system Python, no `-p` interpreter pin) for `tox -e py311` in the pre-check, because this NixOS dev machine cannot execute tox-uv's downloaded standalone CPython 3.11 build (`Could not start dynamically linked executable` — NixOS does not provide the generic-Linux dynamic linker path these builds expect). `tox -e cov` runs the identical `pytest tests/` command set plus coverage instrumentation, so it exercises the same test surface (including the new sync test and the 8 PDF integration tests) that `py311` would have. This is documented as a local-environment-only substitution, not a code gap — the authoritative multi-OS/multi-Python confirmation remains Plan 02's observed GitHub Actions run (D-01).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed overly-broad extraction regex causing a false-positive version divergence**
- **Found during:** Task 1 (first pytest run of the new test)
- **Issue:** The initial regex `@preview/(name):(version)` matched any bare `@preview/<name>:<version>` substring in a file's raw text, including a docstring example in `template_engine.py` (`e.g., "@preview/charged-ieee:0.1.0"`) that documents the `typst_package` config option format. This made `charged-ieee` appear as a package present in `template_engine.py` but absent from `writer.py`/`base.typ`, failing the identity test on a phantom divergence unrelated to the real 4-package hazard.
- **Fix:** Anchored the regex to require the `#import "..."` prefix (`#import\s+"@preview/(name):(version)"`), so only actual Typst import statements are extracted, not comment/docstring mentions.
- **Files modified:** tests/test_preview_version_sync.py
- **Verification:** Re-ran `uv run pytest tests/test_preview_version_sync.py -v` — both tests pass; re-ran the simulated single-file desync (bumping `mitex` in `base.typ`) and confirmed the identity test still fails with the correct diagnostic.
- **Committed in:** e97cd43 (Task 1 commit — fix applied before commit, not a separate commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary correctness fix for the new test itself; no scope creep, no production code touched.

## Issues Encountered
- **Local NixOS environment cannot run `tox -e py311`/`py39`/`py310`/`py312`:** tox-uv's `uv sync --locked -p cpython3.11` step fails with `Could not start dynamically linked executable ... NixOS cannot run dynamically linked executables intended for generic linux environments out of the box` (exit 127). This is a pre-existing constraint of this specific development machine, unrelated to the Phase 1 pin or any Phase 2 code change — it is not a new regression to fix, and no GitHub Actions runner (Ubuntu/macOS/Windows, standard non-NixOS environments) will hit it. Substituted `tox -e cov`, which runs on the ambient system Python (3.13, no `-p` pin) and executes the same `pytest tests/` surface with coverage instrumentation — 402 tests passed, including the new sync test and both integration test classes. Flagged as coverage entry D5 (`human_judgment: true`) for verifier awareness; per D-04 this is a finding to surface, not silently patch, and it does not block Plan 02's push since Plan 02's GitHub Actions observation is the authoritative check (D-01).
- **PDF integration test count is 8, not 7:** the plan and phase context both describe "the 7 PDF-compilation integration tests" for `tests/test_integration_advanced.py::TestPDFGenerationIntegration` + `tests/test_integration_nested_toctree.py::TestE2ETypstCompilation`. Collection shows 4 tests in each class (8 total), not 7. All 8 passed; this is a minor count discrepancy in the plan's documentation, not a test failure — noted for accuracy, no action needed.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tests/test_preview_version_sync.py` is committed and will run automatically under the standard pytest collection in Plan 02's pushed CI matrix (TEST-01) and coverage job (TEST-03) — no separate CI wiring needed.
- The pinned tree passes every locally-provable pre-check surface (tests, coverage, mypy, packaging, docs-pdf, PDF integration tests), de-risking Plan 02's push. Plan 02 must still push and observe the real GitHub Actions run (12-job matrix across 3 OS, Codecov upload, `docs.yml` end-to-end) as the authoritative definition of done per D-01 — none of those OS-specific or Actions-only surfaces can be proven from this local pre-check.
- No blockers for Plan 02.

---
*Phase: 02-verify-the-green-baseline*
*Completed: 2026-07-04*

## Self-Check: PASSED

- FOUND: tests/test_preview_version_sync.py
- FOUND: .planning/phases/02-verify-the-green-baseline/02-01-SUMMARY.md
- FOUND: e97cd43 (Task 1 commit)
- FOUND: 4042930 (SUMMARY commit)
