Paragraph Propagated Target Render Gate
=======================================

This fixture reproduces the corpus fatal where an explicit target placed
immediately before a **paragraph** (not a section) has its id propagated onto
the paragraph by docutils, but the translator emitted no matching anchor -- so
a same-document cross-reference dangled and the compile aborted at the semantic
label-resolution pass.

Propagated target before a paragraph
------------------------------------

.. _my-para-target:

The behavior can be modified in the following ways -- this paragraph carries the
propagated id and must now emit a ``<my-para-target>`` anchor.

Propagated target before a bullet list
--------------------------------------

.. _my-list-target:

* first bullet -- the list node carries the propagated id
* second bullet

References back to the propagated targets
-----------------------------------------

This role emits ``link(<my-para-target>, ...)`` and must resolve to the
paragraph anchor: :ref:`custom paragraph link text <my-para-target>`.

This role emits ``link(<my-list-target>, ...)`` and must resolve to the bullet
list anchor: :ref:`custom list link text <my-list-target>`.
