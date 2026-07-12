# Sphinx configuration for the glob-image render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by tests/test_glob_image_render_gate.py
# to prove the `typstpdf` builder resolves a `*`-glob image URI to a
# concrete on-disk file before compiling. This is the fast, offline
# reproduction of the corpus fatal GATE-02 surfaced:
#
#     TypstError: file not found (searched at <build>/_static/translation.*)
#
# Root cause: TypstBuilder.post_process_images() never consulted the image
# node's `candidates` dict (populated during Sphinx's read-phase
# ImageCollector) and declared no `supported_image_types`, so a `*`-glob
# image URI (e.g. `.. figure:: /_static/pic.*`) was never resolved to the
# concrete file (`pic.png`) that actually exists on disk -- the literal,
# unresolved glob string flowed through to both the emitted `image(...)`
# call and copy_image_files(), which tried to copy a nonexistent "pic.*"
# file.

project = "Glob Image Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Mirror the Sphinx doc/ corpus conf.py: the referenced image lives under a
# declared html_static_path directory (`_static/`), exactly as the corpus's
# `.. figure:: /_static/translation.*` case does.
html_static_path = ["_static"]

# index must be a master document (not merely an included one) so the writer
# emits the full template and TypstPDFBuilder.finish() actually compiles it
# to PDF -- the only build path where the unresolved-glob fatal is
# observable.
typst_documents = [
    ("index", "index", "Glob Image Render Gate", "Test Author"),
]
