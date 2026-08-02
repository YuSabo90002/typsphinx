---
phase: 39-admonition-taxonomy-rubric-nesting
reviewed: 2026-08-02T00:00:00Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - scripts/render_admonition_greyscale.py
  - tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
  - tests/fixtures/admonition_greyscale_probe/conf.py
  - tests/fixtures/admonition_greyscale_probe/index.rst
  - tests/fixtures/admonition_render_gate/index.rst
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/rubric_indent_invariance_gate/conf.py
  - tests/fixtures/rubric_indent_invariance_gate/index.rst
  - tests/fixtures/rubric_strong_nesting_render_gate/conf.py
  - tests/fixtures/rubric_strong_nesting_render_gate/index.rst
  - tests/test_admonition_bucket_render_gate.py
  - tests/test_admonition_greyscale_pipeline.py
  - tests/test_admonitions.py
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_pdf_render_gate.py
  - tests/test_rubric_indent_invariance.py
  - tests/test_rubric_strong_nesting_render_gate.py
  - tests/test_topics.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 39: Code Review Report

**Reviewed:** 2026-08-02T00:00:00Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Reviewed the phase's actual diff surface in `typsphinx/translator.py` (the five
re-routed admonition call sites — `seealso`→`tip`, `danger`/`attention`→`error`,
`admonition`→`notify`, `topic`→`abstract` — the new `sphinx.locale.admonitionlabels`
title lookup in `_visit_admonition`, and the rubric save-slot/separator fix in
`visit_rubric`/`depart_rubric`), plus every listed fixture and test module, and the
dev-only greyscale render script.

Verified directly rather than assumed:
- `node.__class__.__name__` for all ten catalog-keyed docutils admonition node types
  (`note`, `warning`, `tip`, `important`, `caution`, `hint`, `error`, `danger`,
  `attention`) and `addnodes.seealso` matches its `sphinx.locale.admonitionlabels` key
  byte-for-byte (checked interactively against the installed Sphinx); `todo_node`,
  `admonition`, and `topic` are confirmed absent from the catalog, so their existing
  dynamic/caller-supplied title paths are untouched.
- The one site that emits a static title (`_depart_admonition`) now routes it through
  `escape_typst_string` before interpolation; no other code path builds a
  `title:` argument from a static string without escaping. Confirmed the escaper
  correctly handles embedded quotes, backslashes, and non-ASCII text.
- The `visit_rubric`/`depart_rubric` save slots were renamed from the shared
  `_strong_was_*` names to dedicated `_rubric_was_*` names, which is exactly what
  stops a nested inline `strong` child from clobbering the rubric's own saved state
  (confirmed no other handler in the file writes to `_rubric_was_*`, so it cannot be
  clobbered by anything else either). The double-blank-line fix (`anchors_were_emitted`
  guard) was checked against the regenerated `golden.typ`: the diff is confined to
  exactly the propagated-target-in-list-item region the fix commit claims, and the two
  byte-shape CONTROLS (the unanchored "Options" rubric and the unanchored trailing
  rubric) are untouched.
- Ran the full set of listed test modules (`53 passed`) plus `ruff check` and `mypy`
  over the changed files — all clean.

No BLOCKER-level defects found. One WARNING (a test-coverage gap that could hide a
future regression in already-shipped-but-untested behavior) and two INFO items.

## Warnings

### WR-01: Seven admonition unit tests were not updated to assert the new title behavior they now exercise

**File:** `tests/test_admonitions.py:31-70, 113-130, 325-365`
**Issue:** `test_note_converts_to_info`, `test_warning_converts_to_warning`,
`test_tip_converts_to_tip`, `test_caution_converts_to_warning`,
`test_hint_converts_to_tip`, `test_error_converts_to_error` (and their danger/attention
siblings, which at least got title-relevant docstring updates) only assert the
gentle-clues function name and the body wrapper; none of them assert the presence (or
absence) of the new `, title: "..."` argument that `_visit_admonition`'s
`sphinx.locale.admonitionlabels` lookup now attaches to every one of these seven types.
Several docstrings ("Test that nodes.warning converts to `warning[]`") are now
factually stale — real output is `warning({...}, title: "Warning")`, not a bare
`warning[]`/`warning({...})`. The `_CATALOG_TITLE_SENTINELS` table in
`tests/test_admonition_bucket_render_gate.py` does cover this precisely, so there is no
production defect today, but this file's own tests would not fail if a future edit
regressed one of these seven types' title argument (e.g. accidentally reverting to no
title, or reintroducing the old un-escaped interpolation) as long as the gentle-clues
function name stayed the same.
**Fix:** Add a `, title: "..."` assertion (using the real English catalog string, e.g.
`"Note"`, `"Warning"`, `"Tip"`, `"Caution"`, `"Hint"`, `"Error"`) to each of these six
unit tests, mirroring what `test_admonition_titles_match_locale_catalog` already checks
end-to-end, so a regression here fails close to the unit under test and not only in the
render-gate module.

## Info

### IN-01: `render_admonition_greyscale.py`'s `import tempfile` is deferred to the `__main__` block

**File:** `scripts/render_admonition_greyscale.py:176`
**Issue:** `import tempfile` is placed inside the `if __name__ == "__main__":` guard
rather than with the other stdlib imports at the top of the file (`io`, `subprocess`,
`sys`, `pathlib.Path`). Purely a style inconsistency in this dev/CI-only tooling script
— no functional impact.
**Fix:** Move `import tempfile` up to the top-level import block for consistency with
the rest of the module.

### IN-02: `custom_title: str = None` predates this phase but is now exercised by a real i18n-sourced value

**File:** `typsphinx/translator.py:4344`
**Issue:** `_visit_admonition`'s signature (`custom_title: str = None`) is not new to
this phase (pre-existing before 8a37226) and `mypy`/`ruff` both pass clean on it, so
this is not a regression this phase introduced. Flagging only because the phase newly
routes a real (potentially locale-dependent) catalog string through this same
parameter/attribute, making the implicit-`Optional` annotation slightly more
load-bearing than before.
**Fix:** Out of scope for this phase; consider `custom_title: str | None = None` in a
future typing-cleanup pass (not the deferred `Dict`/`List` modernization todo — a
distinct, smaller fix).

---

_Reviewed: 2026-08-02T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
