# Fixture for tests/test_unhandled_nodes_render_gate.py (M009, issue #194,
# SC4): registers a test-only inline node with NO Typst visitor (via the
# fixture-local ``unknown_node_ext`` extension) and places it in a body
# paragraph, a list item, a table cell, a heading and a definition-list term,
# so the generic unknown_visit fallback must keep every placement compilable.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

project = "Unhandled Nodes Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx", "unknown_node_ext"]

# "master.typ" avoids colliding with the docname-derived content file index.typ.
typst_documents = [
    ("index", "master.typ", "Unhandled Nodes Render Gate", "Test Author"),
]
