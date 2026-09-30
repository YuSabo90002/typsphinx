# Phase 39, Plan 03 — GATE-01 Evidence: ADM-05 Rubric Indent Invariance Guard

**Recorded against commit:** `96fb09ee90fb719b40f8c50d9ef7d07ade4c196a` (this plan's own Task 1
commit, `feat(39-03): build two-level rubric-in-description-body fixture` — the translator is
untouched at this commit and throughout this plan; see the `git diff --stat -- typsphinx/` output
below).

## D-12: this is a guard, not a GATE-01 RED

Per `39-CONTEXT.md` D-11/D-12, and mirroring Phase 36's SC#3 precedent (`ROADMAP.md` "Roadmap
Evolution", Phase 36 edit): **ADM-05 already holds against pre-phase code.** 39-CONTEXT.md
measured, via a real `-b typstpdf` build of a `py:class::`/`py:method::` probe read back through
`pypdf`, that Phase 38's `pad(left: SHARED_INDENT_STEP, {...})` wrapper around `desc_content`
already carries the rubric structurally, and that `visit_rubric` performs no indent logic of its
own. A RED cannot be recorded against pre-phase code for a property that is already true — the
same situation Phase 36's SC#3 hit and resolved the same way. This plan's module,
`tests/test_rubric_indent_invariance.py`, is therefore an **INVARIANCE GUARD**: every assertion is
expected GREEN in both directions, against both the untouched translator (recorded here) and after
any future rubric-related change lands. It exists to catch a regression, not to prove a fix. The
phase's classic GATE-01 RED comes from plan 39-02's folded defect (D-13, the `par()` drop) instead.

## Measurement-technique correction to 39-CONTEXT.md

39-CONTEXT.md's own measured table (below) does not state which pypdf extraction technique was
used to obtain it. This plan's own construction re-confirms — as
`tests/test_desc_content_indent_render_gate.py`'s module docstring already recorded for Phase 38 —
that **pypdf's per-glyph `visitor_text` position callback returns `x=0, y=0` on this project's
compiled PDFs and is unusable** for a left-edge measurement. `extraction_mode="layout"`
(reconstructing left-edge indentation as leading whitespace on a monospace-like character grid) is
the only usable technique, and is the one this plan's module uses throughout
(`_layout_lines`/`_leading_columns`/`_find_page_and_column`, copied from
`tests/test_desc_content_indent_render_gate.py`'s precedent). This correction is recorded
explicitly per this plan's `must_haves.truths`, not left silent.

## Verbatim green pytest output

```
$ uv run pytest tests/test_rubric_indent_invariance.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a54e11bcefc40ba26/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a54e11bcefc40ba26
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 7 items

tests/test_rubric_indent_invariance.py::TestRubricIndentInvarianceStructuralGate::test_typ_top_level_control_rubric_emits_no_indent_wrapper PASSED [ 14%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_class_rubric_equals_class_body_column PASSED [ 28%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_method_rubric_equals_method_body_column PASSED [ 42%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_class_body_deeper_than_top_level_reference PASSED [ 57%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_method_body_deeper_than_class_body PASSED [ 71%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_top_level_control_rubric_equals_preceding_paragraph_column PASSED [ 85%]
tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate::test_adm05_neither_rubric_over_indents_its_container PASSED [100%]

============================== 7 passed in 0.79s ===============================
```

## Measured columns — raw observations, NOT expectations

These are the actual leading-whitespace columns `_find_page_and_column` measured against this
plan's fixture (`tests/fixtures/rubric_indent_invariance_gate/index.rst`) at the commit named
above, using `extraction_mode="layout"` text extraction over the real compiled PDF. **They are
observations recorded for evidentiary purposes only — no assertion in
`tests/test_rubric_indent_invariance.py` compares against any of these numbers.** Every assertion
in the module is a RELATIVE comparison between two measured columns (per this plan's
`must_haves.prohibitions`, which forbids pinning a point value or character-column literal as an
expected constant).

| Marker | Page | Column | What it identifies |
|---|---|---|---|
| `RIITOPREF` | 2 | 0 | top-level reference paragraph (page margin) |
| `RIICLASSBODY` | 2 | 7 | class `desc_content` body's first paragraph |
| `RIICLASSRUBRIC` | 2 | 7 | rubric inside the class body |
| `RIIMETHODBODY` | 2 | 14 | nested method `desc_content` body's first paragraph |
| `RIIMETHODRUBRIC` | 2 | 14 | rubric inside the nested method body |
| `RIITOPSECOND` | 2 | 0 | second top-level paragraph, preceding the control rubric |
| `RIICTRLRUBRIC` | 2 | 0 | top-level control rubric (no containing description body) |

Observed pattern: each rubric's column equals its containing body's own column exactly, at both
nesting levels, and the top-level control rubric sits flush with ordinary top-level text at column
0 — consistent with 39-CONTEXT.md's own measured pypdf-point-based table (page margin 70.87pt,
class body / class rubric 98.37pt, method body / method rubric 125.87pt, top-level rubric 70.87pt),
though the two tables use different units (this plan's layout-mode leading-whitespace column count
vs. 39-CONTEXT.md's pypdf point coordinates) and are not directly comparable numerically — only the
*pattern* (equal columns at each level, top-level flush with the margin) is common to both.

## `git diff --stat -- typsphinx/`

```
$ git diff --stat -- typsphinx/
(empty — no output)
```

Confirms this plan modifies no file under `typsphinx/`, consistent with the plan's own
`must_haves.truths` ("This plan modifies no file under typsphinx/") and its threat-model
disposition for T-39-09 (guard-not-RED framing must not be manufactured by touching the
translator).

## Full-suite non-regression

`uv run pytest -m "not slow" -q` at this commit: **713 passed, 29 deselected**, no new failures
introduced by this plan's two new files. `uv run black --check .`, `uv run ruff check .` and
`uv run mypy typsphinx/` all pass repo-wide.
