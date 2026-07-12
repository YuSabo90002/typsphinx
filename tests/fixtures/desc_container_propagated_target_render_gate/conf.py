"""Sphinx config for the desc-container propagated-target anchor render-gate
fixture.

Reproduces GATE-02 corpus fatal #22 offline -- the twenty-second corpus fatal,
surfaced only after bugs #17-#21 unblocked the earlier label fatals. On
Sphinx's own ``doc/`` tree, ``man/sphinx-build.rst`` has an explicit
``.. _make_mode:`` target immediately before ``.. option:: -M buildername``
(an object-description directive). docutils' ``PropagateTargets`` transform
moves the target's id onto the FOLLOWING body element -- for an object
description, that is the outer ``desc`` CONTAINER node, not the
``desc_signature`` (which carries its own, different id, e.g.
``cmdoption-M``). ``visit_desc`` was a no-op and ``depart_desc`` only appended
spacing, so ``node["ids"]`` on the ``desc`` container was never anchored,
while a same-document ``:ref:`` to it renders ``link(<...>, ...)``.
``typst.compile()`` then aborted at the semantic label-resolution pass with::

    TypstError: label `<...:make-mode>` does not exist in the document

Fix: ``visit_desc`` now routes ``node["ids"]`` through the shared
``_emit_id_anchors`` helper (bug #20), mirroring its use in
visit_bullet_list/visit_table/visit_block_quote/etc -- emitted BEFORE any
signature/content children are visited. A ``desc`` node with no ids (the
overwhelming common case) is byte-unchanged.

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Desc Container Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    (
        "index",
        "index",
        "Desc Container Propagated Target Render Gate",
        "typsphinx tests",
    ),
]
