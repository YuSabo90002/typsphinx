# Sphinx configuration for the codly-caption-listitem-leak render-gate
# fixture.
#
# Minimal self-contained project used by
# tests/test_codly_caption_listitem_leak_render_gate.py to prove, via a real
# compile, that a captioned literal_block nested in a list_item opens its
# `{ }` wrapper as `#{` (re-entering Typst code mode) instead of leaking the
# codly config call as visible prose (FID-12).

project = "Codly Caption Listitem Leak Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Codly Caption Listitem Leak Render Gate", "Test Author"),
]
