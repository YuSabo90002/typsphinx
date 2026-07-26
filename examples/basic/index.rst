Basic Sphinx-Typst Example
===========================

Welcome to the basic example of typsphinx!

This example demonstrates how to use Sphinx with the Typst builder
to generate beautiful Typst documents from reStructuredText sources.

Introduction
------------

typsphinx is a Sphinx extension that allows you to:

- Convert Sphinx documentation to Typst markup
- Generate high-quality PDF output using Typst
- Use Sphinx's powerful features with Typst's modern typesetting

Getting Started
---------------

To build this example:

.. code-block:: bash

   # Generate Typst output
   sphinx-build -b typst . _build/typst

   # Generate PDF output directly
   sphinx-build -b typstpdf . _build/pdf

Basic Features
--------------

Text Formatting
~~~~~~~~~~~~~~~

You can use standard reStructuredText formatting:

- **Bold text** for emphasis
- *Italic text* for subtle emphasis
- ``Inline code`` for code snippets

Lists work as expected:

1. First item
2. Second item
3. Third item

Code Examples
~~~~~~~~~~~~~

Here's a simple Python code block:

.. code-block:: python

   def greet(name):
       """A simple greeting function."""
       print(f"Hello, {name}!")

   greet("World")

You can also use other languages:

.. code-block:: javascript

   function add(a, b) {
       return a + b;
   }

   console.log(add(2, 3));

Mathematics
~~~~~~~~~~~

Inline math: :math:`E = mc^2`

Block math:

.. math::

   \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}

Tables
~~~~~~

Simple tables are supported:

.. list-table:: Feature Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - Sphinx HTML
     - Sphinx Typst
   * - Fast build
     - ✓
     - ✓
   * - Beautiful PDF
     -
     - ✓
   * - Cross-references
     - ✓
     - ✓

Conclusion
----------

This example shows the basic usage of typsphinx. For more
advanced features, check out the advanced examples in the ``examples/``
directory.

.. seealso::

   - `Sphinx Documentation <https://www.sphinx-doc.org/>`_
   - `Typst Documentation <https://typst.app/docs/>`_
   - `typsphinx Repository <https://github.com/YuSabo90002/typsphinx>`_
