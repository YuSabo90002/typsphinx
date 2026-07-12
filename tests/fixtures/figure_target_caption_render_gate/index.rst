Figure Target Caption Render Gate
====================================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, D-04). It exercises the FIG-02
caption buffer-swap and internal/external ``:target:`` refid/refuri
branching against a real Typst compile: each caption below must appear
exactly once in the extracted PDF text, with its markup-special characters
intact and no stray juxtaposed ``text(...)`` leak.

.. _internal-anchor-section:

Internal Anchor Section
-------------------------

This section is the destination of the internal ``:target:`` figure below.

Internal Target Figure
------------------------

.. figure:: image.png
   :target: internal-anchor-section_

   Caption with special chars \_ \* \` \[ \] and sentinel
   FIGCAPINTERNALQ7X9 present.

External Target Figure
------------------------

.. figure:: image.png
   :target: https://example.com/external-target

   Caption with special chars \_ \* \` \[ \] and sentinel
   FIGCAPEXTERNALK3M2 present.
