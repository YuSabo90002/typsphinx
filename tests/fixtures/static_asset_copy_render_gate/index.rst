Static Asset Copy Render Gate
=============================

This fixture references a figure image that lives under the declared
html_static_path directory, mirroring the Sphinx doc corpus case.

Before the fix, a typstpdf build aborted because the referenced static
asset was never copied into the Typst output tree.

.. figure:: _static/python-logo.png

   A figure whose image lives under a static directory and must be copied
   into the Typst output tree for the compile to resolve it.
