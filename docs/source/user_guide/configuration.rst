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
5. **Document registry key** -- the registry key into
   ``typst_document_templates`` that this entry's wrapper resolves its
   template, package, and template function through. An absent
   element [4] resolves to the reserved ``"typst"`` registry key, which
   typsphinx synthesizes on every build from the global
   ``typst_template`` / ``typst_package`` / ``typst_template_function``
   settings -- so a four-element entry and a five-element entry naming
   ``"typst"`` behave identically. The lookup is exact string equality
   and is never case-folded: a registry declaring ``"Paper"`` does not
   satisfy an entry naming ``"paper"``. See `Per-Document Templates`_
   below for the registry itself, including what happens when a named
   key is not registered. Real five-element tuples already exist in this
   repository -- ``docs/source/conf.py`` and both ``examples/charged-ieee``
   configs (``approach1`` and ``approach2``) all set one -- so this is not
   merely a hypothetical shape.

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

The template's own directory must not also be named in Sphinx's own
``templates_path`` -- since the whole bundle directory is copied to the
output, doing so would republish the project's Sphinx template directory
in the build output. This repository uses ``_typst/`` for exactly that
reason.

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

Per-Document Templates
~~~~~~~~~~~~~~~~~~~~~~

Every ``typst_documents`` entry's registry key (element [4], or the
reserved ``"typst"`` key when the element is absent) selects a
definition from ``typst_document_templates`` -- the dict mapping a
registry key to its own ``template``, ``package``, and
``template_function`` settings, so each master document can use a
different Typst template, Typst Universe package, or template-function
arguments instead of one globally-configured template being applied to
every master.

Setting ``typst_document_templates`` is entirely additive: a ``conf.py``
that never sets it behaves exactly as before, using only the synthesized
reserved key.

**Definition schema.** A definition is a dict carrying ``template``
exclusively or ``package`` -- setting both is refused (CONF-15) -- plus
an optional ``template_function``, taking the same string form or
dict-with-``params`` form the `Template Function`_ subsection above
already documents. The reserved key ``typst`` itself may not be declared
in ``typst_document_templates`` (CONF-16), because typsphinx owns it.

**Worked example.** ``typst_document_templates`` declaring one key on the
``template`` route, and a ``typst_documents`` list with two entries --
one resolving to the reserved key, one naming the declared key:

.. code-block:: python

   typst_document_templates = {
       "report": {
           "template": "_typst/report.typ",
       },
   }

   typst_documents = [
       ("index", "manual", "Manual", "Author Name"),
       ("summary", "report", "Report", "Author Name", "report"),
   ]

The first entry has no element [4], so its wrapper resolves through the
synthesized reserved ``typst`` key -- using whatever ``typst_template`` /
``typst_package`` / ``typst_template_function`` are globally configured.
The second entry's element [4] names ``report``, so its wrapper instead
uses ``report``'s own ``_typst/report.typ`` template, independent of the
global settings. This is the only place the published documentation shows
a non-default registry key.

**Package route.** A definition may use ``package`` instead of
``template``:

.. code-block:: python

   typst_document_templates = {
       "ieee": {
           "package": "<typst-universe-package-spec>",
       },
   }

The wrapper for a key using ``package`` imports the Typst Universe
package directly, matching the shape shown in `Typst Package`_ above --
and no bundle is copied for that key.

**Which bundles reach the output.** Every key some ``typst_documents``
entry actually names has its bundle -- the resolved template file's own
parent directory -- copied wholesale to the output tree; a key that is
declared but that no entry names is still validated, but its bundle is
not copied. See :doc:`output_layout` for where the copies land. Nothing
under the output directory is ever deleted, so a file removed from a
source bundle can linger at the destination across an incremental
rebuild.

**Empty registry.** An empty ``typst_document_templates`` dict is
accepted, and leaves only the synthesized reserved key -- the same state
as not setting the value at all.

Registry Key Naming Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^

A registry key becomes a directory name under the output tree's reserved
``_template/`` directory, so it must be a single, portable path segment.
The seven shapes below are refused, in the order they are checked:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Rejected key shape
     - Why
   * - Empty or whitespace-only
     - A key becomes a directory name, so it must contain at least one
       non-whitespace character.
   * - Exactly ``.`` or ``..``
     - These are reserved by every filesystem for the current and parent
       directory.
   * - Contains a path separator (``/`` or ``\``)
     - A registry key is a single path segment; a separator would split
       it into more than one.
   * - A Windows reserved device name, matched case-insensitively
       against everything before the first ``.`` -- ``CON.txt`` is
       reserved, ``ICONIC`` is not
     - Some of these names cannot be created as an ordinary file or
       directory on Windows.
   * - Ends with a trailing dot
     - Windows silently strips a trailing dot from a directory name, so
       the written directory would not match the declared key.
   * - Ends with a trailing space
     - Windows silently strips a trailing space from a directory name,
       for the same reason.
   * - Differs from another declared key only by case
     - Two keys that fold to the same directory name would collide when
       their bundles are copied to the output tree.

The case comparison in the last row folds ``/``/``\`` separators,
normalizes path shape, then applies Python's ``casefold()`` -- and
applies no Unicode normalization at all, so the composed (NFC) and
decomposed (NFD) spellings of one accented character are two DIFFERENT
keys, on every platform, with no ``sys.platform`` branch.

A declared key that folds onto the reserved ``typst`` key the same way is
also refused, before any file is written -- reported by the
``pre-write template path failure(s):`` shape below, not by this
key-shape check itself, since the comparison there is against the
synthesized built-in key rather than another declared key.

The ``typst_documents`` element [4] lookup itself, in contrast, is exact
``str`` equality and is never case-folded, so a key must be spelled in an
entry exactly as it was declared.

When the Build Stops
^^^^^^^^^^^^^^^^^^^^^

A misconfigured registry or an unwritable template bundle stops the
build with an ``ExtensionError``. The table below identifies each
config-caused shape by the leading clause of the message it raises;
column three names what to change.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - What went wrong
     - What the build says
     - What to change
   * - ``typst_document_templates`` is set to a truthy value that is
       not a dict
     - ``typst_document_templates must be a dict mapping registry key to definition,``
     - Set ``typst_document_templates`` to a dict mapping each registry
       key to its own definition.
   * - One or more registry definitions are invalid -- this single
       shape aggregates every per-definition failure into one message:
       a non-``str`` key, a rejected key shape, a reserved-key
       redeclaration (CONF-16), a non-``dict`` definition, a definition
       setting both ``template`` and ``package`` (CONF-15), a
       ``template`` value that is neither a path string nor
       ``os.PathLike``, a CONF-17 source-tree bundle, or a template
       file that does not exist
     - ``invalid definition(s):``
     - See `Registry Key Naming Rules`_ for the key-shape cases; for
       the others, correct the named definition's ``template`` or
       ``package`` value.
   * - A ``typst_documents`` entry's element [4] is set to a
       non-string value
     - ``which is not a string -- registered typst_document_templates keys:``
     - Set element [4] to a string naming one of the registered keys
       the message lists.
   * - A ``typst_documents`` entry names a registry key that was
       never declared in ``typst_document_templates``
     - ``which is not a registered typst_document_templates key -- registered keys:``
     - Either declare the named key in ``typst_document_templates`` or
       point element [4] at one of the registered keys the message
       lists.
   * - Two things claim the same output path, including the reserved
       template-bundle directory
     - ``output path collision(s):``
     - Rename one of the colliding wrapper targets, or move a
       definition out of the reserved bundle directory.
   * - A used registry key's template path fails validation before
       anything is written -- covers both a CONF-17 source-tree
       bundle and a collision with Sphinx's own ``templates_path``
     - ``pre-write template path failure(s):`` -- the CONF-17 sub-case
       specifically also reports ``put the template in its own subdirectory (CONF-17, A-01)``
     - Move the template out of ``srcdir`` (or an ancestor of it) and
       out of any directory named in Sphinx's ``templates_path`` --
       this repository uses ``_typst/``.
   * - Two used registry keys resolve to the same bundle destination
     - ``bundle destination collision(s):``
     - Give the colliding keys' definitions distinct template paths so
       their bundles do not land at the same ``_template/<key>/``
       destination.

.. note::

   The two remaining shapes report a filesystem failure at copy time,
   not a ``conf.py`` mistake.
   ``typst_document_templates: failed to copy the resolved template for registry key``
   means the source template file could not be read, or the
   destination could not be written.
   ``was never copied from`` means the resolved template file was
   expected inside its own bundle directory but never arrived there,
   so a wrapper naming this key would import a file that does not
   exist.
   Neither names a ``suppress_warnings`` route, because neither is a
   warning -- both abort the build.

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
