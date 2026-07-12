# Sphinx configuration for the GATE-01 graphviz/inheritance-diagram
# graceful-degrade render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the DEG-01/DEG-02 graceful-degrade placeholder fix in a real
# compile: sphinx-build -> typst.compile() -> pypdf text-extraction,
# asserting the placeholder wording is present and no raw DOT/diagram-spec
# source leaks into the generated .typ (Issue #114, D-01).

import os
import sys

# Make mymodule.py (this fixture's minimal importable class hierarchy)
# resolvable for the inheritance-diagram directive without depending on
# typsphinx's own source tree.
sys.path.insert(0, os.path.abspath("."))

project = "Graphviz Degrade Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Graphviz Degrade Render Gate", "Test Author"),
]
