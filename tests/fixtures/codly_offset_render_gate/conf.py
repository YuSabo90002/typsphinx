# Sphinx configuration for the codly `start:` -> `offset:` API-mismatch
# render-gate fixture (GATE-02 fatal #14).
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, via a real compile, that visit_literal_block emits the codly 1.3.0
# `offset:` parameter (not the removed `start:` parameter) for :linenos:
# code blocks with an explicit :lineno-start:, AND that it emits NO
# spurious offset/start call for the default linenostart=1 case -- covering
# both the `.. code-block::` and `.. literalinclude::` directive forms
# (Sphinx's LiteralInclude always populates highlight_args['linenostart'],
# defaulting to 1, even without an explicit :lineno-start: option).

project = "Codly Offset Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Codly Offset Render Gate", "Test Author"),
]
