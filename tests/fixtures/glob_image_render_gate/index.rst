Glob Image Render Gate
=======================

This fixture references a figure image via a ``*``-glob URI, where only a
single concrete candidate exists on disk. Mirrors the Sphinx doc corpus's
glob-figure case.

Before the fix, a typstpdf build aborted because the emitted image path was
never resolved to the concrete file that exists on disk.

.. figure:: /_static/pic.*

   A figure referenced via a glob URI that must resolve to the one concrete
   candidate file present under the static directory.
