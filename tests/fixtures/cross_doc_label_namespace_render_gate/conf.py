"""Sphinx config for the cross-document label-namespacing render gate.

A minimal multi-document project: the master ``index`` toctree pulls in two
sibling documents (``pagea`` and ``pageb``) that BOTH define a section slugging
to ``shared-topic``. Flattened into one Typst master via ``#include()``, those
would collide to a duplicate ``<shared-topic>`` label -- the exact GATE-02
corpus fatal (``label ... occurs multiple times``) -- unless every label is
namespaced by its source document (bug #21).

Second purpose (Phase 22): the master's ``typst_documents`` target
(``namespace-gate``) deliberately differs from its docname (``index``), so a
build of this project also serves as the automated, real-compile proof that
Phase 22's ``get_target_uri`` decision (stays docname-based, never
target-name-aware) does not break a cross-document ``:ref:`` into or out of a
RENAMED master -- a docname-to-URI mapping that had followed the write-path
rename would surface here as a Typst ``label ... does not exist`` fatal.
"""

project = "Cross-Doc Namespace Gate"
author = "Test Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "namespace-gate", "Cross-Doc Namespace Gate", "Test Author"),
]
