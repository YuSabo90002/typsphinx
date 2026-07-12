---
created: 2026-07-13
title: Fix codly per-block config leaking into PDF body text (and not applied)
area: rendering
files:
  - typsphinx/translator.py (literal_block / code-block codly per-block config emit path — number-format branch AND codly-range highlight branch)
  - tests/test_pdf_render_gate.py (render-gate convention for the regression test)
---

## Problem

Per-block **codly** configuration calls are emitted in a **markup context** instead of code
mode, so Typst treats them as literal text rather than executing them. Two concrete symptoms
(same root cause) found by eyeballing the Sphinx `doc/` v9.1.0 corpus PDF (685p, clone SHA
`cc7c6f435ad37bb12264f8118c8461b230e6830c`):

1. **`codly(number-format: none)` leaks into the body** — the line-numbers-off config renders
   as visible prose instead of being applied.
2. **`codly-range(highlight: (3))` leaks into the body AND the highlight is not applied** —
   the Sphinx `:emphasize-lines:` → codly-range highlight config renders as visible prose,
   and because the call is never executed, the emphasized lines are **not** actually
   highlighted in the output.

Root-cause class: a code-mode `codly(...)` / `codly-range(...)` config call is dropped into
markup content rather than emitted as an executed code-mode statement. Same class as Phase-15
**bug #15** (`block_quote` markup/code-mode confusion) and the broader "code-mode function
call leaks as text" family the Phase-15 GATE-02 campaign fixed across many contexts.
Non-fatal — GATE-02 ("no fatal `TypstCompilationError`") is already met; this is a
rendering-quality + correctness defect.

## Solution

Locate the `literal_block` / `code-block` handling in `typsphinx/translator.py` where the
per-block codly config is emitted (the `number-format` / line-number branch AND the
`codly-range(highlight: ...)` / `:emphasize-lines:` branch). Emit **all** per-block codly
config as **executed code-mode calls** (`#codly(...)` / `#codly-range(...)`, or inside a
`#{ ... }` block), never as markup content.

Acceptance:
- The emitted `.typ` places every codly config as an executed call, not visible text.
- A fast, offline **render-gate test** (`tests/test_pdf_render_gate.py` convention:
  `[sys.executable, "-m", "sphinx", "-b", "typstpdf", ...]` → `typst.compile()` → `pypdf`
  text extraction) asserts a code block with `:emphasize-lines:` (and one without `:linenos:`)
  compiles to `%PDF` and the extracted body text contains **no** `codly(` / `codly-range(` /
  `number-format` / `highlight:` literals. Ideally also assert the emphasized lines are
  actually styled (or at minimum that the `codly-range` call is emitted in code mode).
  Confirm the test FAILS pre-fix, PASSES post-fix.
- No regression to the codly line-number offset behavior from Phase-15 bug #14
  (`codly(offset: N)`).

Env note (NixOS sandbox): run tests with the 4 known-bad integration files excluded
(`--ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`); new
subprocess calls use `[sys.executable, "-m", "sphinx", ...]`, never `uv run sphinx-build`.
