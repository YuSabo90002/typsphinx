# Sphinx configuration for the S04 external-.dot refusal gate fixture.
#
# Minimal self-contained project used by
# tests/test_graphviz_external_dot_gate.py to pin the boundary R007 draws:
# the external-file form `.. graphviz:: some.dot` is scoped OUT, and must
# refuse with the bordered placeholder plus exactly one warning rather than
# silently starting to work.
#
# Deliberately DISJOINT from tests/fixtures/graphviz_render_gate/ (MEM023):
# that fixture's gate asserts a clean build with ZERO degrade warnings, so
# adding an intentionally-refusing directive to it would turn that gate red.
# This refusal needs its own project.

project = "Graphviz External Dot Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
    "sphinx.ext.graphviz",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py). The target is "master.typ" rather than a bare
# "index" to avoid colliding with the unconditional docname-derived content
# file index.typ; it carries no other special meaning.
typst_documents = [
    ("index", "master.typ", "Graphviz External Dot Gate", "Test Author"),
]

# No font configuration anywhere, deliberately: matching
# tests/fixtures/graphviz_render_gate/conf.py so this fixture differs from
# it in exactly one dimension -- the external-file directive form.
