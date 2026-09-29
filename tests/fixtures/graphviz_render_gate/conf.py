# Sphinx configuration for the S02 graphviz render-gate fixture.
#
# Minimal self-contained project used by tests/test_graphviz_render_gate.py
# to prove, in a real compile (sphinx-build -> typst.compile() -> pypdf
# text-extraction), that `.. graphviz::`, `.. digraph::` and `.. graph::`
# all emit real @preview/diagraph diagrams (R001, R002) with no Graphviz
# binary present (R010) and with Japanese labels legible (R012).
#
# Deliberately DISJOINT from tests/fixtures/graphviz_degrade_render_gate/:
# that fixture proves the placeholder is still INTACT for
# inheritance-diagram, this one proves it is GONE for graphviz. Sharing one
# fixture between those two opposite claims is what let them contaminate
# each other, so `sphinx.ext.inheritance_diagram` (and its `mymodule.py`)
# are intentionally absent here.

project = "Graphviz Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
    "sphinx.ext.graphviz",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    # De-collided per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule
    # (a bare "index" target would collide with the unconditional
    # docname-derived content file, index.typ) -- "master.typ" carries no
    # special meaning here.
    ("index", "master.typ", "Graphviz Render Gate", "Test Author"),
]

# No font configuration anywhere, deliberately: the measured prototype
# rendered the Japanese label with none, and templates/base.typ sets only
# `size` and `lang`. Adding one here would hide a real regression.

# numfig must stay True: tests/test_graphviz_render_gate.py
# test_name_yields_resolvable_numref_anchor proves a `:name:` anchor is
# RESOLVABLE by referencing it with `:numref:`, and Sphinx only resolves
# numref to a figure number when figure numbering is enabled.
numfig = True
