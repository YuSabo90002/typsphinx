Advanced Sphinx-Typst Features
================================

Welcome to the advanced example of typsphinx!

This example demonstrates advanced features including:

- Multi-document projects with toctree
- Mathematical equations with mitex
- Cross-references and labels
- Tables and figures
- Code highlighting with codly
- Custom templates (optional)

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Contents

   chapter1
   chapter2

Introduction
------------

This advanced example shows how to use typsphinx for complex
documentation projects with multiple documents, extensive cross-referencing,
and rich mathematical content.

.. _intro-label:

Key Features Demonstrated
--------------------------

1. **Multi-Document Support**

   The project is organized into multiple chapters using Sphinx's ``toctree``
   directive. Each chapter is a separate ``.rst`` file that gets converted
   to a separate ``.typ`` content file. The chapters are combined by guarded
   ``include()`` calls that live in this document's own content file, at the
   toctree's position -- each one runs only when the wrapper being compiled
   has published that edge, so a chapter is rendered once per master that
   actually reaches it.

2. **Mathematics with mitex**

   typsphinx uses the `mitex <https://typst.app/universe/package/mitex>`_
   package to render LaTeX math expressions in Typst. This provides excellent
   compatibility with existing Sphinx/LaTeX math.

3. **Cross-References**

   Sphinx's powerful cross-reference system is preserved in Typst output,
   allowing you to reference sections, equations, figures, and tables
   across your documentation.

4. **Code Highlighting**

   Source code is highlighted using the `codly <https://typst.app/universe/package/codly>`_
   package, providing beautiful syntax highlighting and line numbers.

Quick Start
-----------

Build this example:

.. code-block:: bash

   # Generate Typst output
   sphinx-build -b typst . _build/typst

   # Generate PDF directly
   sphinx-build -b typstpdf . _build/pdf

Project Structure
-----------------

::

   advanced/
   ├── conf.py                 # Sphinx configuration
   ├── index.rst               # This file (master document)
   ├── chapter1.rst            # Chapter 1: Mathematics
   ├── chapter2.rst            # Chapter 2: Figures and Tables
   ├── _typst/                 # Typst-owned template directory (optional)
   │   └── custom.typ
   ├── _templates/             # Sphinx's own templates_path override directory
   └── README.md               # Build instructions

Mathematics Example
-------------------

Inline math: The famous equation :math:`E = mc^2` revolutionized physics.

Block math equation with label:

.. math::
   :label: euler-identity

   e^{i\pi} + 1 = 0

Euler's identity (equation :eq:`euler-identity`) is considered one of the
most beautiful equations in mathematics.

See Also
--------

- :ref:`intro-label` - Link to introduction
- :doc:`chapter1` - Mathematics chapter
- :doc:`chapter2` - Figures and tables chapter
