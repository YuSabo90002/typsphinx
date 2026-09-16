typsphinx Documentation
=======================

**typsphinx** is a Sphinx extension that integrates the Sphinx documentation generator with the Typst typesetting system.

It combines Sphinx's powerful documentation generation capabilities with Typst's modern typesetting features to create high-quality technical documents.

Key Features
------------

- **Sphinx to Typst Conversion**: Convert reStructuredText/Markdown to Typst format
- **Dual Builder Integration**:

  - ``typst`` builder: Generate Typst markup files
  - ``typstpdf`` builder: Generate PDF directly (no external Typst CLI required)

- **Self-Contained PDF Generation**: Self-contained PDF generation via typst-py
- **Customizable Output**: Customize Typst templates and styles
- **Cross-References**: Reproduce Sphinx cross-references, indexes, and table of contents in Typst
- **Code Highlighting**: Syntax highlighting with codly package
- **Math Support**: LaTeX math via mitex or native Typst math
- **Figure Management**: Embed and reference images, tables, and figures

Quick Links
-----------

- **GitHub Repository**: https://github.com/YuSabo90002/typsphinx
- **PyPI Package**: https://pypi.org/project/typsphinx/
- **Issue Tracker**: https://github.com/YuSabo90002/typsphinx/issues

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
