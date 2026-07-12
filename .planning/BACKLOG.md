# Backlog

Tracked items surfaced during planning/execution that are out of the current phase's scope.

---

## BUG: `attribution` content leaks into rendered PDF (block_quote / `.. epigraph::`) — PARTIALLY OPEN

**Surfaced:** 2026-07-12 (Phase 13 research, `gsd-phase-researcher`, Pitfall 4)
**Re-verified:** 2026-07-13 (empirical `-b typstpdf` + `typst.compile()` + `pypdf` on current HEAD)
**Severity:** Medium–High — silent corruption of attribution/author text (no fatal). Worse than a loud fatal because the leak is user-visible in the PDF yet the existing render-gate test does NOT catch it (see blind spot below).

### Original bug (two symptoms), and current status

`.. epigraph::` produces a docutils `block_quote` (epigraph class) optionally containing an
`attribution` child. `typsphinx/translator.py` `visit_block_quote`/`visit_attribution` mis-emitted:

1. **With attribution → `unclosed delimiter` compile fatal.** ✅ **RESOLVED** by the Phase-15
   GATE-02 campaign — commit `c506578` rewrote `visit_block_quote` to a code-mode
   `quote(block: true, { <body> })` body. Verified 2026-07-13: an epigraph with an attribution
   line (stressed with `` ``_t`` `` + `*emphasis*`) compiles with no `TypstCompilationError`.
2. **Source leaks into rendered PDF text.** ⚠️ **STILL OPEN for the attribution content.** The
   block_quote *body* no longer leaks (code-mode now). But `visit_attribution` opens Typst
   **markup mode** (`}, attribution: [`) while the attribution's inline children are still
   emitted through the **code-mode** path (`text("...")`, `emph({...})`) with **no `#` prefix**.
   Inside a markup `[...]` block an un-prefixed `text("...")` is literal prose → the PDF shows
   `text(“Some Author”)` instead of the author name. Affects **all** block_quote/epigraph with
   an attribution, not just epigraph.

**Verified emitted `.typ` (offending line):**
```
}, attribution: [text("EPIGRAPHATTRAUTHORSENTINEL Some Author")])
```
**Verified extracted PDF text:** `— text(“…Some Author”)` (curly quotes) instead of `— …Some Author`.

### ⚠ Test blind spot (must be fixed alongside)

`tests/test_pdf_render_gate.py::TestBlockQuoteMarkupModeRenderGate` currently **passes on an
attribution case yet does not catch this leak**:
- Its `LEAK_SIGNATURES` looks for `text("` (straight ASCII `"`), but Typst markup typesets the
  leaked call with **curly** quotes (`text(“…”)`), so the signature never matches.
- Its presence assertion is a substring check (`"William Shakespeare" in full_text`), which is
  trivially true even inside the leaked `text(“William Shakespeare”)`.
A real fix must harden these checks (exact-phrase assertion + curly-quote `text(“` signature).

### Fix recommendation

In `typsphinx/translator.py`, make `visit_attribution`/`depart_attribution` either:
- (a) toggle `self._in_markup_mode = True` for the duration of the attribution's children
  (mirroring the target/reference markup-mode pattern near ~line 2478) so `visit_Text` emits the
  `#`-prefixed markup form; OR
- (b) switch the attribution argument to a code-mode content value (e.g.
  `attribution: { <code-mode children> }`) instead of a markup `[...]` bracket.
Add a dedicated epigraph render-gate (both with/without attribution) asserting `%PDF`, no fatal,
and no `text(“`/`text("` leak in extracted text — and fix the `TestBlockQuoteMarkupModeRenderGate`
signature/sentinel blind spot.

**Env note (NixOS sandbox):** run tests with `--ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`; use `[sys.executable, "-m", "sphinx", ...]`, never `uv run sphinx-build`.
