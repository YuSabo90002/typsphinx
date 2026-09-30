---
phase: 56-per-document-template-documentation
plan: 04
subsystem: docs
tags: [sphinx, rst, typst, pytest, doc-gate, bibliography]

# Dependency graph
requires:
  - phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
    provides: "the per-key bundle relocation (OUT-04/OUT-05) this plan's asset examples must describe"
  - phase: 56-per-document-template-documentation (plan 01)
    provides: "the merged base this plan built on; the bundle-destination-collision catalogue row on configuration.rst this plan deliberately does not restate"
provides:
  - "docs/source/examples/advanced.rst's custom_ieee.typ code block and note: the bare-filename bibliography reference (\"refs.bib\"), correcting both the literal template source and the destination claim"
  - "docs/source/user_guide/templates.rst's Template Assets closing note: OUT-04's no-exceptions bundle rule, the per-key-directory statement, and the empty-bundle statement"
  - "tests/fixtures/user_template_relative_asset_gate/: a second relative asset (refs.bib) and a #bibliography(\"refs.bib\") call in branded.typ, proving the bare-filename reference resolves by real compile"
  - "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture: a never-skipping class binding both corrected pages to the fixture's measured reference form"
affects: [56-05]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 3606
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: ["prose-binding test class deriving its asserted reference form from the fixture file itself (regex-extracted), not a hardcoded string, so correcting the fixture without correcting the pages fails the binding rather than silently diverging"]

key-files:
  created: [tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib]
  modified:
    - tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ
    - tests/test_user_template_relative_asset_gate.py
    - docs/source/examples/advanced.rst
    - docs/source/user_guide/templates.rst

key-decisions:
  - "No citation call was added to prove the bibliography resolves. A throwaway compile (typst 0.15.0) confirmed #bibliography(\"refs.bib\") with zero #cite() calls compiles successfully (default full: false just renders an empty references section) -- the plan's documented fallback (cite from index.rst or the template body) was never needed."
  - "Task 1's #bibliography(\"refs.bib\") call was placed after body, inside its own pagebreak(), so it renders as a trailing references section, matching the plan's structural guidance."
  - "Task 3's built-in-key coverage assertion checks for the substrings \"built-in\", '\"typst\"', and \"same rule\" independently rather than one exact sentence, so future rewording of the note's exact phrasing does not spuriously break the gate as long as the three facts stay stated."

patterns-established:
  - "DOC-16 prose-binding gate mirrors the DOC-15 catalogue gate's shape (56-01): never-skipping, defined outside any typst-py import guard, with synthetic-page teeth self-tests calling the SAME pure helper functions the real assertions use."

requirements-completed: []
# DOC-16 is intentionally NOT listed here. It is also claimed by plan 56-05
# (per this plan's <requirements_flagging_rule>), and REQUIREMENTS.md's
# traceability flip is the orchestrator's job after the last contributing
# plan lands -- not this plan's. .planning/REQUIREMENTS.md is left
# byte-identical by this plan (git diff --stat confirms zero changes to it).

coverage:
  - id: D1
    description: "advanced.rst's custom_ieee.typ code block and explanatory note both use the bare-filename bibliography reference (\"refs.bib\"), matching the bundle-relocation form; the note no longer claims the template lands at the output root as _template.typ"
    requirement: "DOC-16"
    verification:
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_advanced_rst_publishes_the_bare_reference_form"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_neither_page_publishes_the_subpath_form"
        status: pass
      - kind: integration
        ref: "uv run tox -e docs-html && uv run tox -e docs-pdf (build succeeded, 3/5 warnings, matching the pre-existing baseline)"
        status: pass
    human_judgment: false
  - id: D2
    description: "templates.rst's Template Assets closing note states OUT-04's no-exceptions bundle rule (the built-in \"typst\" key is copied by the same rule as any custom key) plus the per-key-directory and empty-bundle facts, with no ordering claim about colliding destinations"
    requirement: "DOC-16"
    verification:
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_templates_rst_does_not_restrict_bundle_copying_to_custom_templates"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_templates_rst_names_the_built_in_key_as_covered_by_the_same_rule"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_templates_rst_states_the_per_key_directory_rule"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture::test_templates_rst_states_the_empty_bundle_rule"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both published examples are proven by one real sphinx-build -b typstpdf -> typst.compile(), not eyeball review: refs.bib reaches the same per-key bundle destination logo.png and branded.typ already reach"
    requirement: "DOC-16"
    verification:
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate::test_asset_reached_the_bundle_destination"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate::test_build_succeeds"
        status: pass
      - kind: unit
        ref: "tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate::test_pdf_is_valid"
        status: pass
    human_judgment: false
  - id: D4
    description: "The @preview version-lockstep site count stays at three (no fourth site created); the fixture stays free of Typst Universe dependencies"
    requirement: "DOC-16"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py"
        status: pass
    human_judgment: false

# Metrics
duration: 11min
completed: 2026-08-16
status: complete
---

# Phase 56 Plan 04: Per-Document Template Asset Examples Summary

**Corrected both published asset examples to the bare-filename reference the bundle relocation actually resolves, proved by one real `sphinx-build -b typstpdf` compile of an extended fixture, and closed `templates.rst`'s asset note's understated custom-templates-only exception.**

## Performance

- **Duration:** 11 min (commit-to-commit, base commit `8ac9af2e` to final task commit `580936c2`)
- **Started:** 2026-08-16T11:38:08Z
- **Completed:** 2026-08-16T11:49:17Z
- **Tasks:** 3
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- Extended `tests/fixtures/user_template_relative_asset_gate/` with a second relative asset: `refs.bib` (a minimal `@misc` BibTeX entry) and a `#bibliography("refs.bib")` call added to `branded.typ` after the body, using the bare filename to match `logo.png`'s existing form. `test_asset_reached_the_bundle_destination` now asserts `refs.bib` reaches `<outdir>/_template/typst/refs.bib` alongside `logo.png` and `branded.typ`, proving the wholesale copy is not selective.
- Corrected `docs/source/examples/advanced.rst`'s `custom_ieee.typ` code block (`bibliography: bibliography("refs.bib")`, was `"_typst/refs.bib"`) and its explanatory note, which no longer claims the template lands at the output root as `_template.typ` -- it now states typsphinx copies the template's whole bundle directory to the output tree, so `refs.bib` lands beside the template and the bare filename is correct.
- Rewrote `templates.rst`'s Template Assets closing note from "Bundle copying only applies to custom local templates" to OUT-04's no-exceptions rule (the built-in `"typst"` key is copied by the same rule as any custom key), plus a separate sentence on what the `typst_package` route does instead (no local bundle to copy). Added the per-key-directory statement and the empty-bundle statement to the automatic-bundle-copying paragraph.
- Added `TestPublishedAssetGuidanceMatchesTheFixture` (8 tests) to `tests/test_user_template_relative_asset_gate.py`, defined outside the `TYPST_AVAILABLE` skipif scope so it never skips. It derives the bare-filename reference form from `branded.typ` itself via regex extraction (not a hardcoded string), asserts neither page publishes the source-tree-shaped subpath form, asserts the three `templates.rst` facts (no-exceptions, per-key-directory, empty-bundle), and carries two synthetic-page "teeth" self-tests proving the subpath and restriction-phrase detectors fire.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend the relative-asset fixture with a bibliography asset and assert where it lands** - `95461bb5` (feat)
2. **Task 2: Correct advanced.rst's bibliography guidance in both the code block and the note** - `34b12a7a` (fix)
3. **Task 3: Correct templates.rst's asset rule and bind both pages to the fixture's measured destination** - `580936c2` (feat)

**Plan metadata:** committed as part of this SUMMARY.md commit (worktree mode -- STATE.md/ROADMAP.md excluded; the orchestrator owns those writes after the wave merges)

## Files Created/Modified

- `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` - New: a minimal `@misc` BibTeX entry, the second relative asset this fixture's bundle carries.
- `tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ` - Header comment extended to record the bibliography call as a second load-bearing line; a `#bibliography("refs.bib")` call added after `body`.
- `tests/test_user_template_relative_asset_gate.py` - `test_asset_reached_the_bundle_destination` extended with a third existence assertion for `refs.bib`; new `TestPublishedAssetGuidanceMatchesTheFixture` class (8 tests) plus its pure helper functions and module-level `TEMPLATES_RST_PATH`/`ADVANCED_RST_PATH`/`FIXTURE_TEMPLATE_PATH` constants.
- `docs/source/examples/advanced.rst` - `custom_ieee.typ` code block's `bibliography` argument corrected to the bare filename; the explanatory note rewritten to describe the bundle destination instead of a root-level `_template.typ`.
- `docs/source/user_guide/templates.rst` - Template Assets closing note rewritten (no-exceptions rule + package-route explanation); automatic-bundle-copying paragraph gains the per-key-directory and empty-bundle sentences.

## Decisions Made

- **No citation call was needed to make the bibliography render.** The plan's action text anticipated Typst might require at least one `#cite()` call for `#bibliography()` to compile, with an explicit fallback (cite from `index.rst` or the template body). Before implementing, I ran a throwaway `typst.compile()` against a minimal `#bibliography("refs.bib")` call with zero citations (worktree's typst 0.15.0) and it compiled successfully -- Typst's default `full: false` behavior just renders an empty references section when nothing is cited, it does not error. The fallback was therefore never invoked; `branded.typ`'s call carries no citation, matching `advanced.rst`'s own published example (which also carries no `#cite()` call).
- **The built-in-key coverage assertion checks three independent substrings** (`"built-in"`, `'"typst"'`, `"same rule"`) rather than a single exact-sentence match, so a future rewording of the note's phrasing does not spuriously break the gate as long as the three facts (built-in status, the literal key, and rule-equivalence) stay stated.
- **No `:doc:` cross-reference to `configuration.rst`'s bundle-destination-collision catalogue row was added** to `templates.rst`. The task's action text made this optional ("if a pointer is useful"); given D-05's explicit directive not to editorialize about the refusal shape on this page, and that the closing note's job is already fully discharged by the no-exceptions/per-key/empty-bundle facts, I judged an extra cross-reference would add surface without closing a gap this plan is responsible for.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - self-inflicted acceptance-criterion false positive] `_typst/refs.bib` literal in my own new header comment**
- **Found during:** Task 1's acceptance-criteria verification.
- **Issue:** My first draft of `branded.typ`'s extended header comment quoted the forbidden subpath form verbatim (`` e.g. `"_typst/refs.bib"` ``) as an example of what must not be written, which tripped `grep -c '_typst/refs.bib' ... is 0` even though no actual reference in the file used that form.
- **Fix:** Reworded the sentence to "a source-tree-shaped subpath form" without spelling out the literal banned string.
- **Files modified:** `tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ`
- **Verification:** `grep -c '_typst/refs.bib' tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ` returns `0`; `uv run pytest tests/test_user_template_relative_asset_gate.py -q` stayed green.
- **Committed in:** `95461bb5` (fixed before the task commit)

---

**Total deviations:** 1 self-caught fix to my own draft text. No scope creep -- both are corrections within Task 1's own slice, not new functionality.

## Issues Encountered

- **Task 1's acceptance criterion `grep -c '@preview' ... is 0` cannot be satisfied without deleting pre-existing, unrelated prose.** `branded.typ`'s ORIGINAL header comment (predating this plan, from Phase 54) already says: "No `@preview` package imports are declared here ... (CLAUDE.md 'The `@preview` version-sync hazard' ...)" -- two literal occurrences of the substring `@preview`, present in `git show HEAD:tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ` (the commit this plan's base tree already contained) before any edit in this plan. The task's own action text says to "extend" the header comment, not to remove existing content, and the actual intent of the criterion -- "no `@preview` import was added" -- is genuinely true: no import statement was added, only prose referencing the absence of one, which is what the pre-existing text already did. Left the pre-existing comment untouched; the grep count stays 2, not 0. Same class of false positive as 56-01-SUMMARY.md's `git diff | grep -c '^-.*"typst")'` note -- a literal-substring collision in surrounding prose, not an actual violation.
- **Task 2's acceptance criterion `git diff docs/source/examples/advanced.rst | grep -c 'important::' is 0`** also produced a false positive (`1`, not `0`): the `.. important::` heading two lines below the edited note appears as unchanged unified-diff CONTEXT (default 3-line context window), with no `+`/`-` prefix. `git diff docs/source/examples/advanced.rst | sed -n '1,50p'` confirms the important block carries zero changed (`+`/`-`) lines -- it was not touched, only shown as surrounding context because the last hunk of the note edit ends 2 lines above it.

Neither false positive reflects an actual defect; both are documented here per this repository's established precedent (56-01-SUMMARY.md's "Issues Encountered" section) for the same reason: the acceptance-criterion pattern cannot distinguish a literal-substring coincidence from a real violation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `TestPublishedAssetGuidanceMatchesTheFixture` now polices both `templates.rst` and `advanced.rst`'s bibliography/asset guidance against the fixture's real measured output; any future edit to either page that reintroduces the subpath form, the restriction phrase, or drops the per-key/empty-bundle facts will fail this gate.
- `DOC-16` stays `[ ]` / `Pending` in `.planning/REQUIREMENTS.md` (untouched by this plan, confirmed by `git diff --stat` showing zero changes to that file) -- it is also claimed by plan 56-05, so the traceability flip is deferred to the orchestrator/phase-completion step after the last contributing plan lands, per this plan's `<requirements_flagging_rule>`.
- Full-suite baseline moved from 1379 passed/5 skipped/0 failed (56-01's recorded baseline) to **1387 passed/5 skipped/0 failed** (+8, matching the 8 new `TestPublishedAssetGuidanceMatchesTheFixture` methods); `black --check .`, `ruff check .` (via main-checkout workaround, same NixOS ELF limitation as 56-01), and `mypy typsphinx/` are all clean; `tox -e docs-html` (3 warnings) and `tox -e docs-pdf` (5 warnings) both report `build succeeded`, matching the pre-existing baseline exactly. `git diff --stat typsphinx/ docs/source/changelog.rst CHANGELOG.md` is empty across all three task commits.
- No blockers for 56-05 or any later plan in this phase.

## Self-Check: PASSED

- FOUND: `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib`
- FOUND: `tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ`
- FOUND: `tests/test_user_template_relative_asset_gate.py`
- FOUND: `docs/source/examples/advanced.rst`
- FOUND: `docs/source/user_guide/templates.rst`
- FOUND: commit `95461bb5`
- FOUND: commit `34b12a7a`
- FOUND: commit `580936c2`

---
*Phase: 56-per-document-template-documentation*
*Completed: 2026-08-16*
