# Sphinx configuration for the inline-literal-overflow render-gate fixture.
#
# Minimal self-contained project used by
# tests/test_inline_literal_overflow_render_gate.py to prove, via a real
# compile, that a long run of colon-leading inline ``literal`` role tokens
# (e.g. ``:cpp:any:``) gets a leading zero-width-space break opportunity in
# the non-in_table branch of visit_literal, so Typst's line-breaker can wrap
# the run at token boundaries instead of overflowing the right margin and
# clipping mid-token (FID-10).

project = "Inline Literal Overflow Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Inline Literal Overflow Render Gate", "Test Author"),
]
