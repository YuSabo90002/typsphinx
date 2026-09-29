# Sphinx configuration for the S01 diagraph escaping render-gate fixture.
#
# Minimal two-document project used by the S01 gate to prove (a) that BOTH a
# master document and an included document carry the
# @preview/diagraph:0.3.7 import, and (b) that DOT containing every
# R013-hazardous character survives escape_typst_string() into a render()
# call that typst.compile() accepts.

project = "Diagraph Escaping Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template; the
# toctree'd "included" document then exercises the writer's SEPARATE
# included-document import path (typsphinx/writer.py), which must carry the
# diagraph import too.
typst_documents = [
    # OUT-01 self-collision (D-01): every docname unconditionally gets a
    # content file at its own docname path (index.typ), so a target of
    # "index" would collide with it. "master.typ" carries no special
    # meaning -- it is just the de-collided wrapper path.
    ("index", "master.typ", "Diagraph Escaping Render Gate", "Test Author"),
]
