Figure Propagated Target Render Gate
=====================================

This fixture reproduces D-10's three measured shapes for a captioned figure
immediately preceded by a standalone target, via docutils' explicit
``.. _label:`` target directive and its ``PropagateTargets`` transform (see
``conf.py``'s module docstring for the scoping rule). Both the figure's own
self-anchor and the propagated target's anchor must be emitted for the
document to compile.

Named figure preceded by a target
----------------------------------

.. _fig-target:

.. figure:: image.png
   :name: fig-name

   Caption with sentinel FIGTGTNAMEDSENTINEL present.

Unnamed figure preceded by a target
-------------------------------------

.. _fig-target-noname:

.. figure:: image.png

   Caption with sentinel FIGTGTNONAMESENTINEL present.

Named figure inside a bullet-list item, preceded by a target
----------------------------------------------------------------

* Lead-in text for the list item.

  .. _fig-target-li:

  .. figure:: image.png
     :name: fig-name-li

     Caption with sentinel FIGTGTLISTSENTINEL present.

References back to the named figure and propagated targets
----------------------------------------------------------

Numbered reference to the named figure: :numref:`fig-name`.

Explicit-text references to each propagated target and the list-item figure's
own name (explicit link text is mandatory here -- a bare ``:ref:`` to a
captioned figure would default to that figure's caption text and duplicate
the sentinel):

- :ref:`link to fig-target <fig-target>`
- :ref:`link to fig-target-noname <fig-target-noname>`
- :ref:`link to fig-target-li <fig-target-li>`
- :ref:`link to fig-name-li <fig-name-li>`
