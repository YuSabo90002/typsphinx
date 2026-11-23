# Fixture for tests/test_unhandled_nodes_render_gate.py (M009, issue #194):
# a minimal project exercising the "option_list" construct through -b typstpdf.

project = "Unhandled Nodes Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# Keep the description's straight double quotes literal (E3) instead of
# letting the SmartQuotes transform curl them.
smartquotes = False

# "master.typ" avoids colliding with the docname-derived content file index.typ.
typst_documents = [
    ("index", "master.typ", "Unhandled Nodes Render Gate", "Test Author"),
]
