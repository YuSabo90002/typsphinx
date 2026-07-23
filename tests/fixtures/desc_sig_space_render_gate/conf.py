"""Sphinx config for the desc_sig_space render-gate fixture (FID-07 + FID-08).

Mirrors the desc_signature_concat_render_gate fixture's minimal shape. No
intersphinx/network dependency is needed here -- the audit repros (a
``py:class`` annotation prefix, a ``c:function`` signature, and an inline
``cpp:expr`` fragment) are all self-contained, unresolved-domain-token text
that renders without cross-reference resolution.
"""

project = "Desc Sig Space Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Desc Sig Space Render Gate", "typsphinx tests"),
]
