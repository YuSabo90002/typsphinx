# Sphinx configuration for the epigraph attribution render-gate fixture
# (backlog: attribution source-leak fix).
#
# Minimal self-contained project used by tests/test_epigraph_render_gate.py to
# prove, via a real `-b typstpdf` compile, that a block-quote / `.. epigraph::`
# ATTRIBUTION renders its inline children as EVALUATED content, not literal
# Typst source. The buggy handler emitted the attribution as a markup-mode
# `attribution: [ ... ]` argument while its inline children were emitted
# through the code-mode visitors (text("...")/emph({...})/raw("...")). Inside a
# markup `[...]` argument those bytes are literal prose, so Typst typesets the
# author name verbatim -- `text(“Author”)` (curly quotes from smart-quote
# typography) instead of `Author` -- and a lone `_` in an inline-literal child
# (e.g. ``_t``) opens a stray unclosed emphasis span that aborts the compile.
project = "Epigraph Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# One master document compiled straight to PDF by the typstpdf builder.
typst_documents = [
    ("index", "index", project, author),
]
