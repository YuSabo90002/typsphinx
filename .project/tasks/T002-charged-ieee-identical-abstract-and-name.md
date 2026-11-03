---
id: T002
title: Make charged-ieee approach1 render the same abstract as approach2 and replace the stale sphinx-typst name in its README
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - examples/charged-ieee/approach1/conf.py
  - examples/charged-ieee/README.md
  - tests/test_examples_charged_ieee_gate.py
---

# T002 — Make charged-ieee approach1 render the same abstract as approach2 and replace the stale sphinx-typst name in its README

## Context

DOCS-AUDIT at 81af8d6b: examples/charged-ieee/README.md claims both approaches produce identical output, but the shipped PDFs differ in the abstract's line breaks. approach1 passes `ieee_abstract` as a triple-quoted multi-line Python string (`examples/charged-ieee/approach1/conf.py:26-28`) through `typst_template_function["params"]["abstract"]`; approach2 hardcodes the abstract as a Typst content block `let ieee_abstract = [...]` in `examples/charged-ieee/approach2/source/_typst/_template.typ:37`. The owner ruled fix-code (Q2 a): make the outputs identical and keep the README claim. The README also says "sphinx-typst" at lines 3, 7 and 150 (fix-doc, Q3 a). M004 already fixed approach1's title (`"title": project`); `tests/test_examples_charged_ieee_gate.py` builds both approaches.

## Approach

- Change approach1's `ieee_abstract` so the rendered abstract matches approach2's text and line breaks (e.g. one logical paragraph with no embedded newlines, or whatever form approach2 effectively renders); inspect both built PDFs to confirm. Do not edit approach2 or anything under `typsphinx/`.
- Replace the three "sphinx-typst" occurrences in the README with "typsphinx"; keep the identical-output claim.
- Extend `tests/test_examples_charged_ieee_gate.py` with a check that builds both approaches with `typstpdf` (reuse the file's existing build helpers/fixtures) and asserts the extracted abstract text, including line breaks, is identical between the two PDFs, and that the README contains no "sphinx-typst". Keep it OS-neutral (compare text, normalise `\r\n`).
- Never write a literal triple-backtick in Verify; no index-reading checks.

## Interface contract

- None

## Intent coverage

- SC4
- SC5

## Acceptance criteria

1. SC4: building approach1 and approach2 with `typstpdf` produces PDFs whose extracted abstract text, including line breaks, is identical; a test in `tests/test_examples_charged_ieee_gate.py` asserts this and fails on the pre-fix approach1 `conf.py`; the README's identical-output claim is kept.
2. SC5: examples/charged-ieee/README.md contains no "sphinx-typst"; the three occurrences read "typsphinx".

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && ! grep -n 'sphinx-typst' examples/charged-ieee/README.md && grep -q 'identical' examples/charged-ieee/README.md && LC_ALL=C uv run pytest tests/test_examples_charged_ieee_gate.py tests/test_examples_typstpdf_gate.py -o addopts="" -q
```

Heavy: no

## Log

- 2026-11-03 — created by plan (quick mode)
