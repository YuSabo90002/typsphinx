# Sphinx configuration for the S04 malformed-DOT gate fixture.
#
# Minimal self-contained project used by
# tests/test_graphviz_malformed_dot_gate.py to pin what ACTUALLY happens
# when a graphviz directive carries syntactically broken DOT.
#
# Read the module docstring of that test before changing anything here: the
# measured behaviour CONTRADICTS R006's and D002's literal text. Translation
# is clean, and the downstream `typst.compile()` hard-fails carrying
# Graphviz's own syntax-error text. D012 governs -- gate what is measured.
#
# Deliberately DISJOINT from tests/fixtures/graphviz_render_gate/ (MEM023):
# that fixture's gate asserts a clean build that COMPILES to a PDF, so
# adding a compile-breaking diagram to it would turn that gate red. A
# deliberately-unbuildable document needs its own project.

project = "Graphviz Malformed Dot Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
    "sphinx.ext.graphviz",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py). The target is "master.typ" rather than a
# bare "index" to avoid colliding with the unconditional docname-derived
# content file index.typ; it carries no other special meaning.
typst_documents = [
    ("index", "master.typ", "Graphviz Malformed Dot Gate", "Test Author"),
]

# No font configuration anywhere, deliberately: matching the sibling
# graphviz fixtures so this one differs from them in exactly one dimension
# -- the DOT body being syntactically invalid.
