# Phase 74 plan 02, TRN-01 / TRN-02: the doctest_block real-compile gate
# fixture (GATE-01). D-06's two contexts:
#   - context (a): a doctest block in plain paragraph position, with a
#     leading paragraph before it AND a trailing paragraph after it -- the
#     trailing paragraph is load-bearing: it is what turns the pre-handler
#     RED into a real `typst.compile()` refusal (`expected semicolon or
#     line break`) instead of a mere content-collapse. Do NOT remove it.
#   - context (b): one master carrying two shapes, both at a NON-FIRST
#     position in their container (also load-bearing -- a first-position
#     doctest block would not exercise the separator discipline the gate
#     is meant to prove):
#       - (b1) a definition-list item whose term is "Examples:", with a
#         leading paragraph before the doctest block in the definition
#         (the sphinx-autoapi `terms.item` position TRN-02 names);
#       - (b2) a bullet-list item with a leading paragraph, the doctest
#         block, then a trailing paragraph in the same item.
#
# Every `typst_documents` target stem is the docname plus `-out.typ` (the
# Phase 47 de-collision rule -- a target equal to its own docname would
# resolve to the same physical path as that docname's own content file).
project = "Doctest Block Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

root_doc = "index"

typst_documents = [
    ("index", "index-out.typ", "Doctest Block Render Gate", "Test Author"),
    (
        "context_a_paragraph",
        "context_a_paragraph-out.typ",
        "Context A - Doctest Block In Paragraph Position",
        "Test Author",
    ),
]
