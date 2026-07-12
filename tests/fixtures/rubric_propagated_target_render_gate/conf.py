"""Sphinx config for the rubric propagated-target anchor render-gate fixture.

Reproduces GATE-02 corpus fatal #23 offline -- the twenty-third corpus fatal,
surfaced only after bugs #17-#22 unblocked the earlier label fatals. On
Sphinx's own ``doc/`` tree, ``man/sphinx-build.rst`` has an explicit
``.. _makefile_options:`` target immediately before ``.. rubric:: Makefile
Options``. docutils' ``PropagateTargets`` transform moves the target's id onto
the FOLLOWING body element -- for a rubric, that is the ``rubric`` node itself.
``visit_rubric`` rendered a bold heading via a dummy ``strong`` node but never
read ``node["ids"]``, so no anchor was emitted, while a cross-document-safe
``:ref:`Makefile or Make.bat <makefile_options>`` renders ``link(<...>, ...)``.
``typst.compile()`` then aborted at the semantic label-resolution pass with::

    TypstError: label `<...:makefile-options>` does not exist in the document

This fixture also exercises the rest of the missing-anchor sweep that shipped
with the rubric fix, each a body/container node that can carry a propagated (or
own ``:name:``/``:label:``) id but emitted no anchor (or a broken one):

- a ``.. figure::`` whose PROPAGATED id differs from its own caption id
  (the figure self-anchors only ``ids[0]``);
- a captioned ``.. code-block:: :name:`` (the id lands on the outer
  ``literal-block-wrapper`` container);
- a propagated target before a plain ``.. code-block::`` (the id lands on the
  literal_block, previously emitted as a non-joining ` <label>` postfix);
- a ``.. math:: :label:`` labeled equation referenced with ``:eq:`` (previously
  a non-parsing ` <label>` postfix on the equation).

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Rubric Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    (
        "index",
        "index",
        "Rubric Propagated Target Render Gate",
        "typsphinx tests",
    ),
]
