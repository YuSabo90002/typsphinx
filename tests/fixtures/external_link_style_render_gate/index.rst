External Link Style Render Gate
=================================

This fixture exists solely to be compiled to PDF by
``tests/test_external_link_style_render_gate.py`` -- a regression gate for the
two halves of FID-13 (external hyperlink styling and the reference/target
boundary stray-space bug) that existing string-agreement tests never caught
because they never real-compiled the emitted output. It is not meant to be
read as prose.

External reference (styling + boundary)
-----------------------------------------

A named external hyperlink, immediately followed by a period with an
intervening space, proves BOTH FID-13 halves in one compile: the `show link:`
rule must color+underline this reference (D-01/D-02), and the boundary fix
must leave exactly one space before the following period (D-03).

See the FIDTHIRTEENSENTINEL `external reference <https://example.com/>`_ .

Internal reference (unstyled)
-------------------------------

A same-document internal reference, in the SAME document as the external one
above, must stay completely unstyled -- proving the `show link:` rule's URL
type check correctly excludes label-typed internal destinations (D-02).

.. _fidthirteeninternalsentinel:

Internal Target Section
~~~~~~~~~~~~~~~~~~~~~~~~~

A same-document reference: :ref:`fidthirteeninternalsentinel`.
