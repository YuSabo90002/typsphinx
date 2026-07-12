"""Sphinx config for the cross-document label-namespacing render gate.

A minimal multi-document project: the master ``index`` toctree pulls in two
sibling documents (``pagea`` and ``pageb``) that BOTH define a section slugging
to ``shared-topic``. Flattened into one Typst master via ``#include()``, those
would collide to a duplicate ``<shared-topic>`` label -- the exact GATE-02
corpus fatal (``label ... occurs multiple times``) -- unless every label is
namespaced by its source document (bug #21).
"""

project = "Cross-Doc Namespace Gate"
author = "Test Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Cross-Doc Namespace Gate", "Test Author"),
]
