---
phase: 56-per-document-template-documentation
verified: 2026-08-16T12:32:09Z
status: human_needed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open the built `docs/_build/html/user_guide/configuration.html` and the `docs-pdf` output (`docs/_build/pdf/typsphinx.pdf`); confirm the registry error table, the key-naming table, and the removed-values table each render with every row visible and no text overflowing the page margin in the PDF."
    expected: "All three list-tables display fully readable in both HTML and PDF, no row clipped, no horizontal overflow in the PDF."
    why_human: "Layout/legibility is not expressible as an assertion — this project has no PDF text-overflow inspection tooling available (`pdfinfo` not installed in this environment) and rendered-table legibility is inherently a visual judgment. This item was explicitly deferred to end-of-phase by 56-05-PLAN.md's own `<human-check>` block; the build-green half is independently confirmed automated below (both `tox -e docs-html` and `tox -e docs-pdf` succeeded, and all three table headings were confirmed present in the rendered HTML)."
---

# Phase 56: Per-Document Template Documentation Verification Report

**Phase Goal:** The published documentation describes the registry that actually shipped. `configuration.rst:80`'s "accepted and ignored" definition of element [4] and `advanced.rst:129-138`'s outdir-root-relative `refs.bib` guidance are both retired documentation debt this phase must retire.
**Verified:** 2026-08-16T12:32:09Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Independent Verification Method

This report is built entirely from commands I ran myself against the codebase at HEAD
(`c96f1573`), not from SUMMARY.md narration. Every claim below was re-derived: full test suite run
once, both doc builds run from a clean `docs/_build`, repo-wide greps re-run with my own search
terms (not copied from the corrected prose), and — per the adversarial-verification instruction
that a green gate is not proof a gate is load-bearing — I performed **three live falsification
tests**: reintroducing the retracted "accepted and ignored" phrase, reintroducing a stale
`_template.typ` claim, and adding an undocumented `raise ExtensionError` shape to
`typsphinx/template_registry.py`. All three correctly turned their respective gate RED; the
working tree was restored to clean (`git status --short` empty) after each.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1: Element [4] is documented as the registry key; the retracted "accepted and ignored" definition survives on no published surface | ✓ VERIFIED | `configuration.rst:80` now reads "5. **Document registry key**"; my own repo-wide `grep -rn "accepted and ignored" --exclude-dir=.git .` found zero hits outside `.planning/` (historical planning records) and `tests/` (regression assertions / the gate's own detector string). Falsified live: reintroducing the phrase into `configuration.rst` makes `tests/test_registry_documentation_gate.py::TestRetractedElementFourDefinitionIsGone::test_retracted_phrase_absent_from_every_policed_file` fail with the exact offending file named. |
| 2 | SC#1: `typst_document_templates` is documented — each key, the template-xor-package rule, the reserved `"typst"` key, and every fail-loud error | ✓ VERIFIED | `configuration.rst` "Per-Document Templates" (:155), "Registry Key Naming Rules" (:231), and the "When the Build Stops" error table (nine shapes, seven config-caused + two I/O-caused in a separate note) all present and read. Two-way AST-based gate (`TestErrorCatalogueAgreesWithCode`, 5 tests) binds every published fragment to a real `raise ExtensionError` site and vice versa. Falsified live: injecting a new undocumented `raise ExtensionError(...)` into `template_registry.py` makes `test_code_to_docs_every_non_excluded_shape_is_published` fail, naming the new site. Reverted; `git diff --stat -- typsphinx/` confirmed empty afterward. |
| 3 | SC#2: `templates.rst`'s asset example and `advanced.rst`'s `refs.bib` guidance describe the bundle layout (asset beside its template, copied with it) | ✓ VERIFIED | `templates.rst:79-118` states "no exceptions" bundle copying including the built-in `"typst"` key; `advanced.rst:122-131` states the bare `"refs.bib"` reference, matching the bundle layout. Both bound to a real `sphinx-build -b typstpdf` + `typst.compile()` fixture (`tests/test_user_template_relative_asset_gate.py`, 12/12 passed, including 2 teeth tests for the subpath-form and restriction-phrase false claims). |
| 4 | SC#2: each published asset example is exercised by a real build, not reviewed by eye | ✓ VERIFIED | `test_asset_reached_the_bundle_destination` proves the fixture's `refs.bib` lands beside `logo.png`/`branded.typ` at the measured `_template/<key>/` destination via a real Sphinx+Typst build (ran it myself; passed). |
| 5 | SC#3: Migration guidance for `typst_template_assets`, `typst_authors`, `typst_toctree_defaults` is published, naming replacement and consequence, matching CONF-19's warning | ✓ VERIFIED | `configuration.rst:604-644` "Removed Configuration Values" list-table; text read directly matches `typsphinx/removed_config.py:36-57`'s `REMOVED_CONFIG_VALUES` strings verbatim in substance (same-v0.9.0/v0.7.1/v0.6.3, same replacement-or-absence, same consequence). `tests/test_registry_documentation_gate.py::TestRemovedValuesGuidanceMatchesTheWarnings` (4 tests) and `tests/test_removed_config_deprecation_gate.py` (10 tests, including a real `sphinx-build` proving three separate warnings fire in declaration order) both pass. |
| 6 | SC#4: No stale claim survives the sweep across the full repo-wide policed set, discovered at run time | ✓ VERIFIED | My own re-run of five independent grep patterns (not derived from the corrected prose: the retracted phrase, the old root-basename, the deleted method name, the outdir-relative `_templates/refs.bib` form, the deleted `copy_template_assets` method) found zero surviving hits in `docs/source/`, `README.md`, `examples/` outside intentional, already-corrected content and excluded historical changelogs. `tests/test_bundle_layout_sweep_gate.py` (9 tests) is a machine-enforced, `rglob`-discovered, non-skipping gate; falsified live by appending a stale `_template.typ`-at-output-root claim to `templates.rst`, which made `test_no_reserved_template_basename_claim_survives` fail. Reverted; `git status --short` clean afterward. |
| 7 | SC#4: `tox -e docs-html` and `tox -e docs-pdf` stay green | ✓ VERIFIED | Ran both myself from a clean `docs/_build` (removed first, per the environment note about incremental under-reporting): `docs-html` → "build succeeded, 3 warnings"; `docs-pdf` → "build succeeded, 5 warnings" — both match the documented pre-existing baseline exactly, none referencing any page this phase touched. |
| 8 | The `--root` hand-compile conditional (D-03 amendment) is published correctly and both branches are pinned by a real compile | ✓ VERIFIED | `output_layout.rst:71-84`'s "Which File to Compile" section states the conditional correctly (bare target: no root needed; nested target: `--root <outdir>` needed) and gives the reason (Typst's default root = compiled file's own directory). `tests/test_hand_compile_root_gate.py` (10 tests, ran myself, all passed) pins both branches via real `typst.compile()` calls. |

**Score:** 8/8 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/source/user_guide/configuration.rst` | Registry subsection, key-naming rules, error catalogue, removed-values section, element [4] rewrite | ✓ VERIFIED | All sections present, read directly, content matches code sources |
| `docs/source/user_guide/output_layout.rst` | `_template/<key>/` layout, corrected nine-file count, conditional `--root` note | ✓ VERIFIED | Read directly; matches |
| `docs/source/user_guide/templates.rst` | No-exceptions bundle copying rule | ✓ VERIFIED | Read directly; matches |
| `docs/source/user_guide/builders.rst` | Corrected file-count paragraph | ✓ VERIFIED | Now states "four root-level `.typ` files" for the two-entry example, no root-level shared template claim |
| `docs/source/examples/advanced.rst` | Bare-filename `refs.bib` guidance | ✓ VERIFIED | Read directly; matches |
| `examples/basic/README.md`, `examples/advanced/README.md` | Bundle-directory output description | ✓ VERIFIED | Both rebuilt independently by me against a real `-b typst` run of each example project; output tree matches the README's claims exactly |
| `examples/charged-ieee/approach1/conf.py`, `approach2/conf.py` | Corrected comments, `typst_template` value unchanged | ✓ VERIFIED | `copy_template_assets` and stale `_template.typ`-artifact claims gone; `typst_template = "_typst/_template.typ"` value in approach2 confirmed byte-unchanged (legitimate input path) |
| `CLAUDE.md:49` | Corrected architecture bullet | ✓ VERIFIED | Now names `_copy_used_template_bundles()`, which exists at `typsphinx/builder.py:2009`; `_write_template_file` (deleted symbol) no longer mentioned anywhere in the repo |
| `tests/test_registry_documentation_gate.py` | Two-way catalogue gate, key-naming gate, removed-values gate, retraction sweep, all with teeth tests | ✓ VERIFIED | 23 tests, all passed; genuinely fails on falsification (tested live) |
| `tests/test_bundle_layout_sweep_gate.py` | Repo-wide anchored presence gate, teeth tests | ✓ VERIFIED | 9 tests, all passed; genuinely fails on falsification (tested live) |
| `tests/test_hand_compile_root_gate.py` | Both `--root` branches pinned by real compile | ✓ VERIFIED | 10 tests, all passed |
| `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` | New fixture asset | ✓ VERIFIED | Exists, content read, referenced by `branded.typ`'s `bibliography("refs.bib")` call |

### Data-Flow Trace (Level 4)

Not applicable in the conventional sense (this is a docs-only phase, no UI/API data flow), but the
equivalent "is the published claim backed by a real measurement" check was performed for every
truth above via real `sphinx-build`/`typst.compile()` executions I ran myself, not by trusting an
existing green test's prior run.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Basic example builds and matches its README's claimed output tree | `sphinx-build -b typst examples/basic <scratch>` | `basic-example.typ`, `index.typ` at root + `_template/typst/base.typ` one dir down | ✓ PASS |
| Advanced example builds and matches its README's claimed output tree | `sphinx-build -b typst examples/advanced <scratch>` | 4 root-level `.typ` files + `_template/typst/custom.typ` one dir down | ✓ PASS |
| Charged-IEEE approach1/approach2 examples still build after comment corrections | `pytest tests/test_examples_charged_ieee_gate.py` | 2 passed | ✓ PASS |
| Retracted phrase gate fires when reintroduced | live edit + `pytest tests/test_registry_documentation_gate.py::TestRetractedElementFourDefinitionIsGone` | FAILED (as required) | ✓ PASS (gate has teeth) |
| Stale `_template.typ` claim gate fires when reintroduced | live edit + `pytest tests/test_bundle_layout_sweep_gate.py` | FAILED (as required) | ✓ PASS (gate has teeth) |
| Undocumented error shape gate fires when introduced | live edit to `typsphinx/template_registry.py` + `pytest tests/test_registry_documentation_gate.py::TestErrorCatalogueAgreesWithCode` | FAILED (as required) | ✓ PASS (gate has teeth) |

### Probe Execution

Not applicable — this phase has no `scripts/*/tests/probe-*.sh` probes; verification used the
project's own pytest/tox gates instead.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|--------------|----------------|--------------|--------|----------|
| DOC-15 | 56-01, 56-02, 56-03, 56-05 | `configuration.rst` describes element [4] as registry key, retracting "accepted and ignored" | ✓ SATISFIED | Truths 1, 2, 8 above; two-way gate, falsified live and confirmed red-on-drift |
| DOC-16 | 56-04, 56-05 | `templates.rst`/`advanced.rst` asset guidance describes what actually works under the bundle layout | ✓ SATISFIED | Truths 3, 4 above; fixture-bound real build |
| DOC-17 | 56-02, 56-05 | Migration guidance for removed config values published | ✓ SATISFIED | Truth 5 above; matches `REMOVED_CONFIG_VALUES` verbatim, real-build ordering proof |

No orphaned requirements — REQUIREMENTS.md maps exactly DOC-15/DOC-16/DOC-17 to Phase 56, and all
three appear in at least one plan's `requirements:` frontmatter.

**Note on REQUIREMENTS.md's current `[ ] Pending` state:** per the task brief, this is deliberate —
the orchestrator reverted an early premature flip and instructed every plan to leave the checkboxes
Pending so a downstream step confirms delivery independently. My verdict from the evidence above:
**all three are ACTUALLY delivered.** DOC-15, DOC-16, and DOC-17 should be flipped to complete by
the phase-completion step; I have not edited REQUIREMENTS.md myself, per instruction.

### Anti-Patterns Found

None. Scanned every file this phase modified (`docs/source/user_guide/*.rst`,
`docs/source/examples/advanced.rst`, `examples/*/README.md`, `examples/charged-ieee/*/conf.py`,
`CLAUDE.md`, all three new/extended test modules) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/
"coming soon"/"not yet implemented" — zero hits.

### Production-Code Boundary

Confirmed independently: `git diff --stat f07e8cb8..HEAD -- typsphinx/` is empty. Zero lines of
`typsphinx/*.py` changed across all five plans, matching the phase's docs-only scope and every
plan's own prohibition.

### Full-Suite and Lint/Type Gates (measured by me, not copied from SUMMARY.md)

- `uv run pytest -q` → **1417 passed, 5 skipped, 0 failed** (matches the orchestrator's independently-measured count exactly)
- `uv run black --check .` → clean, 339 files unchanged
- `uv run ruff check .` → all checks passed
- `uv run mypy typsphinx/` → Success: no issues found in 8 source files
- `uv run tox -e docs-html` (clean `docs/_build`) → build succeeded, 3 warnings (baseline)
- `uv run tox -e docs-pdf` (clean `docs/_build`) → build succeeded, 5 warnings (baseline)

### Human Verification Required

### 1. Rendered readability of the error-catalogue, key-naming, and removed-values tables

**Test:** Open `docs/_build/html/user_guide/configuration.html` and the compiled
`docs/_build/pdf/typsphinx.pdf`. Confirm the "When the Build Stops" error table, the "Registry Key
Naming Rules" table, and the "Removed Configuration Values" table each render with every row fully
visible and no text overflowing the PDF page margin.

**Expected:** All three tables are legible in both HTML and PDF, no row clipped, no horizontal
overflow.

**Why human:** Visual layout/legibility is not expressible as an automated assertion. This
environment has no PDF text-overflow inspection tool (`pdfinfo` unavailable). This is the single
item `56-05-PLAN.md`'s own `<human-check>` block explicitly deferred to end-of-phase, and
`56-VALIDATION.md`'s "Manual-Only Verifications" table names it as the phase's one non-automatable
behavior. The automated half is independently confirmed above: both doc builds succeed at their
baseline warning count, and all three table headings were confirmed present in the rendered HTML
output.

### Gaps Summary

No gaps found. Every observable truth backed by the ROADMAP's four success criteria was
independently re-derived from the codebase (not from SUMMARY.md claims), and the phase's own two
new machine-enforced gates were live-falsified to confirm they are load-bearing rather than
vacuously green. The only open item is the one behavior this phase's own validation strategy
correctly flagged as requiring human eyes — table rendering legibility in HTML and PDF output.

---

_Verified: 2026-08-16T12:32:09Z_
_Verifier: Claude (gsd-verifier)_
