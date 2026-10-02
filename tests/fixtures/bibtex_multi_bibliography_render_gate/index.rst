Bibtex Multi Bibliography Render Gate
=====================================

.. This fixture is deliberately SEPARATE from
   tests/fixtures/bibtex_citation_render_gate -- that gate pins exactly one
   grid( in the emitted content file and its grid-splitting helpers key off
   the FIRST grid(, so a second bibliography there would break existing
   gates (R011). See conf.py's module docstring for the full reason.

   It is also deliberately minimal: NO second.rst, NO toctree, NO footcite
   site and NO footbibliography directive. The footnote route belongs to S03;
   the cross-document route belongs to S05. What this document pins is TWO
   grids, each scoped by its own :filter: to one key.

   FILTER SYNTAX: the string must be on the LEFT of %, as written below.
   Measured at plan time: the key-on-left comparison form builds
   "successfully" but degrades every citing site to
   "WARNING: could not find bibtex key [bibtex.key_not_found]", and the
   cited-on-left modulo form is rejected outright with
   "expected a string on left side of Mod()". Do not rewrite the filters.

   NOTE: in a comment here, always write a role name WITHOUT its leading
   colon, as with cite:p here. S04's gate regexes the RAW file for the
   colonised cite roles and counts every hit as a real citing site, so a
   fully-colonised mention in prose would silently inflate the citing-site
   count (MEM025's trap).

Chapter One
-----------

.. The sole citing site for the FIRST key. Its chapter-local bibliography
   below is filtered to this key alone, so Chapter One's grid must hold
   "A study of things" and nothing else.

Chapter one cites the first entry :cite:p:`Smith2020`.

References for Chapter One
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. The bibliography directive is owned by sphinxcontrib.bibtex (MEM002),
   including :filter: evaluation. String-on-left form -- see the note above.

.. bibliography::
   :filter: "Smith2020" % key

Chapter Two
-----------

.. The sole citing site for the SECOND key, symmetric to Chapter One. Its
   chapter-local bibliography is filtered to this key alone, so Chapter
   Two's grid must hold "Another work entirely" and nothing else.

Chapter two cites the second entry :cite:p:`Tanaka2019`.

References for Chapter Two
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. The SECOND bibliography directive -- the whole point of this fixture.
   Neither filter names the third refs.bib entry (Nobody2021), which stays
   uncited so the zero-count assertion on "An intentionally uncited" cannot
   degrade into a no-op (MEM006).

.. bibliography::
   :filter: "Tanaka2019" % key
