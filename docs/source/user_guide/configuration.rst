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

Author Information
------------------

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

   typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}

``papersize`` and ``fontsize`` set the paper size and the base font size.
``typst_elements`` supports three keys in total; the third, ``lang``, is
documented in `Document Language`_ below.

Document Language
------------------

The ``lang`` key controls the language Typst uses when generating its own
labels -- most notably the figure and table supplement text (for example
"Figure" / "Table" in English). It is passed through to the template's
``project()`` function and reaches Typst's text setup. The effect is
concrete: with a Japanese setting, a captioned table renders as
「表 1」 and a figure as 「図 1」, where the default English setting
renders "Table 1" and "Figure 1".

Automatic derivation
~~~~~~~~~~~~~~~~~~~~~

When your project uses the bundled default template, ``lang`` is derived
automatically from Sphinx's own ``language`` setting -- no explicit
configuration is needed. The derivation rule is simple: take the part of
the value before the first underscore, hyphen, or at-sign, and lowercase
it. For example:

- ``ja`` becomes ``ja``
- ``zh_CN`` becomes ``zh``
- ``pt_BR`` becomes ``pt``

If a ``language`` value cannot be reduced to a two- or three-letter code,
typsphinx emits a build warning naming the value and leaves the parameter
unset, so the template's own default applies and the build still
succeeds.

Scope: default template only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic derivation applies **only** when the bundled default template is
what actually gets used. It does **not** apply when ``typst_template`` is
configured, when ``typst_package`` is configured, or when a file named
``base.typ`` sits next to your ``conf.py`` in the source directory (which
silently shadows the bundled template). The reason: a template that does
not declare a ``lang`` parameter would receive an argument it never asked
for, and Typst aborts the compile on an undeclared argument.

If you use a custom template or package and want the same behavior, opt in
explicitly: declare a ``lang`` parameter in your own ``project()`` (or
equivalent entry function) and then set it through ``typst_elements``, as
shown below.

Precedence and known limitation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An explicit ``typst_elements`` ``lang`` entry always wins over the value
derived from ``language``, on every template path, and an explicit value
is passed through to Typst exactly as written with no validation.

.. code-block:: python

   language = "ja"

.. code-block:: python

   typst_elements = {"lang": "ja"}

**Known limitation:** region subtags are not supported, so a ``zh_TW``
project resolves to ``zh`` and renders simplified-Chinese supplement text
「图 1」 rather than the traditional 「圖 1」. If you need traditional
Chinese, set the value explicitly through your own template.

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

   # Math
   typst_use_mitex = True

   # Paper size and base font size
   typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}

See Also
--------

- :doc:`builders` - Understanding the typst and typstpdf builders
- :doc:`templates` - Customizing Typst templates
- :doc:`/examples/advanced` - Advanced configuration examples
