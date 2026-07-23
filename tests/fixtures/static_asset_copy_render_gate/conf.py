# Sphinx configuration for the static-asset-copy render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by tests/test_static_asset_copy_gate.py
# to prove the `typstpdf` builder copies a `_static/`-referenced figure image
# into the Typst output tree before compiling. This is the fast, offline
# reproduction of the corpus fatal GATE-02 surfaced:
#
#     TypstError: file not found (searched at <build>/_static/python-logo.png)
#
# Root cause: TypstPDFBuilder.write_doc() overrode the base write_doc() but
# omitted the self.post_process_images(doctree) call, so self.images stayed
# empty during a typstpdf build, copy_image_files() early-returned, and the
# referenced asset was never copied -- so typst.compile() in finish() aborted.

project = "Static Asset Copy Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Mirror the Sphinx doc/ corpus conf.py: the referenced image lives under a
# declared html_static_path directory (`_static/`), exactly as the corpus's
# `.. figure:: _static/python-logo.png` case does.
html_static_path = ["_static"]

# index must be a master document (not merely an included one) so the writer
# emits the full template and TypstPDFBuilder.finish() actually compiles it to
# PDF -- the only build path where the missing-asset fatal is observable.
typst_documents = [
    ("index", "index", "Static Asset Copy Render Gate", "Test Author"),
]
