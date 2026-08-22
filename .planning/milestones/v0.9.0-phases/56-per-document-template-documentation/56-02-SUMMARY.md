---
phase: 56-per-document-template-documentation
plan: 02
subsystem: docs
tags: [sphinx, rst, ast, pytest, doc-gate, typst, template-registry]

# Dependency graph
requires:
  - phase: 56-per-document-template-documentation
    provides: "plan 56-01's Per-Document Templates subsection, its When the Build Stops error catalogue, and the two-way AST-based doc-gate shape (tests/test_registry_documentation_gate.py) this plan builds directly on top of"
provides:
  - "docs/source/user_guide/configuration.rst's completed Per-Document Templates subsection: additive statement, template-xor-package definition schema (CONF-15/CONF-16), a two-master local worked example (D-04), a short package-route schema example, the which-bundles-reach-the-output rule with an output_layout link, the empty-registry statement, and the nested Registry Key Naming Rules sub-subsection (the seven CONF-18 cases, the casefold-without-Unicode-normalization rule, the reserved-key fold refusal, the exact-equality element [4] lookup rule)"
  - "the D-08 preventive statement in Custom Template File: a template's directory must not also be named in Sphinx's templates_path"
  - "a new top-level Removed Configuration Values section covering typst_template_assets, typst_authors, and typst_toctree_defaults, each bound by import to typsphinx/removed_config.py's REMOVED_CONFIG_VALUES"
  - "tests/test_registry_documentation_gate.py: TestKeyNamingRulesMatchTheCode and TestRemovedValuesGuidanceMatchesTheWarnings, plus a generalized _region_text_by_heading() helper shared across all doc-gate classes in the module"
  - "tests/test_removed_config_deprecation_gate.py: TestMultipleRemovedValuesEachWarnSeparately, a real sphinx-build proving three separate warnings fire in REMOVED_CONFIG_VALUES declaration order when all three removed values are set together"
affects: [56-05]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 5707
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: ["Reusable heading-delimited region extractor (_region_text_by_heading()) shared by every doc-gate class in a module, generalized from the single-heading helper 56-01 introduced", "Name-to-phrase module-level dicts checked for exact set-equality against the imported code-side enumeration, so a renamed or added case/removal fails loudly rather than silently going unchecked"]

key-files:
  created: []
  modified: [docs/source/user_guide/configuration.rst, tests/test_registry_documentation_gate.py, tests/test_removed_config_deprecation_gate.py]

key-decisions:
  - "The package-route schema example uses a placeholder value (\"<typst-universe-package-spec>\") instead of a real @preview import string, to honor the plan's absolute prohibition on quoting a new @preview version even though the file already carries two PRE-EXISTING @preview mentions from 56-01's own content (see Issues Encountered) -- my change adds zero new @preview occurrences."
  - "Split what was written as one continuous editing pass into three atomic per-task commits by temporarily reverting Task 2's and Task 3's content, committing Task 1, then reapplying Task 2's content and committing, then reapplying Task 3's content and committing -- preserving the plan's task-level commit granularity and per-task verification gates despite the underlying edits having been drafted together."
  - "Generalized 56-01's single-heading _catalogue_region_text() helper into _region_text_by_heading(heading), keeping _catalogue_region_text() as a one-line wrapper -- both new gate classes (naming rules, removed values) reuse the SAME extraction logic rather than duplicating it a second and third time."

patterns-established:
  - "Pattern: a module-level name-to-phrase dict, checked for exact set-equality against the imported code-side enumeration (set(_KEY_SHAPE_REJECTION_CASES) / set(REMOVED_CONFIG_VALUES)), makes a renamed or newly-added code-side case fail the gate immediately rather than silently passing with stale coverage."

requirements-completed: []

# DOC-15 and DOC-17 are also claimed by plans 56-03/56-04/56-05 in this wave;
# per the orchestrator's explicit instruction, this plan does NOT mark them
# complete in REQUIREMENTS.md. requirements-completed is left empty and
# REQUIREMENTS.md is untouched -- the orchestrator flips both after the last
# contributing plan lands.

coverage:
  - id: D1
    description: "The Per-Document Templates subsection publishes the registry's schema (template-xor-package, CONF-15/CONF-16), a two-master local worked example with no network dependency (D-04), a short package-route schema example, the which-bundles-reach-the-output rule linked to output_layout, the empty-registry statement, and the D-08 preventive templates_path note in Custom Template File"
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_docs_template_layout_gate.py -- all tests"
        status: pass
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py -- all tests"
        status: pass
      - kind: other
        ref: "uv run tox -e docs-html && uv run tox -e docs-pdf (build succeeded, both pre-existing warning baselines only)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A Registry Key Naming Rules sub-subsection, nested before the error table, publishes the seven CONF-18 rejection cases in their fixed check order, the casefold-without-Unicode-normalization comparison rule, the reserved-key fold refusal, and the exact-equality element [4] lookup rule -- bound to typsphinx.template_registry._KEY_SHAPE_REJECTION_CASES by import"
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py::TestKeyNamingRulesMatchTheCode"
        status: pass
    human_judgment: false
  - id: D3
    description: "A top-level Removed Configuration Values section publishes migration guidance for typst_template_assets, typst_authors, and typst_toctree_defaults -- the config-inited/every-builder mechanism, the A-03 None/empty-value edge, exact-name-matching detection, the absence of a suppress_warnings route, and a per-name what-to-do-instead table -- bound to typsphinx.removed_config.REMOVED_CONFIG_VALUES by import, and the multi-value declaration-order claim proven by a real sphinx-build"
    requirement: "DOC-17"
    verification:
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py::TestRemovedValuesGuidanceMatchesTheWarnings"
        status: pass
      - kind: integration
        ref: "tests/test_removed_config_deprecation_gate.py::TestMultipleRemovedValuesEachWarnSeparately::test_all_three_set_together_warn_once_each_in_declaration_order"
        status: pass
  - id: D4
    description: "Rendered legibility of the two new list-tables (Registry Key Naming Rules, Removed Configuration Values) in both furo HTML and the typstpdf PDF"
    requirement: "DOC-15"
    verification:
      - kind: automated_ui
        ref: "uv run tox -e docs-html && uv run tox -e docs-pdf (build succeeded); HTML <table> markup and PDF text extraction (via typst-py's own compiled output) both inspected directly, see Deviations"
        status: pass
    human_judgment: true
    rationale: "Layout/legibility is not expressible as a plain assertion (56-VALIDATION.md's Manual-Only Verifications table names this exact deliverable). This SUMMARY records the executor's own programmatic verification (HTML table cell rendering of the literal backslash, PDF text extraction confirming both new section headings and table rows reached the compiled output) as the closing evidence for this checkpoint; a full visual open-the-file review is deferred to the phase's end-of-phase human_verify_mode checkpoint."

# Metrics
duration: 40min
completed: 2026-08-16
status: complete
---

# Phase 56 Plan 02: Registry Documentation Completion and Removed-Config Migration Guidance Summary

**Completed `configuration.rst`'s registry documentation with a network-free two-master worked example, a seven-case key-naming rules table bound to code by import, and a new Removed Configuration Values section for the three v0.9.0-era config removals -- all held to `typsphinx/template_registry.py` and `typsphinx/removed_config.py` by import rather than transcription.**

## Performance

- **Duration:** 40 min (commit-to-commit)
- **Started:** 2026-08-16T11:14:00Z
- **Completed:** 2026-08-16T11:54:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `docs/source/user_guide/configuration.rst`'s `Per-Document Templates` subsection now carries the full registry contract: an additive-behavior statement, the template-xor-package definition schema (CONF-15/CONF-16), a two-master local `template`-route worked example with no Typst Universe network dependency (D-04, the only place a non-default registry key appears in the published docs), a short `package`-route schema example, the which-bundles-reach-the-output rule linked to `:doc:`output_layout``, Phase 54's D-01 no-deletion note, and the empty-registry statement.
- A nested `Registry Key Naming Rules` sub-subsection, positioned before `When the Build Stops` (D-07): the seven CONF-18 rejection cases as a `list-table` in the fixed order `_validate_registry_key_shape()` checks them, the casefold-without-Unicode-normalization comparison rule, the reserved-key fold refusal, and the exact-`str`-equality element [4] lookup rule. The error table's invalid-definition row now cross-references it via `` `Registry Key Naming Rules`_ ``.
- The `Custom Template File` subsection carries the D-08 preventive statement: a template's own directory must not also be named in Sphinx's `templates_path`.
- A new top-level `Removed Configuration Values` section covers `typst_template_assets`, `typst_authors`, and `typst_toctree_defaults`: the `config-inited`/every-builder mechanism, the A-03 `None`/empty-value edge, exact-name-matching detection, the absence of a `suppress_warnings` route, and a per-name `list-table` in `REMOVED_CONFIG_VALUES` declaration order.
- `tests/test_registry_documentation_gate.py` gained `TestKeyNamingRulesMatchTheCode` (5 tests) and `TestRemovedValuesGuidanceMatchesTheWarnings` (5 tests), both binding published prose to code by import via a generalized `_region_text_by_heading()` helper, each with its own teeth test proving the coverage check actually fires.
- `tests/test_removed_config_deprecation_gate.py` gained `TestMultipleRemovedValuesEachWarnSeparately`: a real `sphinx-build` with all three removed names set together, proving three separate warnings fire (never aggregated) in `REMOVED_CONFIG_VALUES` declaration order, measured by string position rather than asserted.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end -- the registry schema, worked example, package route, and bundle rules** - `e6d1f626` (feat)
2. **Task 2: The registry key naming rules, bound to code by import** - `539801bc` (feat)
3. **Task 3: Migration guidance for the three removed config values** - `55568ceb` (feat)

**Plan metadata:** will be committed as part of this SUMMARY.md commit (worktree mode -- STATE.md/ROADMAP.md excluded; the orchestrator owns those writes after the wave merges)

## Files Created/Modified

- `docs/source/user_guide/configuration.rst` - Grew from 486 to 649 lines: the completed `Per-Document Templates` subsection, the new `Registry Key Naming Rules` sub-subsection, the D-08 note in `Custom Template File`, and the new `Removed Configuration Values` top-level section.
- `tests/test_registry_documentation_gate.py` - New `TestKeyNamingRulesMatchTheCode` and `TestRemovedValuesGuidanceMatchesTheWarnings` classes (10 tests total), a generalized `_region_text_by_heading()` helper, and the `CASE_NAME_TO_PHRASE` / `REMOVED_NAME_TO_PHRASE` module-level phrase maps.
- `tests/test_removed_config_deprecation_gate.py` - New `TestMultipleRemovedValuesEachWarnSeparately` class proving the declaration-order guarantee against a real build.

## Decisions Made

- **Package-route example uses a placeholder, not a real `@preview` string.** The plan's must-have prohibitions state "No `@preview` package version is quoted into any documentation page." The file already carries two pre-existing `@preview` mentions from 56-01's own predecessor content (the `Typst Package` subsection and the `Complete Example` block, both untouched by this plan). Rather than add a third occurrence, the package-route schema example uses `"<typst-universe-package-spec>"` as a placeholder value, satisfying the letter and intent of the prohibition -- my changes introduce zero new `@preview` occurrences (verified: `grep -c '@preview' configuration.rst` stayed at 2, unchanged, across all three commits).
- **Task commits split via a temporary revert-then-reapply sequence.** All three tasks' content was drafted together in one working pass (the tasks are textually adjacent/interleaved within the same file), then Task 2's and Task 3's additions were temporarily reverted via `Edit`, Task 1 was verified and committed alone, Task 2's content was reapplied and committed, then Task 3's. This preserves the plan's required per-task atomic commit granularity and per-task verification gates without losing any of the drafted content.
- **Reused and generalized 56-01's region-extraction helper** (`_catalogue_region_text()` → `_region_text_by_heading(heading)`) rather than writing two more copies of the same heading-delimited slicing logic, per the plan's own instruction ("extracted at run time by the SAME heading-title-delimited helper the catalogue uses").

## Deviations from Plan

### Auto-fixed Issues

None -- plan executed exactly as written, task order and scope followed precisely.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** None.

## Issues Encountered

- **Two of the plan's acceptance-criteria greps are unsatisfiable at baseline, for reasons unrelated to this plan's own changes.**
  - Task 1's acceptance criterion `grep -c '@preview' docs/source/user_guide/configuration.rst is 0` cannot pass: `configuration.rst` already carries two `@preview` mentions (lines 137 and 455 pre-this-plan) from content the page already had before this plan started (the `Typst Package` subsection's own worked example and the `Complete Example` block, both written before 56-01/56-02 and untouched by either). Confirmed via `git diff docs/source/user_guide/configuration.rst | grep -c '@preview'` across each of this plan's three commits: `0` in every diff -- my changes add no new occurrence. The literal grep-on-the-whole-file criterion was already broken before this plan touched anything.
  - Task 3's acceptance criterion `grep -c 'suppress_warnings' docs/source/user_guide/configuration.rst is 0` similarly cannot pass: the phrase already appears once, in 56-01's `.. note::` at the end of the `When the Build Stops` error catalogue ("Neither names a `` ``suppress_warnings`` `` route..."), written by the prior plan and untouched by this one. `git diff` across all three of this plan's commits shows zero new occurrences of the string.
  - Both are documented here rather than "fixed," since fixing them would require editing 56-01's already-committed, already-merged prose, which is out of this plan's `files_modified` scope and not something this plan's tasks call for.
- **`tox -e docs-pdf`'s warning count is 5, not the research baseline of 2.** Verified with `-v` and a clean rebuild that only two genuine `sphinx.util.logging` `WARNING:` lines fire (`unknown node type: <doctest_block ...>` for two autodoc-rendered doctest examples in `writer.py`'s docstrings), plus one additional pre-existing `WARNING: Block quote ends without a blank line` from a docstring in `typsphinx/translator.py`'s `visit_toctree` -- none reference `configuration.rst` or any file this plan touches. This is baseline drift between `56-RESEARCH.md`'s measurement (at commit `f07e8cb8`) and the current worktree base (`8ac9af2e`, after 56-01 merged), not a regression this plan introduced. Both `tox -e docs-html` and `tox -e docs-pdf` still report `build succeeded`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `56-05` (the sweep audit, Wave 3) can now assume `configuration.rst`'s registry documentation, key-naming rules, and removed-values guidance are all complete and gate-bound -- its repo-wide discovery grep will find these sections already correct rather than needing to flag them.
- `DOC-15` and `DOC-17` are left `Pending` in `.planning/REQUIREMENTS.md`, per the orchestrator's explicit instruction: both are also claimed by sibling plans in this wave (56-03, 56-04) and by 56-05, so the flip to complete is deferred to whichever step owns closing out the last contributing plan.
- No blockers. `git diff --stat typsphinx/` is empty across all three commits -- no production code touched, matching this docs-only plan's scope. Full suite (`uv run pytest -q`) ran green in the background during this plan's own verification pass (1390 passed / 5 skipped / 0 failed, matching the post-56-01 baseline plus this plan's 15 new tests); `black --check .`, `ruff check .` (from the main checkout, per the NixOS ELF workaround), and `mypy typsphinx/` are all clean.

## Self-Check: PASSED

- FOUND: `docs/source/user_guide/configuration.rst`
- FOUND: `tests/test_registry_documentation_gate.py`
- FOUND: `tests/test_removed_config_deprecation_gate.py`
- FOUND: commit `e6d1f626`
- FOUND: commit `539801bc`
- FOUND: commit `55568ceb`

---
*Phase: 56-per-document-template-documentation*
*Completed: 2026-08-16*
