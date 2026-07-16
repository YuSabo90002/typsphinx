Figure Length Render Gate
==========================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, D-04). It exercises the FIG-01
``_convert_length_to_typst()`` fix against a real Typst compile: every
``:width:`` case below must compile without aborting, the ``px`` case must
be present in the generated ``.typ`` as a converted ``pt`` value, and no raw
unconvertible unit may leak into the output.

Pixel Width
-----------

.. figure:: image.png
   :width: 200px

   Pixel-width figure case.

Percentage Width
-----------------

.. figure:: image.png
   :width: 50%

   Percentage-width figure case.

Em Width
--------

.. figure:: image.png
   :width: 3em

   Em-width figure case.

Bare Unitless Width
--------------------

.. figure:: image.png
   :width: 300

   Bare unitless width figure case (treated as px per D-02).

Inch Width
----------

.. figure:: image.png
   :width: 2in

   Inch-width figure case.

Unknown Unit Width
--------------------

.. figure:: image.png
   :width: 1ex

   Unknown/unconvertible-unit figure case (must warn and drop, never leak
   the raw unit into Typst output).

Figwidth Pixel
--------------

.. figure:: image.png
   :figwidth: 400px

   Figwidth-pixel figure case (LEN-01): must wrap
   ``block(width: 300pt)[#figure(``.

Figwidth Percentage
--------------------

.. figure:: image.png
   :figwidth: 75%

   Figwidth-percentage figure case (LEN-01): must wrap
   ``block(width: 75%)[#figure(`` (pass-through, unchanged).

Figwidth Unknown Unit
-----------------------

.. figure:: image.png
   :figwidth: 5ex

   Figwidth unknown-unit figure case (LEN-01): must warn and drop, never
   leak the raw unit into Typst output, and never wrap in a block(width:)
   -- no dimension is applied.
