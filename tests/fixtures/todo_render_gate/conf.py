# Sphinx configuration for the GATE-01 todo render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the TODO-01 visit_todo_node/depart_todo_node fix in a real compile:
# sphinx-build -> typst.compile() -> pypdf text-extraction, asserting the
# `.. todo::` body renders inside a gentle-clues task() box titled "Todo"
# when todo_include_todos=True (D-01), and is entirely absent when
# todo_include_todos is False -- mirroring every official Sphinx builder's
# SkipNode gating.

project = "Task Box Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "sphinx.ext.todo",
    "typsphinx",
]

# Explicit per 16-RESEARCH.md Pitfall 1 -- the render path is never
# exercised without it; mirrors the real corpus's effective config.
todo_include_todos = True

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Task Box Render Gate", "Test Author"),
]
