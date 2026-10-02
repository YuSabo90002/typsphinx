Bibliography and Citations
==========================

typsphinx renders bibliographies and citations by rendering
`sphinxcontrib-bibtex <https://pypi.org/project/sphinxcontrib-bibtex/>`_'s
*resolved* citation nodes as ordinary Typst content. That is the defining
guarantee for this feature: typsphinx carries **zero** bibliography-specific
code. By the time a document reaches the Typst translator, sphinxcontrib-bibtex
has already turned every ``:cite:`` role and every ``.. bibliography::``
directive into plain docutils citation, reference and inline nodes, and the
generic visitors that already existed handle them. Nothing in the pipeline knows
what a BibTeX key is.

The practical consequence is that what sphinxcontrib-bibtex supports is what
typsphinx supports, and the constraints you can trip are its constraints rather
than typsphinx's.

Setup
-----

``sphinxcontrib-bibtex`` is **not** a typsphinx dependency. typsphinx itself
carries only Sphinx, docutils and Typst at runtime, so you install the
bibliography extension yourself::

   pip install sphinxcontrib-bibtex

Then enable it in your own ``conf.py`` alongside typsphinx, and point it at your
``.bib`` files:

.. code-block:: python

   extensions = [
       "typsphinx",
       "sphinxcontrib.bibtex",
   ]

   bibtex_bibfiles = ["refs.bib"]

No typsphinx setting needs to change. There is no bibliography-related
configuration value in typsphinx, because there is no bibliography-related code
path to configure.

What Is Supported
-----------------

Every form below is exercised end to end by the test suite, in both the emitted
``.typ`` markup and the compiled PDF.

Parenthetical Citations
~~~~~~~~~~~~~~~~~~~~~~~

``:cite:p:`` renders as a bracketed citation group, the usual
``[1]``-style parenthetical reference:

.. code-block:: rst

   The result was reproduced independently :cite:p:`Smith2020`.

Textual Citations
~~~~~~~~~~~~~~~~~

``:cite:t:`` renders the author name *outside* the bracket group, so the
citation reads as part of the sentence:

.. code-block:: rst

   :cite:t:`Smith2020` reproduced the result independently.

Multi-Key Citations
~~~~~~~~~~~~~~~~~~~

A single role naming several keys renders as **one** bracketed group, not as one
group per key:

.. code-block:: rst

   Two independent groups agree :cite:p:`Smith2020,Tanaka2019`.

Footnote Citations
~~~~~~~~~~~~~~~~~~

``:footcite:`` paired with ``.. footbibliography::`` renders as real Typst
footnotes, printed at the foot of the page where the citing site appears -- not
collected into a list at the end of the document:

.. code-block:: rst

   An earlier survey covered this ground :footcite:`Tanaka2019`.

   .. footbibliography::

Citing the same key a second time emits a bare reuse reference rather than a
second footnote body, so the entry text is not duplicated on the page.

Reference Lists
~~~~~~~~~~~~~~~

``.. bibliography::`` renders as a Typst ``grid``: one row per entry, each row
carrying the pybtex label and the formatted entry body.

.. code-block:: rst

   References
   ==========

   .. bibliography::

A bare directive renders only the entries actually cited somewhere in the
project, not every entry in your ``.bib`` files. Add the ``:all:`` option if you
want the whole file listed.

Several Reference Lists in One Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multiple ``.. bibliography::`` directives render as independent grids. A common
shape is one chapter-local list narrowed with ``:filter:`` plus a corpus-wide
list at the end of the project; each renders its own rows, and neither interferes
with the other. See the first constraint below for how that interacts with an
entry two lists both own.

Citations Across the ``#include()`` Boundary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A citing site in an included document resolves against a ``.. bibliography::``
living in a *different* document, and the resulting link survives the Typst
``#include()`` boundary into the compiled PDF. This works for the ordinary
layout in which a master document is a pure toctree, every chapter is an
included file, and the reference list sits in its own chapter -- so every single
citation has to cross an include boundary to reach its entry.

Constraints You Can Trip
------------------------

The three constraints below are measured behaviour, not theory. Each is the
behaviour of sphinxcontrib-bibtex that typsphinx faithfully passes through.

Entries Appear Once Per Reference List, Not Once Per Document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exactly-once is a *per reference list* property. An entry owned by two
``.. bibliography::`` directives -- say a chapter-local filtered list and a
corpus-wide list -- legitimately renders **twice** in the finished PDF, once in
each grid. That is correct output, not a duplication bug.

On the test suite's own four-entry fixture the measured entry-body occurrence
counts in the compiled PDF are 1, 2, 1 and 0: the ``2`` is the key that two
bibliographies both own, and the ``0`` is an entry nothing cites. If you are
writing your own check over generated output, count per grid rather than per
document.

The Key-on-Left ``:filter:`` Form Degrades Silently
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``:filter:`` expressions must put the key *string* on the left:

.. code-block:: rst

   .. bibliography::
      :filter: "Smith2020" % key

Writing the comparison the other way round -- ``key == "Smith2020"`` -- is a
**silent** failure. The grid simply empties, while the build still exits 0 with
**zero warnings, even under** ``-W``. The citing sites do not warn either,
because they fall back to a corpus-wide bibliography elsewhere in the project,
so sphinxcontrib-bibtex's ``bibtex.key_not_found`` never fires.

Build cleanliness therefore cannot detect this. If you use ``:filter:``, check
the *rendered* output -- look at the grid and confirm the rows you expect are
present. A clean strict build is not evidence that the filter matched anything.

``:keyprefix:`` Is Load-Bearing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the same key is rendered by two bibliographies in one project, the second
one needs ``:keyprefix:`` to keep its anchors distinct:

.. code-block:: rst

   .. bibliography::
      :filter: "Smith2020" % key
      :keyprefix: ch2-

This is not cosmetic. Removing ``:keyprefix:`` in that situation is a hard
``bibtex.duplicate_citation`` failure under a strict (``-W``) build. The prefix
stays internal to the anchors -- it does not leak into the rendered labels or
entry bodies.

Citation Style Is Owned By pybtex
---------------------------------

Citation labels and the formatting of each entry body come from
`pybtex <https://pypi.org/project/pybtex/>`_, selected through
sphinxcontrib-bibtex's ``bibtex_default_style``. typsphinx does not reformat
them: whatever string pybtex produced for a label or an entry body is emitted
into the Typst output as-is.

In particular, **Typst's own** ``#bibliography()`` **and** ``#cite()``
**functions are deliberately not used.** A reference list is emitted as a
``grid`` of already-formatted rows, and a citation as an already-formatted
reference. The consequences are worth stating plainly:

- Typst's CSL styles are **unavailable**. Supplying a ``.csl`` file has no
  effect on typsphinx output.
- Typst never sees your ``.bib`` files. It sees only text that pybtex already
  rendered.
- To change how citations and entries look, configure pybtex and
  sphinxcontrib-bibtex -- not Typst.

This is the same choice Sphinx's own LaTeX builder makes: it emits pybtex-rendered
``\bibitem`` entries rather than handing the ``.bib`` file to BibTeX. Keeping the
same ownership boundary is what lets the Typst, LaTeX and HTML builders agree on
labels, bodies and ordering for the same sources, which the test suite asserts
as a three-way comparison.

See Also
--------

- :doc:`builders` - Understanding the typst and typstpdf builders
- :doc:`configuration` - Configuration options available in ``conf.py``
