Converted Source
=================

This document's figure references an SVG. A custom post-transform
(registered in ``conf.py``) "converts" it to an ABSOLUTE path under
``<doctreedir>/images/chart.png`` -- reproducing exactly what Sphinx's real
``ImageConverter``/``ImageDownloader`` post-transforms do for any image
that needs conversion or download.

.. figure:: _static/chart.svg

   A figure whose URI is rewritten to an absolute path by the fixture's
   fake image converter, landing at the same basename an ordinary source
   image already occupies.
