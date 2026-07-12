Rubric Propagated Target Render Gate
======================================

This fixture reproduces the corpus fatal where an explicit target placed
immediately before a ``.. rubric::`` has its id propagated by docutils onto the
``rubric`` node, but the translator emitted no matching anchor, so a
same-document cross-reference dangled and the compile aborted at the semantic
label-resolution pass. It also covers the rest of the missing-anchor sweep.

References that must resolve
-----------------------------

- The rubric: :ref:`jump to the rubric <my-rubric-target>`.
- The figure (propagated id, not its caption id):
  :ref:`jump to the figure <my-fig-target>`.
- The captioned code block (id on the container):
  :ref:`jump to the captioned block <captioned-block>`.
- The plain code block (propagated id on the literal_block):
  :ref:`jump to the plain block <my-code-target>`.
- The labeled equation: :eq:`euler-eq`.
- The list item (target between bullet items):
  :ref:`jump to the list item <my-list-target>`.

Propagated target before a rubric
-----------------------------------

.. _my-rubric-target:

.. rubric:: Makefile Options

Text after the rubric; the ``rubric`` node carries the propagated
``my-rubric-target`` id and must now emit a matching anchor.

Propagated target before a figure with its own caption id
-----------------------------------------------------------

.. _my-fig-target:

.. figure:: img.png
   :name: my-own-fig

   A caption. The figure self-anchors its own ``my-own-fig`` id; the
   PROPAGATED ``my-fig-target`` id (a different id) must also be anchored.

Captioned code block whose name lands on the container
--------------------------------------------------------

.. code-block:: python
   :name: captioned-block
   :caption: A captioned block

   captioned = True

Propagated target before a plain code block
---------------------------------------------

.. _my-code-target:

.. code-block:: python

   plain = True

Labeled equation
------------------

.. math::
   :label: euler-eq

   e^{i pi} + 1 = 0

Propagated target between bullet list items
---------------------------------------------

* first bullet item that spans
  more than a single line of text

  .. _my-list-target:

* second bullet item after the target; docutils propagates the
  ``my-list-target`` id onto THIS list_item node

Control: a rubric with no preceding target
--------------------------------------------

.. rubric:: Plain Rubric

This control rubric has no preceding explicit target, so it must carry no ids
and emit no anchor (byte-unchanged regression control).
