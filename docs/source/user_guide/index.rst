User Guide
==========

This section provides comprehensive documentation on using typsphinx.

.. toctree::
   :maxdepth: 2

   configuration
   builders
   templates
   output_layout

Overview
--------

typsphinx integrates Sphinx with Typst to provide high-quality PDF output
without the complexity of LaTeX.

The extension provides two builders:

- **typst**: Generates Typst markup files (``.typ``)
- **typstpdf**: Generates PDF files directly using typst-py

Main Topics
-----------

:doc:`configuration`
   Learn about all configuration options available in ``conf.py``

:doc:`builders`
   Understand the difference between typst and typstpdf builders

:doc:`templates`
   Customize output using Typst templates

:doc:`output_layout`
   Understand which emitted ``.typ`` file to compile and where it is written
