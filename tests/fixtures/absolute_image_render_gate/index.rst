Absolute Image Render Gate
============================

This fixture references an SVG figure. A custom post-transform (registered
in ``conf.py``) rewrites its ``uri`` to an ABSOLUTE path under
``<doctreedir>/images/`` -- reproducing exactly what Sphinx's real
``ImageConverter``/``ImageDownloader`` post-transforms do for any image that
needs conversion or download (Issue #130).

Before the fix, a typstpdf build of this fixture failed to copy the
converted asset ("are the same file") and emitted a garbled image path that
aborted the Typst compile ("file not found").

.. figure:: _static/diagram.svg

   A figure whose URI is rewritten to an absolute path by the fixture's
   fake image converter.
