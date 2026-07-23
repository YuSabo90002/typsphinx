Configuration
=============

This page documents all configuration options available for typsphinx.

Basic Configuration
-------------------

Add these settings to your ``conf.py`` file:

Project Information
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   project = "My Project"
   copyright = "2025, Author Name"
   author = "Author Name"
   release = "1.0.0"

These are standard Sphinx settings that typsphinx uses for document metadata.

Typst Documents
~~~~~~~~~~~~~~~

Define which documents to build:

.. code-block:: python

   typst_documents = [
       ("index", "output", "Title", "Author", "typst"),
   ]

Each tuple contains:

1. **Source file** (without ``.rst`` extension)
2. **Output filename stem** -- governs both the emitted ``.typ`` file and,
   under the ``typstpdf`` builder, the compiled ``.pdf``. A literal trailing
   ``.typ`` is stripped if present, and nothing else is, so a stem
   containing a period such as ``v1.2-manual`` is preserved intact. A path
   component is not supported: a path-bearing value produces a build
   warning and the file is written under its basename next to the source
   document.
3. **Document title**
4. **Author**
5. **Document class** (usually "typst")

Template Configuration
----------------------

Template Function
~~~~~~~~~~~~~~~~~

Specify the Typst template function:

.. code-block:: python

   # Simple string format
   typst_template_function = "project"

   # Dictionary format with parameters
   typst_template_function = {
       "name": "ieee",
       "params": {
           "abstract": "This paper presents...",
           "index-terms": ["AI", "ML"],
       }
   }

Custom Template File
~~~~~~~~~~~~~~~~~~~~

Use a custom Typst template file:

.. code-block:: python

   typst_template = "_templates/custom.typ"

The template file should define a ``project`` function (or the function
specified in ``typst_template_function``).

Typst Package
~~~~~~~~~~~~~

Use external Typst packages from Typst Universe:

.. code-block:: python

   typst_package = "@preview/charged-ieee:0.1.4"

Template Assets
~~~~~~~~~~~~~~~

Control how template assets (fonts, images, logos) are copied:

.. code-block:: python

   # Default: Automatic directory copy
   typst_template = "_templates/custom.typ"
   # All files in _templates/ are automatically copied

   # Explicit: Specify which assets to copy
   typst_template_assets = [
       "_templates/logo.png",
       "_templates/fonts/",
       "_templates/icons/*.svg"  # Glob patterns supported
   ]

   # Disable: Empty list prevents automatic copying
   typst_template_assets = []

**Default**: ``None`` (automatic directory copy)

**Type**: ``list[str] | None``

When ``typst_template_assets`` is:

- ``None`` (default): Automatically copy entire template directory
- List of paths: Copy only specified files/directories (supports glob patterns)
- Empty list ``[]``: Disable automatic asset copying

.. note::

   This setting only applies to local custom templates (``typst_template``).
   Typst Universe packages (``typst_package``) handle assets automatically.

See :doc:`templates` for detailed examples.

Math Rendering
--------------

mitex Support
~~~~~~~~~~~~~

Enable LaTeX math rendering with mitex:

.. code-block:: python

   typst_use_mitex = True  # Default

When enabled, LaTeX math expressions are converted to Typst using the mitex package.
When disabled, math is passed directly as Typst math syntax.

Code Highlighting
-----------------

Codly Configuration
~~~~~~~~~~~~~~~~~~~

Enable code highlighting with codly:

.. code-block:: python

   typst_use_codly = True  # Default

Customize line numbering:

.. code-block:: python

   typst_code_line_numbers = True  # Show line numbers

Author Information
------------------

Simple Format
~~~~~~~~~~~~~

.. code-block:: python

   typst_author = ("John Doe", "Jane Smith")

Detailed Format
~~~~~~~~~~~~~~~

Include detailed author information:

.. code-block:: python

   typst_authors = {
       "John Doe": {
           "department": "Computer Science",
           "organization": "MIT",
           "email": "john@mit.edu"
       },
       "Jane Smith": {
           "department": "Engineering",
           "organization": "Stanford",
           "email": "jane@stanford.edu"
       }
   }

Paper Size and Format
---------------------

.. code-block:: python

   typst_papersize = "a4"  # Default: "a4"
   # Options: "a4", "us-letter", "a5", etc.

   typst_fontsize = "11pt"  # Default: "11pt"

Complete Example
----------------

Here's a complete ``conf.py`` example:

.. code-block:: python

   # Project information
   project = "My Documentation"
   copyright = "2025, My Name"
   author = "My Name"
   release = "1.0.0"

   # General configuration
   extensions = ["typsphinx"]

   # Typst documents
   typst_documents = [
       ("index", "mydoc", project, author, "typst"),
   ]

   # Template configuration
   typst_package = "@preview/charged-ieee:0.1.4"
   typst_template_function = {
       "name": "ieee",
       "params": {
           "abstract": "This document demonstrates...",
           "index-terms": ["Documentation", "Typst"],
           "paper-size": "us-letter",
       }
   }

   # Author details
   typst_authors = {
       "My Name": {
           "department": "Engineering",
           "organization": "My Organization",
           "email": "me@example.com"
       }
   }

   # Math and code
   typst_use_mitex = True
   typst_use_codly = True
   typst_code_line_numbers = True

See Also
--------

- :doc:`builders` - Understanding the typst and typstpdf builders
- :doc:`templates` - Customizing Typst templates
- :doc:`/examples/advanced` - Advanced configuration examples
