Diagrams
========

typsphinx renders Graphviz DOT diagrams straight into Typst and PDF output, so a
diagram written once in your documentation appears as a real vector drawing in the
generated PDF.

.. graphviz::
   :caption: Thessomantic dogfood pipeline

   digraph dogfood {
       "Vorthaneglim" -> "Pellucidrane";
   }

That diagram is part of this very page, and it is rendered by the same code path
your own documents use -- building this documentation to PDF is how the feature is
kept honest.

What Is Supported
-----------------

The three Graphviz directives Sphinx ships -- ``.. graphviz::``,
``.. digraph::`` and ``.. graph::`` -- all render as real vector diagrams in
Typst and PDF output, provided the DOT source is written **inline** in the
directive body.

No Graphviz Installation Is Needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rendering goes through the Typst ``@preview/diagraph`` package, which carries
Graphviz itself compiled to WebAssembly. **No system Graphviz installation and no
``dot`` binary are needed for Typst or PDF output.** That is typsphinx's defining
guarantee for diagrams: the Typst and PDF builders draw your graphs on a machine
that has never had Graphviz installed, and the package is fetched and cached by
Typst like any other ``@preview`` dependency.

Captions and References
~~~~~~~~~~~~~~~~~~~~~~~

``:caption:`` renders as a Typst figure caption, and ``:name:`` gives the figure a
resolvable anchor, so ``:ref:`` and ``:numref:`` can point at it from anywhere in
the project. Note that ``:numref:`` resolves to an actual figure *number* only when
``numfig = True`` is set in your ``conf.py``; with numfig left at its default,
Sphinx warns that numbering is disabled and no number is produced.

.. code-block:: rst

   .. graphviz::
      :caption: Request lifecycle
      :name: request-lifecycle

      digraph lifecycle {
          "accept" -> "route" -> "respond";
      }

Layout Engine
~~~~~~~~~~~~~

``:layout:`` selects the Graphviz layout engine, and reaches diagraph's ``engine:``
parameter directly. Sphinx's older spelling ``:graphviz_dot:`` is accepted as an
alias for the same option. ``neato`` is the engine exercised end to end by the
test suite, and the others Graphviz provides are available on the same route.

Engine strings are passed through **unvalidated**. A misspelled engine name
produces no Sphinx-side warning at all; it surfaces later as a Typst compile error
when the document is built, so check the spelling if a PDF build fails on a
diagram that looks correct.

Alternative Text
~~~~~~~~~~~~~~~~

``:alt:`` reaches diagraph's ``alt:`` parameter, so the alternative text you write
for the HTML side is carried into the Typst output too.

What Is Not Supported
---------------------

Each of the exclusions below is deliberate, not an oversight.

``:align:`` Is Discarded
~~~~~~~~~~~~~~~~~~~~~~~~

``:align:`` is discarded silently, with no warning. This matches the project-wide
state of alignment in typsphinx: alignment options are not carried into Typst
output for any node type, and diagrams are not treated as a special case.

External ``.dot`` Files
~~~~~~~~~~~~~~~~~~~~~~~

Only the inline form renders. Pointing the directive at a file on disk --
``.. graphviz:: path/to/file.dot`` -- is **not supported**: the diagram falls back
to a bordered placeholder in the output and the build emits exactly one warning
explaining that only inline DOT is supported. If you keep your graphs in separate
``.dot`` files today, paste the DOT into the directive body to have it rendered.

``.. inheritance-diagram::``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``.. inheritance-diagram::`` is **not** routed through diagraph. It still degrades
to a bordered placeholder, with its own single warning, exactly as it did before
diagram rendering was added.

Malformed DOT Fails the Build
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the DOT source is syntactically broken, typsphinx's own translation stays
clean -- it writes the diagram out with no warning -- but the downstream Typst
compile **hard-fails**, carrying Graphviz's own diagnostic, for example::

   Diagraph error: syntax error in line 2 near ';'

So a syntactically broken diagram currently fails the whole PDF build rather than
degrading to an error block inside the page. That is the honest current behaviour;
the intended handling of this case is still an open decision. Until it changes,
treat a Typst compile failure mentioning ``Diagraph error`` as a DOT syntax error
in your own source, at the line the diagnostic names.

HTML Output
-----------

HTML output remains ``sphinx.ext.graphviz``'s responsibility, and the HTML side
**does** require a real ``dot`` binary on the build machine. ``sphinx.ext.graphviz``
must therefore be present in your ``extensions`` list for the directives to be
recognised at all:

.. code-block:: python

   extensions = [
       "typsphinx",
       "sphinx.ext.graphviz",
   ]

On a machine without Graphviz installed, the HTML build logs::

   dot command 'dot' cannot be run (needed for graphviz output)

and the diagram is missing from the HTML pages, while the Typst and PDF build of
the very same sources is unaffected and renders the diagram normally. That
contrast is the practical point of this page: the PDF path needs no binary, and
the HTML path does.
