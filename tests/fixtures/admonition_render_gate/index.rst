Admonition Render Gate
=======================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (D-04). It is not meant to be read as
prose -- it exercises the admonition markup/code-mode fix against a real
Typst compile.

Golden Note
-----------

.. note::

   This setting only applies to local custom templates (``typst_template``).
   Typst Universe packages (``typst_package``) handle assets automatically.

Note With A Bullet List
------------------------

.. note::

   Before list.

   - Item one.
   - Item two.

Warning With A Literal Block
------------------------------

.. warning::

   Before code.

   .. code-block:: python

      x = 1

Hint Type
---------

.. hint::

   This is a hint admonition (D-06 new type).

Danger Type
-----------

.. danger::

   This is a danger admonition (D-06 new type).

Nested Admonition
------------------

.. note::

   Outer note before nested warning.

   .. warning::

      Inner warning nested inside the outer note.

   Outer note after nested warning.
