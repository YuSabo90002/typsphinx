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

Setting ``typst_documents`` is optional. When it is absent, typsphinx
derives a single entry from ``root_doc``, ``project``, and ``author``, with
the target stem produced by the same ``make_filename_from_project`` helper
Sphinx's own LaTeX builder uses. An explicitly-set value always wins,
including an explicit empty list, because Sphinx resolves a raw user-set
config value before falling back to a callable default. The derived entry
makes the root document a master, so its emitted ``.typ`` receives the full
template wrapper.

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
3. **Document title** -- the entry's own value is used when present,
   including an empty string, which renders as an empty title: an empty
   string is a *value*, not a signal to fall back. When the element is
   absent or ``None``, typsphinx falls back to ``project``. A non-``str``
   value emits a build warning and then falls back to ``project`` as well.
4. **Author** -- resolved the same way as the title: a present value wins
   (including ``""``); an absent, ``None``, or non-``str`` value falls back
   to ``author``, with a build warning for the non-``str`` case. Whether
   this value also beats ``typst_authors`` is settled at the mapping
   stage by exactly one thing -- whether the active parameter mapping
   sends ``"author"`` to the template parameter named ``authors``, which
   is what the default mapping does.
   `Author Information`_ below states the full rule, including the two
   cases this summary does not cover: a mapping that sends ``"author"``
   to a different parameter, and a mapping that sends a different key to
   ``authors``. ``typst_template_function``'s dict-form ``params`` take
   precedence over *both* -- a user who has named both the template
   function and its arguments has already made a more specific decision
   than either.
5. **Document class** (usually "typst") -- **accepted and ignored**:
   typsphinx reads nothing from this position today, and a five-element
   tuple is valid and behaves identically to a four-element one. Real
   five-element tuples already exist in this repository --
   ``docs/source/conf.py`` and both ``examples/charged-ieee`` configs
   (``approach1`` and ``approach2``) all set one -- so this is not merely
   a hypothetical shape.

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

**Precedence.** Two stages decide what reaches the template's ``authors``
parameter, in this order:

1. **The parameter mapping**, applied while Sphinx metadata is turned into
   template parameters. typsphinx seeds ``authors`` from ``typst_authors``
   first and then applies the mapping, so whatever the mapping writes into
   ``authors`` replaces that seed. No other assignment in that mapping step
   replaces the seed: the defaults typsphinx back-fills for a missing
   parameter only fill a key that is not already set, and ``typst_elements``
   accepts no ``authors`` key at all.
2. **``typst_template_function``'s dict-form** ``params``, applied later,
   when the document is rendered. A ``params["authors"]`` entry there
   replaces whatever stage 1 produced -- including a ``typst_authors`` seed
   that came through stage 1 untouched.

Within stage 1, one question decides the outcome, and it is not about the
template route: **does the active parameter mapping send some Sphinx
metadata key to the template parameter named** ``authors``?

The default mapping sends ``author`` to ``authors``, so on an ordinary
build the entry's own author element (the fourth position in
`Typst Documents`_ above) -- or the ``author`` fallback it resolves to
-- wins.

``typst_authors`` therefore comes through stage 1 as the sole source of
``authors`` if and only if no entry of the active mapping targets
``authors`` with a source key the build actually supplies. It is the
*target* key that decides, not whether ``"author"`` appears in the mapping
at all:

* A mapping that sends ``"author"`` somewhere other than ``authors``
  -- for example ``typst_template_mapping = {"author": "doc_authors"}``,
  for a custom template whose function names its author parameter
  differently -- leaves ``authors`` alone. Stage 1's own output then
  carries both: ``typst_authors`` as ``authors``, and the entry's author
  value as ``doc_authors`` -- subject to stage 2's override above if
  ``typst_template_function`` also sets ``params["authors"]``.
* A mapping that sends some other key to ``authors`` -- for example
  ``typst_template_mapping = {"project": "authors"}`` -- replaces the
  seed even though it never mentions ``"author"``. Stage 1's own output
  for ``authors`` is then the project name, in the same shape an author
  value would take -- again subject to stage 2's override.

A ``typst_package`` build with ``typst_template_mapping`` not set at
all reaches stage 1's surviving case by a side door rather than by a rule
of its own: typsphinx then passes only what was explicitly mapped, and
nothing was, so the mapping is empty and can target nothing.
Package-based and template-based builds -- including the bundled
default template -- are governed by the one stage-1 rule above;
``typst_package`` affects only which mapping is in force, never whether
the mapping replaces the seed.

Coming through stage 1 is not the end of the story. Setting
``typst_template_function`` to its dict form with a ``params["authors"]``
entry replaces the ``typst_authors`` seed at stage 2, so a project that
sets ``typst_authors`` alongside a mapping targeting nothing but ``title``
still renders the template function's own ``authors`` value.

.. note::

   ``typst_authors`` is fully replaceable by ``typst_template_function``'s
   ``params["authors"]`` -- rendering the same author dictionary through
   both routes was measured to produce a byte-identical ``authors:``
   value, differing only in the order of named arguments in the emitted
   call (semantically irrelevant in Typst). ``typst_authors`` is
   **slated for removal** in a future major release; new configurations
   should prefer ``typst_template_function``'s ``params`` instead.

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
   typst_elements = {"lang": "de"}

Here the derived value would be ``ja``, but the explicit entry wins, so
Typst typesets in German and renders 「Tabelle 1」.

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

   # Author details (see "Author Information" above for the precedence
   # rule and the typst_authors forward-removal notice)
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
