---
id: T002
title: Make charged-ieee approach1 render the same abstract as approach2 and replace the stale sphinx-typst name in its README
wave: 1
deps: []
status: done
agent: build_T002
base: d3e33bccfb008560106232d050e7324140df9e13
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
- 2026-11-03 — build_T002: ready. Pre-fix measurement: approach1 PDF abstract extracted as 'Abstract—This paper presents novel approaches to machine \nlearning\napplications in computer vision. We demonstrate state-of-the-art \nresults on\nbenchmark datasets ...' (hard breaks from the Typst string's embedded newlines) vs approach2 '... machine \nlearning applications in computer vision. We demonstrate state-\nof-the-art results ... compre -\nhensive analysis of our methodology.\n'. Added to tests/test_examples_charged_ieee_gate.py: `_abstract_text()` (page-1 text from "Abstract" to "Index Terms", line breaks kept, CR LF/CR folded to LF), `TestChargedIeeeExamplesGate::test_both_approaches_render_identical_abstract` (builds both with typstpdf, asserts equal), and module-level `test_readme_names_typsphinx_not_sphinx_typst` (no "sphinx-typst", "identical output" kept). Both new tests FAILED on unmodified conf.py/README (2 failed, 2 passed). Fix: approach1/conf.py `ieee_abstract` is now one logical line via implicit string concatenation (same words); README's 3 "sphinx-typst" -> "typsphinx" (lines 3, 7, 150); identical-output claim kept. Task Verify run as written: uv sync ok, grep checks ok, `8 passed in 4.02s`. black --check and ruff clean on changed files. Note (not changed, outside files): docs/source/examples/advanced.rst:25 shows the same triple-quoted `ieee_abstract` pattern.
- 2026-11-03 — orchestrator Verify (isolate gsd-path-task/T002): pass, exit 0; output tail:
  ```
  ........                                                                 [100%]
  8 passed in 3.93s
  Resolved 95 packages in 0.57ms
  Checked 94 packages in 0.34ms
  ```
