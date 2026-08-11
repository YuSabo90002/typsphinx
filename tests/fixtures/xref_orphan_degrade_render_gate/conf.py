"""Sphinx config for the orphan cross-reference degrade render gate.

A minimal multi-document project reproducing the GATE-02 corpus fatal (25th):
the master ``index`` toctree includes ``included``, but ``orphan`` is marked
``:orphan:`` and appears in NO toctree. ``included`` carries a ``:ref:`` to a
labelled section in ``orphan`` AND a ``:ref:`` to a labelled section in
``included`` itself. Flattened into one compiled Typst master, ``orphan.typ`` is
written but never ``#include()``d, so a ``link(<orphan:...>)`` label link to it
dangles and ``typst.compile()`` hard-fails with ``label ... does not exist`` --
unless the cross-reference to the non-included target degrades to plain text.
"""

project = "Orphan Xref Degrade Gate"
author = "Test Author"
release = "1.0"

extensions = ["typsphinx"]

# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Orphan Xref Degrade Gate", "Test Author"),
]
