---
created: 2026-07-13
title: Fix codly() config leaking into PDF body text
area: rendering
files:
  - typsphinx/translator.py (literal_block / code-block codly-config emit path — the line-number-off / number-format: none branch)
  - tests/test_pdf_render_gate.py (render-gate convention for the regression test)
---

## Problem

`codly(number-format: none)` renders as **literal prose in the PDF body** instead of being
applied as a codly (code-block package) configuration. The reader sees the raw Typst function
call text where a code block should simply render without line numbers.

Root-cause class: a code-mode `codly(...)` config call is emitted in a **markup context**, so
Typst treats it as literal text rather than executing it. Same class as Phase-15 **bug #15**
(`block_quote` markup/code-mode confusion) and the broader "code-mode function call leaks as
text" family the Phase-15 GATE-02 campaign fixed across many contexts.

Found by eyeballing the Sphinx `doc/` v9.1.0 corpus PDF (685 pages, clone SHA
`cc7c6f435ad37bb12264f8118c8461b230e6830c`). Non-fatal — GATE-02 ("no fatal
`TypstCompilationError`") is already met; this is a rendering-quality defect.

## Solution

Locate the `literal_block` / `code-block` handling in `typsphinx/translator.py` where the
per-block codly config is emitted (the branch that disables line numbers, i.e. emits
`number-format: none` for a `:linenos:`-off block). Emit the codly config as an **executed
code-mode call** (`#codly(...)` / inside a `#{ ... }` block), not as markup content.

Acceptance:
- The emitted `.typ` places the codly config as an executed call, not visible text.
- A fast, offline **render-gate test** (`tests/test_pdf_render_gate.py` convention:
  `[sys.executable, "-m", "sphinx", "-b", "typstpdf", ...]` → `typst.compile()` → `pypdf`
  text extraction) asserts a code block **without** `:linenos:` compiles to `%PDF` and the
  extracted body text contains **no** `codly(` / `number-format` literal. Confirm it FAILS
  pre-fix, PASSES post-fix.
- No regression to the codly line-number offset behavior from Phase-15 bug #14
  (`codly(offset: N)`).

Env note (NixOS sandbox): run tests with the 4 known-bad integration files excluded
(`--ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`); new
subprocess calls use `[sys.executable, "-m", "sphinx", ...]`, never `uv run sphinx-build`.
