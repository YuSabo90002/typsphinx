Basic Examples
==============

Simple examples to get started with typsphinx.

Minimal Configuration
---------------------

The simplest possible setup:

**conf.py**:

.. code-block:: python

   project = "My Project"
   author = "My Name"
   extensions = ["typsphinx"]

   typst_documents = [
       ("index", "output", project, author, "typst"),
   ]

**index.rst**:

.. code-block:: rst

   My Documentation
   ================

   Welcome to my documentation!

   Introduction
   ------------

   This is a simple example.

**Build**:

.. code-block:: bash

   sphinx-build -b typstpdf source/ build/pdf

Adding Math
-----------

Include mathematical expressions:

**index.rst**:

.. code-block:: rst

   Math Examples
   =============

   Inline math: :math:`E = mc^2`

   Display math:

   .. math::

      \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}

The math is automatically rendered using mitex (LaTeX) or native Typst math.

Code Blocks
-----------

Add syntax-highlighted code:

**index.rst**:

.. code-block:: rst

   Code Example
   ============

   Python code:

   .. code-block:: python

      def hello(name):
          print(f"Hello, {name}!")

      hello("World")

Code is highlighted using the codly package.

Tables
------

Create tables:

**index.rst**:

.. code-block:: rst

   Data Table
   ==========

   .. list-table:: Feature Comparison
      :header-rows: 1

      * - Feature
        - typsphinx
        - LaTeX
      * - Setup time
        - 5 minutes
        - 2 hours
      * - PDF quality
        - Excellent
        - Excellent
      * - Ease of use
        - Easy
        - Complex

Images
------

Include images:

**index.rst**:

.. code-block:: rst

   Figures
   =======

   .. figure:: _static/diagram.png
      :width: 80%
      :align: center

      Figure 1: System Architecture

Make sure to create a ``_static/`` directory for your images.

Cross-References
----------------

Link to sections and documents:

**index.rst**:

.. code-block:: rst

   Documentation Structure
   =======================

   See :ref:`installation-section` for setup instructions.

   .. _installation-section:

   Installation
   ------------

   Installation instructions here.

**Another file (api.rst)**:

.. code-block:: rst

   API Reference
   =============

   See :doc:`/index` for the main documentation.

Lists and Admonitions
---------------------

**index.rst**:

.. code-block:: rst

   Important Notes
   ===============

   .. note::

      This is a note admonition.

   .. warning::

      This is a warning admonition.

   Bullet list:

   - Item 1
   - Item 2
   - Item 3

   Numbered list:

   1. First
   2. Second
   3. Third

Complete Basic Example
-----------------------

Here's a complete minimal project:

**Directory structure**:

.. code-block:: text

   myproject/
   ├── source/
   │   ├── conf.py
   │   ├── index.rst
   │   └── _static/
   └── build/

**conf.py**:

.. code-block:: python

   project = "My Project"
   copyright = "2025, My Name"
   author = "My Name"
   release = "1.0"

   extensions = ["typsphinx"]

   typst_documents = [
       ("index", "myproject", project, author, "typst"),
   ]

   typst_use_mitex = True

**index.rst**:

.. code-block:: rst

   My Project Documentation
   ========================

   .. toctree::
      :maxdepth: 2

      introduction
      usage
      api

   Introduction
   ------------

   This project does amazing things.

   Features:

   - Feature 1
   - Feature 2
   - Feature 3

   Quick Example
   -------------

   .. code-block:: python

      import myproject
      result = myproject.do_something()
      print(result)

**Build and view**:

.. code-block:: bash

   sphinx-build -b typstpdf source/ build/pdf
   open build/pdf/myproject.pdf

Next Steps
----------

- Explore :doc:`advanced` for more complex examples
- Read :doc:`/user_guide/configuration` for all options
- Learn about :doc:`/user_guide/templates` for customization
