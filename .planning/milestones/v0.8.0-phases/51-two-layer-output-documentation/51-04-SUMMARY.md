---
phase: 51-two-layer-output-documentation
plan: 04
subsystem: docs
tags: [sphinx, rst, documentation, wrapper-content-split]

# Dependency graph
requires:
  - phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
    provides: "The wrapper/content split, target-as-path resolution (_resolve_target_stem, _escapes_outdir), and the collision guard this plan's corrections must match"
  - phase: 51-two-layer-output-documentation (plan 01)
    provides: "docs/source/user_guide/output_layout.rst, the page this plan links to instead of duplicating its contract"
provides:
  - "docs/source/user_guide/builders.rst with the falsified one-file-per-entry Output claim, both `typst compile` walkthroughs, the Development `open` line, and the Document Definitions paragraph all corrected and cross-linked to output_layout"
  - "docs/source/user_guide/configuration.rst with the OUT-01 reversal applied to the typst_documents element-2 contract (path honoured, three shapes refused) and cross-linked to output_layout"
  - "docs/source/user_guide/templates.rst with the template-debugging walkthrough reading the wrapper instead of the content file, cross-linked to output_layout"
affects: [51-06]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 1807
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Concrete-filename CLI walkthroughs (D-06): every typst compile / cat / open example names the actual wrapper filename its own conf.py produces, with a one-line comment stating the derivation, instead of a generic docname-based placeholder"

key-files:
  created: []
  modified:
    - docs/source/user_guide/builders.rst
    - docs/source/user_guide/configuration.rst
    - docs/source/user_guide/templates.rst

key-decisions:
  - "Row 4 (builders.rst:156, the Development walkthrough's `open build/pdf/index.pdf` line) disposition: FIX, per the plan's explicit instruction — D-04 scopes the sweep to every falsified claim found repo-wide, not only split-caused ones, and this claim is measurably false (pre-existing CONF-08-era staleness) with a one-line fix."

patterns-established: []

requirements-completed: [DOC-14]

coverage:
  - id: D1
    description: "builders.rst's Output section states the two-file-per-entry wrapper+content shape instead of the falsified one-file-per-entry count, and all three CLI walkthroughs (Manual Compilation, Development, Production Option 2) name the concrete wrapper filename (myproject.typ / myproject.pdf) their own implicit configuration produces"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'One file per document' docs/source/user_guide/builders.rst -> 0; grep -c 'build/typst/index.typ' -> 0; grep -c 'build/pdf/index.pdf' -> 0; grep -c 'build/typst/myproject.typ' -> 2; grep -c 'build/pdf/myproject.pdf' -> 1"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py, tests/test_docs_contract_claims_gate.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "builders.rst's Document Definitions paragraph states element 2 names the wrapper only, and enumerates all four .typ files (main.typ, api-ref.typ wrappers; index.typ, api.typ content files) the shown config emits, with only the wrappers becoming PDFs"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'and it governs both' docs/source/user_guide/builders.rst -> 0; awk '/^Document Definitions/,/^Builder-Specific Options/' docs/source/user_guide/builders.rst | grep -c 'index.typ|api.typ|main.typ|api-ref.typ' each -> 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "configuration.rst's typst_documents element-2 description matches _escapes_outdir(): a path is honoured relative to the output directory, and only a `..` segment, an absolute target, or a drive-qualified target is refused with a warning and a basename fallback"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'component is not supported' docs/source/user_guide/configuration.rst -> 0; grep -c 'manuals/guide.typ' -> 1; sed -n '28,35p' docs/source/user_guide/configuration.rst | grep -c 'make_filename_from_project' -> 1 (byte-unchanged)"
        status: pass
      - kind: unit
        ref: "tests/test_docs_contract_claims_gate.py, tests/test_builder_output_stem.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "templates.rst's template-inspection walkthrough reads the wrapper (myproject.typ), because content files carry no template application at all, and states why the content file cannot show a template problem"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'cat build/typst/index.typ' docs/source/user_guide/templates.rst -> 0; grep -c 'cat build/typst/myproject.typ' -> 1; grep -c 'Generate .typ files for inspection' -> 1 (preserved)"
        status: pass
      - kind: unit
        ref: "tests/test_docs_contract_claims_gate.py"
        status: pass
    human_judgment: false
  - id: D5
    description: "builders.rst, configuration.rst, and templates.rst each carry at least one :doc:`output_layout` cross-reference (in-body plus a See Also entry) instead of a duplicated copy of the page's contract, and zero lines under typsphinx/ changed"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'output_layout' builders.rst -> 4, configuration.rst -> 2, templates.rst -> 2; git diff --name-only HEAD -- typsphinx/ -> empty"
        status: pass
    human_judgment: false

# Metrics
duration: ~25min
completed: 2026-08-15
status: complete
---

# Phase 51 Plan 04: Two-Layer Output Documentation — builders/configuration/templates Corrections Summary

**Corrected the falsified output-shape, path-contract, and template-debugging claims in `builders.rst`, `configuration.rst`, and `templates.rst`, replacing each with the measured wrapper/content behaviour and a cross-reference to the new `output_layout` page.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-15 (approx.)
- **Completed:** 2026-08-15
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `builders.rst`'s Output section no longer claims one file per `typst_documents` entry; it now states the wrapper+content split and links to `output_layout` for the full contract
- All three `typst compile` / `open` CLI walkthroughs in `builders.rst` name the concrete wrapper filename their own implicit configuration produces (`myproject.typ` / `myproject.pdf`, per `project = "My Project"`), instead of a docname-derived name that is now the content file
- `builders.rst`'s Document Definitions paragraph correctly scopes element 2 to the wrapper only, and enumerates all four `.typ` files (two wrappers, two content files) the shown configuration actually emits
- `configuration.rst`'s `typst_documents` element-2 contract reverses the OUT-01-falsified "path component is not supported" claim to match `_escapes_outdir()` exactly: a path is honoured relative to the output directory, and only a `..` segment, an absolute target, or a drive-qualified target is refused with a warning and a basename fallback
- `templates.rst`'s template-debugging walkthrough now inspects the wrapper instead of the content file, since content files carry no template application at all since Phase 47
- Each of the three pages gained a `:doc:`output_layout`` cross-reference in its corrected prose plus a `See Also` entry, placed first

## Task Commits

Each task was committed atomically:

1. **Task 1: builders.rst — the Output section, both compile walkthroughs, and Document Definitions** - `21be0c7e` (docs)
2. **Task 2: configuration.rst — the typst_documents element-2 contract (the OUT-01 reversal)** - `4f170f69` (docs)
3. **Task 3: templates.rst — inspect the wrapper, because content files carry no template** - `4955efba` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified

- `docs/source/user_guide/builders.rst` - Corrected Output bullets, Manual Compilation, Document Definitions, Common Workflow (Development + Production Option 2), and See Also
- `docs/source/user_guide/configuration.rst` - Corrected `typst_documents` element-2 contract (OUT-01 reversal) and See Also
- `docs/source/user_guide/templates.rst` - Corrected template-inspection walkthrough and See Also

## Decisions Made

- Row 4 (`builders.rst:156`, the Development walkthrough's `open build/pdf/index.pdf` line) was flagged by the researcher as a possible out-of-scope call — a pre-existing CONF-08-era staleness, not caused by the two-layer split. Per the plan's `<sweep_rows_owned_by_this_plan>` explicit disposition, **fixed** rather than deferred: D-04 scopes the sweep to every falsified claim found repo-wide, the claim is measurably false as published (the PDF is named from `project`, never `index`, since v0.7.1), and the fix is one line.
- Kept every edit strictly within the three declared `files_modified` — no changes to `output_layout.rst` (owned by 51-01/51-03/51-06) or `index.rst` (owned by 51-01), per the parallel-execution scope fence.

## Deviations from Plan

None - plan executed exactly as written. All acceptance criteria (negative greps returning 0, positive greps returning the exact counts specified) were verified before each task's commit, and both automated `<verify>` commands passed.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 13 falsified-claim sweep rows this plan owns (`51-RESEARCH.md` Part A rows 1-7) are fixed; none deferred.
- Zero lines changed under `typsphinx/` (`git diff --name-only HEAD -- typsphinx/` is empty).
- `tests/test_docs_contract_claims_gate.py`, `tests/test_builder_output_stem.py`, and `tests/test_output_layout_docs_gate.py` all pass (37/37) against the corrected pages.
- Plan 51-06's full docs HTML build (proving every `:doc:` reference resolves, including the new `output_layout` cross-references added by this plan and 51-02/51-03/51-05 in the same wave) has not yet run — that verification belongs to 51-06, after every wave-2 plan has merged.

## Self-Check: PASSED

All three modified files confirmed present on disk with expected content
(`builders.rst`, `configuration.rst`, `templates.rst`). All three task
commits (`21be0c7e`, `4f170f69`, `4955efba`) confirmed present in `git log`.

---
*Phase: 51-two-layer-output-documentation*
*Completed: 2026-08-15*
