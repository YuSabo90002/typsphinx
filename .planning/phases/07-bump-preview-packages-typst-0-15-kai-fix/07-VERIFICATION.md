---
phase: 07-bump-preview-packages-typst-0-15-kai-fix
verified: 2026-07-11T00:25:13Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 7: Bump @preview Packages + typst 0.15 (kai fix) Verification Report

**Phase Goal:** `typst` is raised to 0.15 and the four bundled `@preview` packages are bumped in lockstep so the `typstpdf` builder compiles the project docs to PDF with zero `kai`-class errors — the empirical root-cause fix and the highest-risk gate of the milestone.
**Verified:** 2026-07-11T00:25:13Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `tox -e docs-pdf` compiles the project docs to PDF with zero `TypstError` (no `unknown variable: kai`) — FWD-02, PKG-01, PKG-02 | ✓ VERIFIED | Independently re-ran `.venv/bin/tox -e docs-pdf` after deleting `docs/_build/pdf/index.pdf`. Fresh run: `build succeeded, 2 warnings`, `docs-pdf: OK`, `Generated PDF: .../docs/_build/pdf/index.pdf`. Grepped both the freshly-regenerated PDF bytes and the saved `/tmp/07-docs-pdf.log` (dated 2026-07-11 09:12, matching the SUMMARY's execution window) — zero occurrences of `kai`, zero `TypstError`. |
| 2 | `pytest tests/test_preview_version_sync.py` passes — the three sync sites agree in lockstep — PKG-03 | ✓ VERIFIED | `.venv/bin/python -m pytest tests/test_preview_version_sync.py -x -v` → `2 passed in 0.01s` (both `test_preview_versions_identical_across_declaration_sites` and `test_all_four_packages_declared`). |
| 3 | `uv sync --locked` resolves cleanly with typst 0.15.x installed from the regenerated lockfile — FWD-02 | ✓ VERIFIED | `.venv/bin/uv sync --locked` exits 0, no changes needed (lockfile already current). `uv.lock`'s `[[package]] name = "typst"` block shows `version = "0.15.0"`. `pyproject.toml:30` reads `"typst>=0.15.0,<0.16",`; diff of commit `2ed64aa` confirms this is the *only* line changed in the `dependencies` array (sphinx/docutils lines untouched). |
| 4 | The generated PDF opens with no missing-glyph tofu, no broken/blank boxes, no error glyphs (coarse visual glance per D-01/D-04) — FWD-02 | ✓ VERIFIED | PDF regenerated in this session (2,063,964 bytes, `/Count 101` confirms 101 pages, matching SUMMARY's claim). SUMMARY records the executor's own coarse glance across ~12 sampled pages (cover, TOC, config examples, code blocks, math examples, API reference, changelog) finding no tofu/broken boxes/error glyphs — human-judgment item, self-attested by the executor per D-01/D-04's lightweight glance criterion (not an element-by-element audit). No compiler-level error glyphs are present (the compile itself is clean, per Truth 1). |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | pins `typst>=0.15.0,<0.16` (FWD-02) | ✓ VERIFIED | Line 30: `"typst>=0.15.0,<0.16",`. Old pin `typst>=0.14.1,<0.15` absent. Only the typst line changed. |
| `uv.lock` | regenerated with typst 0.15.x (FWD-02) | ✓ VERIFIED | `name = "typst"` / `version = "0.15.0"`. `uv sync --locked` green. |
| `typsphinx/writer.py` | carries mitex 0.2.7 / gentle-clues 1.3.1 / codly-languages 0.1.10, codly 1.3.0 unchanged — PKG-01/02/03 | ✓ VERIFIED | Lines 94-97: `codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7` (named import `: mi, mitex` preserved), `gentle-clues:1.3.1`. |
| `typsphinx/template_engine.py` | same four versions, master-doc path — PKG-01/02/03 | ✓ VERIFIED | Lines 313-316: byte-identical version strings to writer.py, named mitex import preserved. |
| `typsphinx/templates/base.typ` | same four versions, default-template path — PKG-01/02/03 | ✓ VERIFIED | Lines 8,9,14,19: same four version strings; mitex import correctly kept as glob `: *` (not converted to named form — asymmetry preserved as specified). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| Four `@preview` version strings | writer.py / template_engine.py / base.typ | Identical version substrings across all three files | ✓ WIRED | Confirmed byte-identical via direct grep of all three files; `test_preview_version_sync.py` (the automated guard) passes. |
| mitex 0.2.7 named export (`mi`, `mitex`) | writer.py / template_engine.py named import | `#import "@preview/mitex:0.2.7": mi, mitex` resolved at compile time by the docs-pdf compile of included (non-master) documents | ✓ WIRED | The `docs-pdf` compile includes multiple non-master (toctree-included) documents (`user_guide/*.typ`, `api/*.typ`, etc. all use writer.py's import path) and compiled clean with zero `TypstError` — a renamed/removed export would have surfaced as an "unknown variable" or "unresolved import" TypstError at exactly this call site. None occurred. |
| codly 1.3.0 (registry ceiling, unchanged) | typst 0.15 compiler | Compile of the docs' code-block content (`.. code-block::` directives → codly-languages/codly calls) | ✓ WIRED | The docs corpus includes multiple code blocks (installation.rst, quickstart.rst, user_guide/*, api examples); compile succeeded with zero TypstError, empirically confirming codly 1.3.0 compiles under typst 0.15 — the core empirical unknown named in the plan. |
| `uv.lock` typst 0.15.x | tox `docs-pdf` env | `tox-uv`'s `uv-venv-lock-runner` installs from the regenerated lock into the `.tox/docs-pdf` venv | ✓ WIRED | Independently re-ran `tox -e docs-pdf`; the `.tox/docs-pdf` venv installs and compiles against the newly-locked typst 0.15.0 (not the stale 0.14.9) — confirmed by the successful compile itself (a 0.14.9 install would still show `kai`). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `docs-pdf` compiles kai-free (independent re-run, not trusting SUMMARY) | `rm -f docs/_build/pdf/index.pdf && .venv/bin/tox -e docs-pdf` | `build succeeded, 2 warnings`; `docs-pdf: OK`; PDF regenerated (2,063,964 bytes, 101 pages via `/Count 101`) | ✓ PASS |
| `test_preview_version_sync.py` passes | `.venv/bin/python -m pytest tests/test_preview_version_sync.py -x -v` | `2 passed in 0.01s` | ✓ PASS |
| `uv sync --locked` is green | `.venv/bin/uv sync --locked` | exit 0, no changes | ✓ PASS |
| Full test suite has no regressions | `.venv/bin/python -m pytest -q` | `402 passed, 463 warnings in 13.17s` (matches SUMMARY's "402 passed" claim) | ✓ PASS |
| Tree is black-clean (correct pinned version, `black>=26,<27`) | `.venv/bin/python -m black --check .` | `All done! 50 files would be left unchanged.` (Note: an initial `nix-shell -p black` run used a mismatched black 25.1.0 and flagged 2 unrelated pre-existing files (`tests/test_config_*`) — re-run with the project's pinned black 26.5.1 via `.venv` confirms the tree is genuinely clean; the mismatch was a tooling artifact of this verification session, not a real issue.) | ✓ PASS |
| Tree is ruff-clean | `nix-shell -p ruff --run "ruff check ."` (ruff 0.15.14, within pinned `>=0.15,<0.16`) | `All checks passed!` | ✓ PASS |
| No debt markers in phase-modified files | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER" pyproject.toml typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` | no matches | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FWD-02 | 07-01-PLAN.md | `typst` re-pinned to `>=0.15.0,<0.16`; `typstpdf` builder compiles docs to PDF under typst 0.15 with no `kai`-class error | ✓ SATISFIED | pyproject.toml/uv.lock pin verified; independent `docs-pdf` re-run compiles clean, zero TypstError/kai. |
| PKG-01 | 07-01-PLAN.md | `mitex` bumped 0.2.4→0.2.7, empirically resolving `kai` under typst 0.15 (real compile, not changelog) | ✓ SATISFIED | mitex:0.2.7 present in all 3 sync sites; docs-pdf compile (which exercises mitex on both master and included-document paths) is clean. |
| PKG-02 | 07-01-PLAN.md | `gentle-clues` (1.2.0→1.3.1) and `codly-languages` (0.1.1→0.1.10) bumped; `codly` 1.3.0 confirmed to compile under typst 0.15 | ✓ SATISFIED | All three version strings verified in all 3 sync sites; codly 1.3.0 (unchanged, registry ceiling) confirmed compiling via the same clean docs-pdf compile. |
| PKG-03 | 07-01-PLAN.md | 3-way `@preview` version-sync updated in lockstep; `test_preview_version_sync.py` passes | ✓ SATISFIED | `2 passed` on direct re-run; byte-identical version strings confirmed via grep across writer.py/template_engine.py/base.typ. |

No orphaned requirements: REQUIREMENTS.md maps only FWD-02, PKG-01, PKG-02, PKG-03 to Phase 7, and all four appear in the plan's `requirements` frontmatter and are marked `[x]` complete in REQUIREMENTS.md.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none found in phase-modified files (`pyproject.toml`, `uv.lock`, `writer.py`, `template_engine.py`, `base.typ`) | — | No debt markers, no stub returns, no placeholder text in any file this phase touched. |

**Out-of-scope discovery (not an anti-pattern introduced by this phase):** `typsphinx/translator.py::_visit_admonition` has a pre-existing markup/code-mode bug causing admonitions to render literal Typst source. This file is **not** in `07-01-PLAN.md`'s `files_modified` list. Verified independently: `git blame` on `_visit_admonition` (typsphinx/translator.py:2253) attributes it to the initial commit `e718ef9` (2025-10-13), and none of this phase's three commits (`2ed64aa`, `ca4c1ab`, `82d573b`) touch `translator.py`. The bug reproduces independent of `@preview` package version (a markup-vs-code-mode mismatch in the translator's own admonition/paragraph interaction, not a compile error). Logged correctly to `deferred-items.md` — this is a legitimate scope deferral, not a Phase-7 gap: none of the three ROADMAP Phase 7 success criteria, nor the plan's four `must_haves.truths`, require per-element content-correctness verification of admonition rendering. D-04 explicitly restricts the visual-glance criterion to "no blank/broken boxes, no missing-glyph tofu, no error glyphs" and explicitly rejects an element-by-element checklist. Literal source text is a content-correctness defect, not a compiler error glyph or layout failure, and it predates the phase by ~9 months (first became *visible* only because `docs-pdf` never compiled successfully until this phase's kai fix landed). Recommend this be picked up as a dedicated follow-up (not currently mapped to Phase 8/9/10 in ROADMAP.md or REQUIREMENTS.md v1/v2) — flagged for maintainer awareness, but does not block this phase or the milestone's traceability.

### Human Verification Required

None. The one human-judgment item in this phase (D-04 coarse PDF visual glance) was already performed and recorded by the executor during Task 3, with specific evidence (which pages were sampled, what was checked). The verifier independently regenerated the PDF (confirming byte-for-byte reproducibility of page count and a clean, kai-free compile) and did not find grounds to distrust the executor's glance report — the compile-time evidence (zero TypstError) is the authoritative D-01 hard gate, and the visual glance is explicitly scoped as a lightweight backstop, not a re-auditable checklist. No further human action is required to close this phase.

### Gaps Summary

None. All 4 must-have truths verified, all 5 required artifacts verified (exists + substantive + wired), all 4 key links wired, all 4 requirement IDs satisfied with no orphans, tree is black/ruff/debt-marker clean, and the full 402-test suite passes with no regressions. The `docs-pdf` compile — the phase's hard, highest-risk gate — was independently re-run in this verification (not merely trusted from the SUMMARY) and reproduced a clean, `kai`-free 101-page PDF. The one out-of-scope discovery (admonition rendering bug) is correctly scoped as pre-existing and orthogonal to this phase's package-version-bump mandate, and is properly logged in `deferred-items.md` for future triage.

---

_Verified: 2026-07-11T00:25:13Z_
_Verifier: Claude (gsd-verifier)_
