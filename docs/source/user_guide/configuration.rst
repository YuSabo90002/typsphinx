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
2. **Wrapper output target** -- names the entry's **wrapper** file only; it
   does not govern the entry's content file, which is written separately
   under the entry's own source docname. A literal trailing ``.typ`` is
   stripped if present, and nothing else is, so a stem containing a period
   such as ``v1.2-manual`` is preserved intact. A path in the target is
   honoured relative to the output directory: a target of
   ``"manuals/guide.typ"`` writes the wrapper to ``manuals/guide.typ``
   under the output directory. Three shapes are still refused, each with a
   build warning and a basename fallback written at the output root
   instead: a target with a ``..`` path segment, an absolute target, and a
   drive-qualified target -- the drive-qualified check is a pure
   string-shape test, so a Windows-shaped target (``"C:manual"``) is
   refused identically on every platform. See :doc:`output_layout` for
   worked examples of both the honoured-path and the refused shapes.
3. **Document title** -- the entry's own value is used when present,
   including an empty string, which renders as an empty title: an empty
   string is a *value*, not a signal to fall back. When the element is
   absent or ``None``, typsphinx falls back to ``project``. A non-``str``
   value emits a build warning and then falls back to ``project`` as well.
4. **Author** -- resolved the same way as the title: a present value wins
   (including ``""``); an absent, ``None``, or non-``str`` value falls back
   to ``author``, with a build warning for the non-``str`` case. Whether
   this resolved value reaches the template's ``authors`` parameter is
   settled by whether the active parameter mapping sends ``"author"`` to
   the template parameter named ``authors``, which is what the default
   mapping does. `Author Information`_ below states the full mapping rule,
   including the two cases this summary does not cover: a mapping that
   sends ``"author"`` to a different parameter, and a mapping that sends a
   different key to ``authors``. That mapping-stage outcome is itself
   subordinate to whether ``typst_template_function``'s dict-form
   ``params`` is declared at all -- a user who has named both the template
   function and its arguments has already made a more specific decision
   than either, and when ``params`` is present it is the *complete*
   parameter set, discarding whatever the mapping stage produced.
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

   typst_template = "_typst/custom.typ"

The template file should define a ``project`` function (or the function
specified in ``typst_template_function``).

Typst Package
~~~~~~~~~~~~~

Use external Typst packages from Typst Universe:

.. code-block:: python

   typst_package = "@preview/charged-ieee:0.1.4"

Template Assets
~~~~~~~~~~~~~~~

Every used template's bundle directory (the resolved template file's own
parent directory) is copied wholesale to the output tree automatically --
fonts, images, logos, and any other file alongside the template file all
reach the output with no configuration needed.

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

Detailed Author Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Rich per-author structure -- department, organization, location, email -- is
expressed through ``typst_template_function``'s dict-form ``params`` route,
the same route used for any other custom parameter:

.. code-block:: python

   ieee_authors = [
       {
           "name": "John Doe",
           "department": "Computer Science",
           "organization": "MIT",
           "email": "john@mit.edu",
       },
       {
           "name": "Jane Smith",
           "department": "Engineering",
           "organization": "Stanford",
           "email": "jane@stanford.edu",
       },
   ]

   typst_template_function = {
       "name": "project",
       "params": {
           "authors": ieee_authors,
       }
   }

**Precedence.** One question decides the parameter set your template
function receives: **is a** ``params`` **key present in**
``typst_template_function``'s dictionary form?

If it is, ``params`` is the **complete, exclusive** parameter set, on
every route (``typst_template``, ``typst_package``, and the bundled
default alike): the auto-derived ``title``/``authors``/``date``, the
``typst_elements`` allowlist merge, and the three ``toctree_*`` keys are
all discarded wholesale, not merged key-by-key. An explicitly empty
``params: {}`` passes **nothing at all** -- the predicate is the presence
of the ``params`` key, not the truthiness of the dict it holds, so a
zero-named-parameter custom template (``#let project(body) = {...}``) is a
legitimate configuration.

A user who has named both the template function and its arguments has
already made a more specific decision than either -- that sentence
described the *intent* here before this rule was implemented; it is now
literally what the code does, with no residual merge behind it.

If ``params`` is **not** present, the parameter mapping decides what
reaches ``authors`` instead: **does the active parameter mapping send
some Sphinx metadata key to the template parameter named** ``authors``?
The default mapping sends ``author`` to ``authors``, so on an ordinary
build the entry's own author element (the fourth position in
`Typst Documents`_ above) -- or the ``author`` fallback it resolves to --
reaches the template, converted to a Typst array (:doc:`templates`'s
Standard Parameters section states the array shape and the comma-split
rule). It is the *target* key that decides, not whether ``"author"``
appears in the mapping at all:

* A mapping that sends ``"author"`` somewhere other than ``authors`` --
  for example ``typst_template_mapping = {"author": "doc_authors"}``, for
  a custom template whose function names its author parameter
  differently -- leaves ``authors`` unset by the mapping stage; the
  non-package back-fill then supplies an empty array instead.
* A mapping that sends some other key to ``authors`` -- for example
  ``typst_template_mapping = {"project": "authors"}`` -- writes
  ``authors`` from that key instead, in the same array shape an author
  value would take.

A ``typst_package`` build with ``typst_template_mapping`` not set at all
reaches this same case by a side door rather than by a rule of its own:
typsphinx passes only what was explicitly mapped, and nothing was, so the
mapping is empty and can target nothing -- and the ``title``/``authors``/
``date`` back-fill that would otherwise supply a default is itself
withheld on the package route (see :doc:`templates`'s Configuration-Based
Templates section).

.. warning::

   A **partial** migration to the ``params`` route is a silent trap.
   Declaring ``params`` with only one key -- for example
   ``params: {"authors": [...]}`` -- to add rich author structure while
   expecting ``title`` and ``date`` to keep arriving from the auto-derived
   set does **not** work: declaring ``params`` at all replaces the entire
   set. The build does not error -- it renders with the template's own
   defaults, typically an empty title and no author, because every
   parameter ``params`` does not name is simply absent and Typst applies
   the function's own default for an absent named argument. If you want
   one extra parameter beyond the auto-derived set, declare the **full**
   set you need inside ``params``; there is no partial-override
   mechanism.

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

On every non-package template route, ``lang`` is derived automatically
from Sphinx's own ``language`` setting -- no explicit configuration is
needed. The derivation rule is simple: take the part of the value before
the first underscore, hyphen, or at-sign, and lowercase it. For example:

- ``ja`` becomes ``ja``
- ``zh_CN`` becomes ``zh``
- ``pt_BR`` becomes ``pt``

If a ``language`` value cannot be reduced to a two- or three-letter code,
typsphinx emits a build warning naming the value and leaves the parameter
unset, so the template's own default applies and the build still
succeeds.

Scope: every non-package route
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic derivation applies on every route **except** ``typst_package``:
the bundled default template, an explicit ``typst_template``, and a
``<srcdir>/_typst/base.typ`` shadow of the bundled template all receive the
auto-derived ``lang`` argument unconditionally. It is withheld only when
``typst_package`` is configured, because typsphinx never introspects a
third-party Typst Universe function's signature and would otherwise hand
it an argument it never declared.

This means declaring a ``lang`` parameter in a custom template is not an
opt-in -- on every non-package route it is **mandatory**: an existing
custom template that omits it fails to compile with a Typst
``unexpected argument: lang`` abort the next time it is built. See
:doc:`templates`'s nine-parameter contract for the full parameter list.

If you use ``typst_package`` and want the same behavior, opt in
explicitly: declare a ``lang`` parameter in your own wrapping template
and then set it through ``typst_elements``, as shown below.

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

   # Template configuration -- typst_package requires typst_template_function
   # with a params key (see "Configuration-Based Templates" in :doc:`templates`).
   # Declaring params makes it the COMPLETE parameter set (see "Author
   # Information" above), so title/authors are named here explicitly rather
   # than relying on the typst_documents entry's own values.
   typst_package = "@preview/charged-ieee:0.1.4"
   typst_template_function = {
       "name": "ieee",
       "params": {
           "title": project,
           "authors": [
               {
                   "name": author,
                   "department": "Engineering",
                   "organization": "My Organization",
                   "email": "me@example.com",
               },
           ],
           "abstract": "This document demonstrates...",
           "index-terms": ["Documentation", "Typst"],
           "paper-size": "us-letter",
       }
   }

   # Math
   typst_use_mitex = True

   # Paper size and base font size
   typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}

See Also
--------

- :doc:`output_layout` - The wrapper/content output contract
- :doc:`builders` - Understanding the typst and typstpdf builders
- :doc:`templates` - Customizing Typst templates
- :doc:`/examples/advanced` - Advanced configuration examples
