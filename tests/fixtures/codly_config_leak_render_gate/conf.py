# Sphinx configuration for the per-block codly-config markup/code-mode
# leak render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, via a real compile, that visit_literal_block emits every per-block
# codly configuration call (``codly(number-format: none)`` for the
# line-numbers-off case, ``codly-range(highlight: (...))`` for the
# ``:emphasize-lines:`` case) as an EXECUTED code-mode call, never as
# markup content that Typst would typeset as literal prose.

project = "Codly Config Leak Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    # De-collided per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule
    # (a bare "index" target would collide with the unconditional
    # docname-derived content file, index.typ) -- "master.typ" carries no
    # special meaning here.
    ("index", "master.typ", "Codly Config Leak Render Gate", "Test Author"),
]
