---
phase: 18-fidelity-fixes-regression-gate-close
plan: 02
subsystem: testing
tags: [sphinx, typst, pdf, corpus-gate, regression, milestone-close]

# Dependency graph
requires:
  - phase: 18-fidelity-fixes-regression-gate-close (plan 01)
    provides: "FID-01a fr-column + in-table ZWSP fix in translator.py, applied uniformly to every table in the corpus (D-02)"
provides:
  - "Real full-corpus GATE-03 re-run confirming the FID-01a fix does not regress fatal-free compilation (SC#2/GATE-02 non-regression) across the ~684-page Sphinx v9.1.0 doc/ corpus"
  - "Confirmed unknown_visit catalogue is empty of todo_node/manpage post-fix (SC#3)"
  - "Confirmed SC#4 milestone invariant: zero new runtime deps, no @preview version bump, 3-way version-sync surface untouched"
  - "Visual confirmation (extdev/deprecated grid table, pp.239-245 of the fresh build) that the wide-table collision/clip is gone with no new collision introduced"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified: []

key-decisions:
  - "No source changes made or needed -- this plan is purely verification/gate re-run per D-04 (GATE-03 is mechanical, not a design decision). No per-task commits exist because files_modified is empty by design."

requirements-completed: [GATE-03]

coverage:
  - id: D1
    description: "SC#4 milestone invariant guard: zero new runtime deps, no @preview version bump, writer.py/template_engine.py/templates/base.typ version-sync surface unchanged since phase start"
    requirement: "GATE-03"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py -q"
        status: pass
      - kind: other
        ref: "git diff --stat 3963a25..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ pyproject.toml (empty diff)"
        status: pass
    human_judgment: false
  - id: D2
    description: "GATE-03 full-corpus real-render regression gate: sphinx-build -b typstpdf over the cached Sphinx v9.1.0 doc/ corpus (689 pages), index.pdf produced with valid %PDF magic, 0 fatal errors, unknown_visit catalogue empty of todo_node/manpage"
    requirement: "GATE-03"
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -q"
        status: pass
    human_judgment: false
  - id: D3
    description: "Confirmatory visual check: extdev/deprecated 'Deprecated APIs' grid table (pp.239, 241, 245 of the fresh corpus build) renders with cell text wrapping within its column, no inter-column glyph collision, no right-margin clip"
    requirement: "GATE-03"
    verification:
      - kind: manual_procedural
        ref: "Rendered PDF pages 239/241/245 via pdftoppm and visually inspected (Read tool image view)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-19
status: complete
---

# Phase 18 Plan 02: GATE-03 Corpus Regression Close Summary

**Re-ran the real ~684-page Sphinx v9.1.0 corpus through `-b typstpdf` post-FID-01a: fatal-free (689-page `index.pdf`, valid `%PDF` magic), `unknown_visit` catalogue empty, and the SC#4 no-new-deps/no-`@preview`-bump invariant confirmed untouched — milestone v0.6.1's regression gate is closed.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-19T22:50:00Z (approx.)
- **Completed:** 2026-07-19T23:10:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 0 (verification-only plan; `files_modified: []` per plan frontmatter)

## Accomplishments

- **Task 1 (SC#4 invariant guard):** Confirmed `pytest tests/test_preview_version_sync.py -q` passes (2/2, 3-way `@preview` version agreement intact). Confirmed `git diff --stat` against the phase-start baseline commit (`3963a25`, pre-18-01) shows zero changes to `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, or `pyproject.toml` — the FID-01a fix (18-01) touched only `translator.py` and test files. Confirmed `pypdf>=6.14,<7` remains in `[project.optional-dependencies].dev` only, never promoted to `[project].dependencies` (still 3 runtime deps: sphinx, docutils, typst).
- **Task 2 (GATE-03 corpus re-run):** Ran `tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` for real in the full local environment (the NixOS sandbox restriction was already lifted per prior session memory; `import typst` succeeds, typst 0.15.0 present). The test cloned/reused the cached Sphinx v9.1.0 `doc/` corpus (tag `v9.1.0`, commit `cc7c6f435ad37bb12264f8118c8461b230e6830c`), ran a real `sphinx-build -b typstpdf` over all corpus docnames, and asserted:
  - `index.pdf` exists, non-empty, valid `%PDF` magic — **verified independently**: 15,179,893 bytes, **689 pages** (via `pypdf.PdfReader`), confirming this was a genuine full-corpus build, not a stub or partial run (13.4s wall time — Typst's Rust compiler is simply fast for this corpus size; corroborated by comparing byte size to Phase 17's cached corpus PDF of 15,153,646 B, same order of magnitude).
  - `unknown_visit` catalogue (printed to stdout): `[]` — empty, confirming `todo_node`/`manpage` (Phase 16 fixes) have not regressed and no new silently-dropped node type was introduced by the FID-01a fr-column change.
  - Test result: **1 passed in 13.41s**.
  - **Confirmatory human-check:** Located the `extdev/deprecated` "Deprecated APIs" grid table in the fresh build's `index.pdf` (pages 239, 241, 245 — same docname/table the Phase 17 audit flagged as the FID-01a repro anchor, originally pp.239–249). Rendered these pages to PNG via `pdftoppm` (through `nix-shell -p poppler-utils`, since poppler isn't on the base PATH) and visually inspected them with the Read tool's image view. Confirmed: every cell (including long dotted API paths like `sphinx.registry.SphinxComponentRegistry.html_themes` and `sphinx.ext.napoleon.docstring.GoogleDocstring._qualify_name()`) wraps its text within its own column — no cross-column glyph collision, no right-margin clipping. This visually confirms the fix at the exact repro anchor, matching the automated collision-absence proof from 18-01's `test_wide_table_render_gate.py`.

## Task Commits

No per-task commits — this plan is a verification/gate-close plan with `files_modified: []` by design (D-04: GATE-03 re-runs existing test machinery, no source changes). Both tasks ran real test/verification commands only; `git status --short` confirmed zero working-tree changes after both tasks completed.

**Plan metadata:** see commit list in completion message (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified

None. This plan re-runs existing test machinery (`tests/test_corpus_gate.py`, `tests/test_preview_version_sync.py`) unchanged and records the outcome.

## Decisions Made

None - followed plan as specified. D-04 (GATE-03 is mechanical, not a design decision) was implemented exactly as locked: the existing `test_corpus_compiles_with_no_fatal_error` gate was reused as-is, not modified or weakened.

## Deviations from Plan

None - plan executed exactly as written. Both tasks were pure verification with no code changes required; no bugs, missing functionality, or blockers were encountered.

## Issues Encountered

None. `poppler-utils` was not on the base PATH for the confirmatory visual check (a NixOS quirk, not a plan-scoped issue) — resolved via `nix-shell -p poppler-utils --run pdftoppm`, a read-only tooling workaround with no code or dependency impact (does not touch `pyproject.toml`).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Milestone v0.6.1 (rendering fidelity) is now complete.** All three phases done: Phase 16 (todo_node/manpage handlers + LEN-01 converter), Phase 17 (rendering-fidelity audit, F1-F15 catalogued), Phase 18 (FID-01a fix + GATE-03 close).
- GATE-03 is green in the full local environment (not an environmental deferral): fatal-free 689-page corpus compile, empty `unknown_visit` catalogue, SC#4 invariants intact.
- Known residual risk carried forward from 18-01 (documented in 18-RESEARCH.md Assumption A2, explicitly out of Phase 18's locked scope): GATE-03's fatal-only corpus re-run does not machine-detect a NEW *silent* (non-fatal) column collision on a corpus table other than the `extdev/deprecated` repro. The confirmatory human visual check covered the repro anchor only, not all 689 pages. Any such finding on a different table would be a future-audit candidate (F1-F15 style), not a Phase 18 regression.
- No blockers for closing the milestone.

## Self-Check: PASSED

- `tests/test_preview_version_sync.py -q` output confirmed: `2 passed in 0.01s`.
- `tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` output confirmed: `1 passed in 13.41s`, printed `Unknown Visit Catalogue: []`.
- `index.pdf` at the test's tmp_path (`/tmp/pytest-of-yuta/pytest-51/test_corpus_compiles_with_no_f0/_build/index.pdf`) confirmed present, 15,179,893 bytes, 689 pages via independent `pypdf.PdfReader` inspection.
- `git status --short` confirmed empty (no untracked/modified files) after both tasks.
- `git diff --stat 3963a25..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ pyproject.toml` confirmed empty.

---
*Phase: 18-fidelity-fixes-regression-gate-close*
*Completed: 2026-07-19*
