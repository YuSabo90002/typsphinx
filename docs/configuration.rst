=============
Configuration
=============

This document provides a complete reference for all configuration options available in typsphinx.

Overview
========

typsphinx is configured through your Sphinx project's ``conf.py`` file. All configuration values are prefixed with ``typst_`` to avoid conflicts with other extensions.

Quick Start
-----------

Minimal configuration example:

.. code-block:: python

   # conf.py
   extensions = ['sphinxcontrib.typst']

   typst_documents = [
       ('index', 'output.typ', 'My Project', 'Author Name'),
   ]

Configuration Reference
=======================

Document Generation
-------------------

typst_documents
~~~~~~~~~~~~~~~

Defines which documents to build and their metadata.

:Type: ``list`` of tuples
:Default: ``[]``

Each tuple contains:

1. **Source name** (str): Document name without extension (e.g., ``'index'``)
2. **Target name** (str): Output .typ filename (e.g., ``'output.typ'``)
3. **Title** (str): Document title
4. **Author** (str): Document author(s)

**Example:**

.. code-block:: python

   typst_documents = [
       ('index', 'manual.typ', 'User Manual', 'Development Team'),
       ('api', 'api-reference.typ', 'API Reference', 'John Doe'),
   ]

**Notes:**

- If empty, no documents will be built
- Multiple documents can be specified for multi-document projects
- Each document is built independently

Template Configuration
----------------------

typst_template
~~~~~~~~~~~~~~

Path to a custom Typst template file.

:Type: ``str`` or ``None``
:Default: ``None`` (uses built-in template)

**Example:**

.. code-block:: python

   typst_template = '_templates/custom.typ'

**Template Search Order:**

1. Absolute path if provided
2. Relative to project source directory
3. Relative to ``_templates/`` directory
4. Built-in default template

typst_template_mapping
~~~~~~~~~~~~~~~~~~~~~~

Custom mapping between Sphinx metadata and template parameters.

:Type: ``dict`` or ``None``
:Default: ``None`` (uses default mapping)

Allows you to rename template parameters to match your custom template.

**Default Mapping:**

- ``project`` → template parameter ``title``
- ``author`` → template parameter ``authors``
- ``release`` → template parameter ``version``

**Example:**

.. code-block:: python

   typst_template_mapping = {
       'project': 'doc_title',
       'author': 'doc_authors',
       'release': 'doc_version',
   }

This maps Sphinx's ``project`` to your template's ``doc_title`` parameter.

typst_template_function
~~~~~~~~~~~~~~~~~~~~~~~

Name of the template function to call in custom templates.

:Type: ``str`` or ``None``
:Default: ``None`` (auto-detect from template)

**Example:**

.. code-block:: python

   typst_template_function = 'my_template'

In your custom template:

.. code-block:: typst

   #let my_template(title: "", authors: (), body) = {
     // Your template code
   }

Content and Styling
-------------------

typst_elements
~~~~~~~~~~~~~~

Dictionary of Typst-specific styling elements.

:Type: ``dict``
:Default: ``{}``

**Available Options:**

- ``papersize``: Paper size (e.g., ``'a4'``, ``'letter'``)
- ``fontsize``: Base font size (e.g., ``'11pt'``, ``'12pt'``)
- ``mainfont``: Main font family
- ``monofont``: Monospace font for code

**Example:**

.. code-block:: python

   typst_elements = {
       'papersize': 'a4',
       'fontsize': '11pt',
       'mainfont': 'Linux Libertine',
       'monofont': 'Fira Code',
   }

typst_use_mitex
~~~~~~~~~~~~~~~

Enable LaTeX math rendering using mitex package.

:Type: ``bool``
:Default: ``True``

When enabled, LaTeX math expressions are converted using the mitex Typst package, which provides better compatibility with LaTeX syntax.

**Example:**

.. code-block:: python

   typst_use_mitex = True

**Note:** Requires the mitex package. If disabled, basic math conversion will be attempted but with limited LaTeX support.

Table of Contents
-----------------

typst_toctree_defaults
~~~~~~~~~~~~~~~~~~~~~~

Default options for ``toctree`` directives.

:Type: ``dict`` or ``None``
:Default: ``None``

Sets default values for toctree options that can be overridden per-directive.

**Available Options:**

- ``maxdepth``: Maximum depth of toctree (integer)
- ``numbered``: Enable numbering (boolean)
- ``caption``: Default caption text (string)
- ``titlesonly``: Show titles only (boolean)
- ``hidden``: Hide toctree from output (boolean)

**Example:**

.. code-block:: python

   typst_toctree_defaults = {
       'maxdepth': 3,
       'numbered': True,
       'caption': 'Contents',
   }

Typst Packages
--------------

typst_package
~~~~~~~~~~~~~

Specify a Typst Universe package to use.

:Type: ``str`` or ``None``
:Default: ``None``

**Example:**

.. code-block:: python

   typst_package = "@preview/diagraph:0.2.5"

The package will be imported in generated Typst files.

typst_package_imports
~~~~~~~~~~~~~~~~~~~~~

List of custom import statements for Typst packages.

:Type: ``list`` or ``None``
:Default: ``None``

Allows fine-grained control over package imports.

**Example:**

.. code-block:: python

   typst_package_imports = [
       '#import "@preview/diagraph:0.2.5": *',
       '#import "@preview/tablex:0.1.0": tablex, cellx',
   ]

Debug and Development
---------------------

typst_debug
~~~~~~~~~~~

Enable debug mode for detailed logging.

:Type: ``bool``
:Default: ``False``

When enabled, outputs detailed information about the conversion process.

**Example:**

.. code-block:: python

   typst_debug = True

**Alternative:** Set environment variable:

.. code-block:: bash

   export SPHINX_TYPST_DEBUG=1

Complete Example
================

Here's a complete ``conf.py`` example with common settings:

.. code-block:: python

   # conf.py

   # Project information
   project = 'My Project'
   author = 'Development Team'
   release = '1.0.0'

   # General Sphinx configuration
   extensions = [
       'sphinxcontrib.typst',
       'sphinx.ext.autodoc',
       'sphinx.ext.napoleon',
   ]

   # typsphinx configuration

   # Define documents to build
   typst_documents = [
       ('index', 'manual.typ', project, author),
   ]

   # Use custom template
   typst_template = '_templates/custom.typ'

   # Customize styling
   typst_elements = {
       'papersize': 'a4',
       'fontsize': '11pt',
   }

   # Enable LaTeX math support
   typst_use_mitex = True

   # Configure toctree defaults
   typst_toctree_defaults = {
       'maxdepth': 2,
       'numbered': True,
   }

   # Import Typst packages
   typst_package_imports = [
       '#import "@preview/codly:0.1.0": *',
   ]

Building Documents
==================

After configuring your project, build Typst documents using:

.. code-block:: bash

   # Build Typst files only
   sphinx-build -b typst source/ build/typst

   # Build PDF directly (requires typst CLI)
   sphinx-build -b typstpdf source/ build/pdf

Troubleshooting
===============

Common Issues
-------------

Configuration Not Applied
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Changes to ``conf.py`` are not reflected in output.

**Solution:**

- Clear the build directory and rebuild:

  .. code-block:: bash

     rm -rf _build/
     sphinx-build -b typst source/ build/typst

- Use the ``-a`` flag to rebuild all files:

  .. code-block:: bash

     sphinx-build -a -b typst source/ build/typst

Template Not Found
~~~~~~~~~~~~~~~~~~

**Problem:** Custom template file cannot be found.

**Solution:**

- Verify the template path is correct relative to source directory
- Use absolute path if needed:

  .. code-block:: python

     import os
     typst_template = os.path.join(os.path.dirname(__file__), 'templates', 'custom.typ')

Package Import Errors
~~~~~~~~~~~~~~~~~~~~~

**Problem:** Typst package imports fail during compilation.

**Solution:**

- Verify package name and version are correct
- Check Typst Universe for available packages: https://typst.app/universe
- Ensure package syntax is correct:

  .. code-block:: python

     typst_package_imports = [
         '#import "@preview/package:version": *',
     ]

Math Rendering Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem:** LaTeX math expressions not rendering correctly.

**Solution:**

- Ensure ``typst_use_mitex = True`` in ``conf.py``
- Verify the mitex package is available
- For unsupported LaTeX commands, consider using Typst's native math syntax

Debug Mode
----------

Enable debug output to troubleshoot conversion issues:

.. code-block:: python

   # conf.py
   typst_debug = True

Or via environment variable:

.. code-block:: bash

   export SPHINX_TYPST_DEBUG=1
   sphinx-build -b typst source/ build/typst

This provides detailed logging of:

- Document conversion steps
- Template processing
- Node translation
- Configuration values

FAQ
===

Can I use multiple templates?
------------------------------

Currently, one global template is applied to all documents. To use different templates per document, you can:

1. Specify document-specific settings in ``typst_elements``
2. Use conditional logic in your template based on document metadata
3. Generate separate builds with different ``conf.py`` settings

How do I customize the default template?
-----------------------------------------

1. Copy the default template from ``sphinxcontrib/typst/templates/base.typ``
2. Modify it to suit your needs
3. Reference it in ``conf.py``:

   .. code-block:: python

      typst_template = '_templates/my_custom.typ'

Can I use Typst packages from Typst Universe?
----------------------------------------------

Yes! Use the ``typst_package`` or ``typst_package_imports`` configuration:

.. code-block:: python

   typst_package_imports = [
       '#import "@preview/codly:0.1.0": *',
       '#import "@preview/gentle-clues:0.3.0": *',
   ]

Does typsphinx support all Sphinx features?
------------------------------------------------------

typsphinx supports most common Sphinx features including:

- Standard reStructuredText directives
- Code blocks with syntax highlighting
- Cross-references and links
- Tables and figures
- Math equations (via mitex)
- Toctree and document hierarchy

Some advanced features may have limited support. Check the documentation or file an issue for specific features.

See Also
========

- :doc:`installation` - Installation guide
- :doc:`usage` - Usage examples and tutorials
- `Typst Documentation <https://typst.app/docs/>`_ - Official Typst documentation
- `Sphinx Documentation <https://www.sphinx-doc.org/>`_ - Official Sphinx documentation
