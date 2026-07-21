Advanced Examples
=================

Advanced configurations and use cases for typsphinx.

Using Typst Universe Packages
------------------------------

charged-ieee Template
~~~~~~~~~~~~~~~~~~~~~

Use the charged-ieee package for IEEE-style papers:

**conf.py**:

.. code-block:: python

   project = "Machine Learning Applications"
   author = "John Doe"

   # Use IEEE package
   typst_package = "@preview/charged-ieee:0.1.4"

   # Configure template with parameters
   ieee_abstract = """
   This paper presents novel approaches to machine learning
   applications in computer vision.
   """

   ieee_keywords = ["Machine Learning", "Computer Vision", "AI"]

   typst_template_function = {
       "name": "ieee",
       "params": {
           "abstract": ieee_abstract,
           "index-terms": ieee_keywords,
           "paper-size": "us-letter",
       }
   }

   # Detailed author information
   typst_authors = {
       "John Doe": {
           "department": "Computer Science",
           "organization": "MIT",
           "email": "john@mit.edu"
       }
   }

Custom Template Wrapping
-------------------------

Wrap external packages with custom logic:

**_templates/custom_ieee.typ**:

.. code-block:: typst

   #import "@preview/charged-ieee:0.1.4": ieee

   #let project(
     title: "",
     authors: (),
     date: none,
     body
   ) = {
     // Transform simple author tuples to IEEE format
     let ieee_authors = authors.map(name => (
       name: name,
       department: "Engineering",
       organization: "My Organization",
       location: "City, State",
       email: name.split(" ").at(0).lower() + "@example.com"
     ))

     // Define abstract and keywords (could be parameters)
     let ieee_abstract = [
       This document demonstrates custom template wrapping
       with automatic author transformation.
     ]

     let ieee_keywords = (
       "Documentation",
       "Typst",
       "Automation"
     )

     // Apply IEEE template
     show: ieee.with(
       title: title,
       authors: ieee_authors,
       abstract: ieee_abstract,
       index-terms: ieee_keywords,
       bibliography: "refs.bib",
     )

     body
   }

**conf.py**:

.. code-block:: python

   typst_template = "_templates/custom_ieee.typ"

.. important::

   Do **not** also set ``typst_package`` here. The wrapping template already
   declares ``#import "@preview/charged-ieee:0.1.4": ieee`` itself, and setting
   both ``typst_package`` and ``typst_template`` together is unsupported:
   typsphinx emits a build warning naming both config values, ignores the
   ``typst_package`` setting, and honours ``typst_template`` — so the wrapper
   is written and imported as before.

   Use ``typst_package`` **or** ``typst_template`` — not both.

Multi-Document Projects
------------------------

Build multiple related documents:

**conf.py**:

.. code-block:: python

   typst_documents = [
       # (source, output, title, author, class)
       ("index", "main", "Main Documentation", "Team", "typst"),
       ("api/index", "api-reference", "API Reference", "Team", "typst"),
       ("tutorial/index", "tutorial", "Tutorial", "Team", "typst"),
   ]

Each document is built separately with its own output file.

Custom Styling
--------------

Apply custom fonts and colors:

**_templates/styled.typ**:

.. code-block:: typst

   #let project(
     title: "",
     primary-color: blue,
     body
   ) = {
     // Set custom font
     set text(
       font: "New Computer Modern",
       size: 11pt,
     )

     // Custom heading style
     show heading.where(level: 1): it => {
       set text(fill: primary-color, size: 20pt, weight: "bold")
       it
       v(0.5em)
     }

     show heading.where(level: 2): it => {
       set text(fill: primary-color.lighten(20%), size: 16pt)
       it
       v(0.3em)
     }

     // Title page
     align(center)[
       #text(size: 28pt, fill: primary-color, weight: "bold")[
         #title
       ]
     ]

     pagebreak()

     body
   }

**conf.py**:

.. code-block:: python

   typst_template = "_templates/styled.typ"

   typst_template_function = {
       "name": "project",
       "params": {
           "primary-color": "rgb(0, 102, 204)",  # Custom blue
       }
   }

Conditional Content
-------------------

Use different templates for different documents:

**conf.py**:

.. code-block:: python

   # Default template for most documents
   typst_template = "_templates/default.typ"

   # Define multiple documents
   typst_documents = [
       ("index", "main", "Main Docs", "Team", "typst"),
       ("paper", "research-paper", "Research Paper", "Authors", "typst"),
   ]

For document-specific templates, you can use Sphinx's ``per-file`` configuration
or conditional logic in your template.

Bibliographies
--------------

Include bibliographies with BibTeX:

**index.rst**:

.. code-block:: rst

   Research Paper
   ==============

   According to Smith et al. [Smith2023]_, machine learning...

   References
   ----------

   .. [Smith2023] Smith, J. (2023). Machine Learning Advances.
                  Journal of AI Research, 15(2), 123-145.

**Custom template with bibliography**:

.. code-block:: typst

   #let project(title: "", body) = {
     set page(paper: "us-letter")

     text(20pt, weight: "bold")[#title]
     v(2em)

     body

     // Bibliography section
     pagebreak()
     heading(numbering: none)[References]
     // Bibliography rendered from .bib file
   }

Advanced Math
-------------

Complex mathematical expressions:

**index.rst**:

.. code-block:: rst

   Advanced Mathematics
   ====================

   Matrix equation:

   .. math::

      \\mathbf{A} \\mathbf{x} = \\mathbf{b}

      \\begin{pmatrix}
      a_{11} & a_{12} \\\\
      a_{21} & a_{22}
      \\end{pmatrix}
      \\begin{pmatrix}
      x_1 \\\\ x_2
      \\end{pmatrix}
      =
      \\begin{pmatrix}
      b_1 \\\\ b_2
      \\end{pmatrix}

   Aligned equations:

   .. math::

      \\begin{align}
      f(x) &= x^2 + 2x + 1 \\\\
           &= (x + 1)^2
      \\end{align}

CI/CD Integration
-----------------

GitHub Actions workflow for documentation:

**.github/workflows/docs.yml**:

.. code-block:: yaml

   name: Documentation

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

   jobs:
     build-docs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Setup Python
           uses: actions/setup-python@v5
           with:
             python-version: "3.11"

         - name: Install dependencies
           run: |
             pip install -e .
             pip install sphinx furo sphinx-autodoc-typehints

         - name: Build HTML documentation
           run: |
             cd docs
             sphinx-build -b html source _build/html

         - name: Build PDF documentation
           run: |
             cd docs
             sphinx-build -b typstpdf source _build/pdf

         - name: Upload PDF artifact
           uses: actions/upload-artifact@v4
           with:
             name: documentation-pdf
             path: docs/_build/pdf/*.pdf

Performance Optimization
------------------------

For large documentation projects:

**conf.py**:

.. code-block:: python

   # Parallel build
   import multiprocessing
   parallel_read_safe = True
   parallel_write_safe = True

   # Limit depth for faster builds
   typst_documents = [
       ("index", "output", "Title", "Author", "typst"),
   ]

   # Disable expensive features if not needed
   typst_use_codly = True  # Keep code highlighting
   typst_code_line_numbers = False  # Disable if not needed

See Also
--------

- :doc:`/user_guide/configuration` - All configuration options
- :doc:`/user_guide/templates` - Template system details
- `Typst Documentation <https://typst.app/docs>`_ - Official Typst reference
- `Typst Universe <https://typst.app/universe>`_ - Package repository
