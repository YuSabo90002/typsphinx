# Sphinx configuration for the D-04 admonition render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the admonition markup/code-mode fix in a real compile: sphinx-build
# -> typst.compile() -> pypdf text-extraction, asserting no literal Typst
# source (par(/text(/raw() leaks into rendered admonition prose.

project = "Admonition Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus the gentle-clues @preview import -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    # OUT-01 self-collision (D-01): "index" as the target used to be safe
    # because pre-Phase-47 output was one file per docname; now every
    # docname unconditionally gets a content file at its own docname path
    # (index.typ), so a target that resolves to the SAME path would collide
    # with it. De-collided per 47-EXPECTED-STRUCTURE.md's fixture
    # de-collision rule -- "master.typ" carries no special meaning here.
    ("index", "master.typ", "Admonition Render Gate", "Test Author"),
]
