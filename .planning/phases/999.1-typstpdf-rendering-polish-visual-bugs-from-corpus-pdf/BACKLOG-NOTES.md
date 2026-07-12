# Phase 999.1 (BACKLOG): typstpdf rendering polish — visual bugs from corpus PDF

**Status:** backlog parking lot (unsequenced). Non-fatal visual/rendering defects found by
eyeballing the generated PDF *after* GATE-02 was met. GATE-02 = "no fatal
`TypstCompilationError`" is already green (Phase 15); these are quality issues for a future
rendering-polish milestone (e.g. v0.7.0).

**How to use this file:** append each newly-found visual bug from the corpus PDF here as its
own `## Bug:` block. When ready to work them, `/gsd-review-backlog` promotes 999.1 to the
active milestone, then `/gsd-discuss-phase 999.1` / `/gsd-plan-phase 999.1`.

**Repro corpus:** Sphinx `doc/` v9.1.0 (clone SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`),
built via `TYPSPHINX_CORPUS_REPORT=1 pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s`
→ `index.pdf` (685 pages, ~15 MB).

---

## Bug: `codly(...)` config leaks into PDF body text

**Found:** 2026-07-13 (eyeballing the corpus PDF)

**Symptom:** `codly(number-format: none)` appears as **literal prose in the rendered body**
instead of being applied as a codly (code-block package) configuration. The reader sees the
raw Typst function call text where a code block should just render without line numbers.

**Root-cause class:** a code-mode `codly(...)` call is emitted in a **markup context**, so
Typst treats it as literal text rather than executing it. This is the SAME class as Phase-15
**bug #15** (`block_quote` markup/code-mode confusion — a code-mode call rendered as prose),
and the broader "code-mode function call leaks as text" family the Phase-15 campaign fixed
across many contexts.

**Likely fix site:** `typsphinx/translator.py` — the `literal_block` / `code-block` handling
where the codly per-block config is emitted (the branch that disables line numbers, i.e.
emits `number-format: none` for a `:linenos:`-off block). The config call needs to be in
code mode (`#codly(...)` / inside `#{ ... }`), not dropped into markup content.

**Fix acceptance (when promoted):**
- The emitted `.typ` places the codly config as an executed call, not visible text.
- A fast, offline **render-gate test** (`tests/test_pdf_render_gate.py` convention:
  `[sys.executable, "-m", "sphinx", "-b", "typstpdf", ...]` → `typst.compile()` → `pypdf`
  text extraction) asserts that a code block **without** `:linenos:` compiles to `%PDF` and
  that the extracted body text contains **no** `codly(` / `number-format` literal.
- No regression to the codly line-number offset behavior fixed in Phase-15 bug #14
  (`codly(offset: N)`).

**Environment note (NixOS sandbox):** run tests with the 4 known-bad integration files
excluded (`--ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`);
new subprocess calls use `[sys.executable, "-m", "sphinx", ...]`, never `uv run sphinx-build`.

---

<!-- Append further visual bugs below as `## Bug: <short title>` blocks. -->
