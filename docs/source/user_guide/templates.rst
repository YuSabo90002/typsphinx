Templates
=========

Customize the appearance and structure of your Typst output using templates.

Template System Overview
------------------------

typsphinx uses Typst templates to control document layout and styling.
There are three ways to customize templates:

1. **Default template**: Built-in template (no configuration needed)
2. **Configuration-based**: Use ``typst_template_function`` dict format
3. **Custom template file**: Provide your own ``.typ`` template

Default Template
----------------

The default template provides a clean, professional layout:

.. code-block:: python

   # No configuration needed - uses built-in template
   typst_documents = [
       ("index", "output", "Title", "Author", "typst"),
   ]

Features:

- Title page with project name and author
- Table of contents
- Section numbering
- Professional styling

Configuration-Based Templates
------------------------------

Use Typst Universe packages with configuration:

.. code-block:: python

   typst_package = "@preview/charged-ieee:0.1.4"

   typst_template_function = {
       "name": "ieee",
       "params": {
           "abstract": "This paper presents...",
           "index-terms": ["AI", "ML"],
           "paper-size": "us-letter",
       }
   }

A ``typst_package`` configuration **requires** ``typst_template_function`` in its
dictionary form with a ``params`` key: the ``params`` dict becomes the complete set of
named arguments passed to the package function (the same exclusivity rule
`Custom Parameters`_ below documents). Naming only the function -- the plain string
form, or a dict with no ``params`` key -- is **deprecated**: typsphinx cannot
introspect a third-party Typst Universe function's signature, so handing it the
default parameter set a custom template would receive is misuse, not a defect
typsphinx works around in code. A reader who ignores this rule reaches a real Typst
compile failure the first time the build supplies an argument the package function
never declared -- for example ``unexpected argument: toctree_maxdepth`` once the
master document has a toctree, or ``unexpected argument: papersize`` once
``typst_elements`` sets one.

Advantages:

- No custom files needed
- Declarative configuration
- Easy to maintain

See :doc:`/examples/advanced` for complete examples.

Custom Template Files
---------------------

For full control, create a custom template file.

Template Assets
~~~~~~~~~~~~~~~

When using custom templates, you often need additional assets like fonts, logos, or images. typsphinx automatically copies these assets to the output directory.

**Automatic Asset Copying (Default)**

By default, all files in your template directory are automatically copied (except ``.typ`` files):

.. code-block:: python

   # conf.py
   typst_template = "_templates/custom.typ"
   # All files in _templates/ are automatically copied

Directory structure:

.. code-block:: text

   _templates/
     ├── custom.typ          # Template file
     ├── logo.png            # Automatically copied
     ├── fonts/
     │   └── custom.otf      # Automatically copied
     └── icons/
         └── icon.svg        # Automatically copied

Reference assets in your template using relative paths:

.. code-block:: typst

   // _templates/custom.typ
   #image("logo.png")
   #set text(font: "fonts/custom.otf")
   #image("icons/icon.svg")

**Explicit Asset Specification**

For more control, explicitly specify which assets to copy:

.. code-block:: python

   # conf.py
   typst_template = "_templates/custom.typ"
   typst_template_assets = [
       "_templates/logo.png",
       "_templates/fonts/",
       "_templates/icons/*.svg"
   ]

Features:

- Individual files: ``"_templates/logo.png"``
- Directories: ``"_templates/fonts/"``
- Glob patterns: ``"_templates/icons/*.svg"``

**Disabling Automatic Copying**

To disable automatic asset copying (for performance):

.. code-block:: python

   # conf.py
   typst_template = "_templates/custom.typ"
   typst_template_assets = []  # Empty list = no automatic copying

.. note::

   Typst Universe packages (``typst_package``) handle assets automatically.
   Asset copying only applies to custom local templates (``typst_template``).

Basic Structure
~~~~~~~~~~~~~~~

Create a file ``_templates/custom.typ``:

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
     // Title page
     align(center)[
       #text(size: 24pt, weight: "bold")[#title]
       #v(1em)
       #text(size: 14pt)[#authors.join(", ")]
       #if date != none {
         v(1em)
         text(size: 12pt)[#date]
       }
     ]

     pagebreak()

     // Table of contents
     outline(title: "Contents", indent: auto)

     pagebreak()

     // Document body
     body
   }

Configuration
~~~~~~~~~~~~~

Reference your custom template in ``conf.py``:

.. code-block:: python

   typst_template = "_templates/custom.typ"

Template Parameters
-------------------

Standard Parameters
~~~~~~~~~~~~~~~~~~~

When ``typst_template_function["params"]`` is **not** declared (see `Custom
Parameters`_ below for what changes once it is), your template function receives up
to nine named parameters plus a trailing positional ``body``, each under its own
emission condition:

- ``title`` -- the document title (from ``typst_documents``, or Sphinx's ``project``).
  Arrives unconditionally on every non-package route -- the bundled default, an
  explicit ``typst_template``, and a ``<srcdir>/_typst/base.typ`` shadow alike.
- ``authors`` -- always a Typst **array**, never a bare string. A string source
  (Sphinx's ``author``, or the entry's own author element) is split on commas: a
  single name becomes a one-element array, and ``"Alice Smith, Bob Jones"`` becomes a
  two-element array. Arrives unconditionally, on the same routes as ``title``.
- ``date`` -- the document date (Sphinx's ``release``). Arrives unconditionally, on
  the same routes as ``title``.
- ``papersize`` -- only when ``papersize`` is set in ``typst_elements``.
- ``fontsize`` -- only when ``fontsize`` is set in ``typst_elements``.
- ``lang`` -- on every non-package route, auto-derived from Sphinx's own ``language``
  setting; an explicit ``typst_elements["lang"]`` value always wins over the derived
  one. See :doc:`configuration` for the full derivation rule (Document Language
  section).
- ``toctree_maxdepth``, ``toctree_numbered``, ``toctree_caption`` -- only when the
  master document's own toctree is present. A master with no toctree receives none of
  these three.

A master document with **no toctree and no** ``typst_elements`` therefore receives
only the unconditional subset: ``title``, ``authors``, ``date``, and ``lang``, plus
the trailing positional ``body`` -- four named parameters, not nine. The bundled
default template (``typsphinx/templates/base.typ``) declares all nine plus ``body``,
with a default for every parameter that may be absent, which is why it works
regardless of which conditional parameters a given build supplies. A custom template
should do the same if it needs to work across every document a project builds, or
declare only the subset it knows it will always receive.

.. important::

   Adding a template parameter is a **breaking change** for a correctly-written
   custom template. Typst rejects a named argument a function never declared, so the
   day typsphinx passes a tenth parameter, every existing custom template that
   declares exactly today's nine stops compiling. This is what makes the next
   parameter addition a deliberate decision, not a routine one.

On the ``typst_package`` route with no ``params`` declared, the picture is different
again: ``title``/``authors``/``date`` are **not** back-filled -- a third-party Typst
Universe function's own signature decides what it accepts -- and ``lang`` is withheld
for the same reason. See `Configuration-Based Templates`_ above.

Custom Parameters
~~~~~~~~~~~~~~~~~

Add custom parameters using ``typst_template_function``:

.. code-block:: python

   typst_template_function = {
       "name": "project",  # Your template function name
       "params": {
           "subtitle": "A Technical Report",
           "version": "1.0",
           "confidential": True,
       }
   }

Access in template:

.. code-block:: typst

   #let project(
     title: "",
     subtitle: none,
     version: none,
     confidential: false,
     body
   ) = {
     // Use custom parameters
     if confidential {
       text(fill: red)[CONFIDENTIAL]
     }
     // ...
   }

Once ``params`` is declared -- even naming a single key -- it is the **complete**
parameter set: none of ``title``/``authors``/``date``, ``papersize``/``fontsize``/
``lang``, or the ``toctree_*`` keys arrive unless the ``params`` dict names them
itself. This example's ``params`` dict names only ``subtitle``, ``version`` and
``confidential``, so exactly those three named parameters reach the template above --
its ``title`` parameter keeps its own default (``""``) because nothing ever passes it
a value. See :doc:`configuration`'s precedence section for the full exclusivity rule.

Wrapping External Packages
---------------------------

You can wrap Typst Universe packages in custom templates:

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
     // Transform parameters
     let ieee_authors = authors.map(name => (
       name: name,
       department: "Engineering",
       organization: "My Org",
     ))

     // Apply IEEE template
     show: ieee.with(
       title: title,
       authors: ieee_authors,
     )

     body
   }

This approach gives you:

- Parameter transformation
- Custom preprocessing
- Multiple package integration

Examples
--------

Minimal Template
~~~~~~~~~~~~~~~~

This template declares only ``title`` -- one parameter short of the unconditional
subset -- so it needs a ``params`` dict naming exactly that key; without one, the
auto-derived ``authors``/``date`` (and ``lang``, and any toctree/``typst_elements``
keys the build supplies) would arrive as undeclared arguments and abort the compile.

.. code-block:: python

   # conf.py
   typst_template = "_templates/minimal.typ"
   typst_template_function = {
       "name": "project",
       "params": {
           "title": "Minimal Report",
       }
   }

.. code-block:: typst

   #let project(title: "", body) = {
     set page(paper: "a4", margin: 2.5cm)
     set text(font: "New Computer Modern", size: 11pt)

     align(center)[#text(20pt, weight: "bold")[#title]]
     v(2em)

     body
   }

Academic Paper Template
~~~~~~~~~~~~~~~~~~~~~~~

This template declares four parameters -- ``title``, ``authors``, ``abstract`` and
``keywords`` -- none of which is the auto-derived default set on its own, so it needs
a ``params`` dict naming all four.

.. code-block:: python

   # conf.py
   typst_template = "_templates/academic.typ"
   typst_template_function = {
       "name": "project",
       "params": {
           "title": "A Study of Typst Templates",
           "authors": ("Alice Smith", "Bob Jones"),
           "abstract": "This paper examines custom template parameter contracts.",
           "keywords": ("Typst", "Sphinx", "Templates"),
       }
   }

.. code-block:: typst

   #let project(
     title: "",
     authors: (),
     abstract: none,
     keywords: (),
     body
   ) = {
     // Two-column layout
     set page(
       paper: "us-letter",
       columns: 2,
       margin: (x: 2cm, y: 2.5cm),
     )

     // Title and authors in single column
     place(top + center, float: true)[
       #text(18pt, weight: "bold")[#title]
       #v(0.5em)
       #text(12pt)[#authors.join(", ")]
     ]

     // Abstract box
     if abstract != none {
       place(top + center, float: true, clearance: 3em)[
         #box(width: 100%, inset: 1em)[
           *Abstract:* #abstract
         ]
       ]
     }

     // Keywords
     if keywords.len() > 0 {
       place(top + center, float: true, clearance: 6em)[
         *Keywords:* #keywords.join(", ")
       ]
     }

     v(8em)

     // Two-column body
     body
   }

Best Practices
--------------

1. **Start simple**: Use the default template or configuration-based approach first
2. **Reuse packages**: Leverage Typst Universe packages when possible
3. **Test incrementally**: Build frequently to catch errors early
4. **Document parameters**: Comment your template parameters clearly
5. **Keep it maintainable**: Don't over-complicate templates

Debugging Templates
-------------------

If you encounter errors:

1. **Check syntax**: Typst errors are reported in build output
2. **Test standalone**: Compile your template with test data
3. **Use typst builder**: Generate ``.typ`` files to inspect output
4. **Simplify**: Remove customizations until it works

.. code-block:: bash

   # Generate .typ files for inspection
   sphinx-build -b typst source/ build/typst

   # Check the template usage in the wrapper -- with typst_documents
   # unset, project = "My Project" produces the wrapper myproject.typ
   cat build/typst/myproject.typ

The docname-named content file (``index.typ`` in this example) holds the
body only and carries no template application at all, so a template
problem is always visible in the wrapper -- see :doc:`output_layout` for
the full wrapper/content contract.

See Also
--------

- :doc:`output_layout` - The wrapper/content output contract
- :doc:`configuration` - Template configuration options
- :doc:`/examples/advanced` - Advanced template examples
- `Typst Documentation <https://typst.app/docs>`_ - Official Typst docs
- `Typst Universe <https://typst.app/universe>`_ - Template packages
