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

   # Detailed author information -- moved directly into
   # typst_template_function["params"]["authors"] below. Declaring params
   # makes it the COMPLETE parameter set (see :doc:`/user_guide/configuration`'s
   # Author Information section), so title is also named here explicitly
   # rather than relying on the typst_documents entry's own value.
   ieee_authors = [
       {
           "name": "John Doe",
           "department": "Computer Science",
           "organization": "MIT",
           "email": "john@mit.edu",
       },
   ]

   typst_template_function = {
       "name": "ieee",
       "params": {
           "title": project,
           "authors": ieee_authors,
           "abstract": ieee_abstract,
           "index-terms": ieee_keywords,
           "paper-size": "us-letter",
       }
   }

Custom Template Wrapping
-------------------------

Wrap external packages with custom logic:

**_typst/custom_ieee.typ**:

.. code-block:: typst

   #import "@preview/charged-ieee:0.1.4": ieee

   #let project(
     title: "",
     authors: (),
     date: none,
     toctree_maxdepth: 2,
     toctree_numbered: false,
     toctree_caption: "Contents",
     papersize: "a4",
     fontsize: 11pt,
     lang: "en",
     body
   ) = {
     // Transform simple author tuples to IEEE format
     let ieee_authors = authors.map(name => (
       name: name,
       department: "Engineering",
       organization: "My Organization",
       location: "City, State",
       email: lower(name.split(" ").at(0)) + "@example.com"
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
       bibliography: bibliography("refs.bib"),
     )

     body
   }

**conf.py**:

.. code-block:: python

   typst_template = "_typst/custom_ieee.typ"

.. note::

   ``bibliography`` takes the **result of a call to** Typst's own
   ``bibliography()`` function, not a bare path string -- ``ieee()`` rejects
   a plain ``"refs.bib"`` string with a type error. Place ``refs.bib`` next
   to ``custom_ieee.typ`` in your ``_typst/`` directory: typsphinx copies
   that whole directory -- the template's bundle -- to its own directory
   under the output tree (see :doc:`/user_guide/templates`'s Template
   Assets section), so ``refs.bib`` lands **beside** the template file, not
   at the output root. The relative reference written inside the template
   therefore resolves against that same directory -- reference the asset
   by its bare filename, ``"refs.bib"``, matching where the copy lands.

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

Each entry gets its own wrapper file at the entry's target -- ``main.typ``,
``api-reference.typ`` and ``tutorial.typ`` -- and each is compiled
separately. The wrappers are not the whole story: every document in the
project also gets a content file named after its docname, whether or not it
appears above. See :doc:`/user_guide/output_layout` for the full
wrapper/content contract and which file to compile.

Custom Styling
--------------

Apply custom fonts and colors:

**_typst/styled.typ**:

.. code-block:: typst

   #let project(
     title: "",
     primary-color: "#1e88e5",
     body
   ) = {
     // Set custom font
     set text(
       font: "New Computer Modern",
       size: 11pt,
     )

     // Custom heading style
     show heading.where(level: 1): it => {
       set text(fill: rgb(primary-color), size: 20pt, weight: "bold")
       it
       v(0.5em)
     }

     show heading.where(level: 2): it => {
       set text(fill: rgb(primary-color).lighten(20%), size: 16pt)
       it
       v(0.3em)
     }

     // Title page
     align(center)[
       #text(size: 28pt, fill: rgb(primary-color), weight: "bold")[
         #title
       ]
     ]

     pagebreak()

     body
   }

**conf.py**:

.. code-block:: python

   typst_template = "_typst/styled.typ"

   typst_template_function = {
       "name": "project",
       "params": {
           "title": "My Styled Document",
           "primary-color": "#0066cc",  # Custom blue
       }
   }

Declaring ``params`` makes it the **complete** parameter set (see
:doc:`/user_guide/configuration`'s Author Information section for the full
exclusivity rule), so ``title`` must be named here explicitly -- without it,
the template's own ``title: ""`` default would apply and the styled title
page above would render empty.

.. note::

   ``primary-color`` is declared as a **hex string**, not a raw Typst color
   literal such as ``blue`` or a ``rgb(...)`` call. Every value that reaches
   a template through ``typst_template_function["params"]`` is a Python
   value (``str``/``int``/``float``/``bool``/``list``/``dict``/``None``)
   formatted as the equivalent Typst literal -- a Python ``str`` always
   becomes a quoted Typst string, never a bare identifier or function call.
   The template converts the hex string to a color itself with
   ``rgb(primary-color)``, which Typst's ``rgb()`` constructor accepts
   directly.

Conditional Content
-------------------

Use different templates for different documents:

**conf.py**:

.. code-block:: python

   # Default template for most documents
   typst_template = "_typst/default.typ"

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

   #let project(
     title: "",
     authors: (),
     date: none,
     toctree_maxdepth: 2,
     toctree_numbered: false,
     toctree_caption: "Contents",
     papersize: "a4",
     fontsize: 11pt,
     lang: "en",
     body
   ) = {
     set page(paper: papersize)

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

See Also
--------

- :doc:`/user_guide/configuration` - All configuration options
- :doc:`/user_guide/templates` - Template system details
- `Typst Documentation <https://typst.app/docs>`_ - Official Typst reference
- `Typst Universe <https://typst.app/universe>`_ - Package repository
