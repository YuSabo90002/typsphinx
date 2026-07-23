Nested Master Render Gate
==========================

This fixture's only master document sits at the nested docname ``api/index``.
It proves that ``-b typstpdf`` resolves a sibling ``#include()`` and an
upward-crossing ``image()`` reference on the same basis the translator emits
them -- the master's own directory -- instead of the outdir root.

.. toctree::

   usage

A root-level image referenced from a nested master, forcing the emitted
Typst to climb one directory (``image("../logo.png")``).

.. image:: /logo.png
