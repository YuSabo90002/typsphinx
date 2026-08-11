# Sphinx configuration for the inline-math-after-text render-gate fixture
# (Phase 34, GATE-01, MATH-01).
#
# Minimal self-contained project used by
# tests/test_inline_math_after_text_render_gate.py to prove that inline math
# immediately following text -- inside a bullet list item, a collapsed
# confval field body, and a definition-list term -- compiles through
# typst.compile() on both the mitex and native math paths, per backlog 999.1
# / MATH-01. `visit_math` currently only calls `_add_paragraph_separator()`,
# which is a no-op in all three of these contexts (`self.in_paragraph` is
# deliberately False there), so an adjacent inline expression and the
# `mi(...)` / `$...$` call land with zero characters between them --
# rejected by Typst's parser with "expected comma" or "expected semicolon
# or line break".
#
# `index` MUST be a master document so the writer emits the full template
# and TypstPDFBuilder.finish() actually compiles it to PDF -- the ONLY
# build path where the missing-separator fatal is observable (a `-b typst`
# build would emit the invalid `.typ` but never compile it).
#
# `typst_use_mitex` is deliberately left at its `True` default: the native
# emission path is reached from this SAME fixture via a `-D
# typst_use_mitex=0` CLI override in the test module, rather than a second
# fixture project.

project = "Inline Math After Text Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    # De-collided per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule
    # (a bare "index" target would collide with the unconditional
    # docname-derived content file, index.typ) -- "master.typ" carries no
    # special meaning here.
    ("index", "master.typ", "Inline Math After Text Render Gate", "Test Author"),
]
