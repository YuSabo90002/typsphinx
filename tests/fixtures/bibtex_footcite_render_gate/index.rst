Bibtex Footcite Render Gate
============================

.. This fixture is deliberately SEPARATE from
   tests/fixtures/bibtex_citation_render_gate -- see conf.py's module
   docstring for the measured 2-failed/11-passed reason (D008). It is also
   deliberately minimal: NO second.rst, NO toctree, NO cite:p or cite:t
   site, and above all NO bibliography directive. Only footbibliography
   belongs here; a grid in this document would destroy S03's zero-grid
   contract. The COMBINED form (a grid and footnotes in one project) is
   owned by S06, not S03.

   NOTE: in a comment here, always write a role name WITHOUT its leading
   colon, as with footcite above. S03's gate regexes the RAW file for the
   colonised footcite role and counts every hit as a real citing site, so a
   fully-colonised mention in prose would silently inflate the citing-site
   count (MEM022's trap).

First Site
----------

.. A hand-written docutils footnote REFERENCE, placed first so it is the
   lowest-numbered footnote in the document. This is the coexistence
   subject: its emitted label is index:fn-plain, which must stay DISTINCT
   from every bibtex-generated footcite label. Its definition appears
   further down, before footbibliography.

A hand-written footnote coexists with the generated ones [#plain]_.

.. The FIRST footcite site for the first refs.bib key. This is where
   typsphinx emits the DEFINITION footnote form -- the bracket-wrapped,
   label-attached [#footnote({...}) <index:fn-footcite-smith2020>] shape --
   carrying Smith2020's formatted body.

The first entry is cited in a footnote here :footcite:`Smith2020`.

Repeat Site
-----------

.. A REPEAT footcite site naming the SAME first key. This is the reuse-form
   subject: the second reference to an already-emitted footnote id must emit
   the bare reuse form footnote(<index:fn-footcite-smith2020>) and must NOT
   emit a second definition -- a second definition would mean a doubled
   footnote body in the compiled PDF. Keep this site naming Smith2020.

The same first entry is cited again :footcite:`Smith2020`.

Second Key Site
---------------

.. A single footcite site for the SECOND refs.bib key, so the exactly-once
   count has two independent subjects with clearly distinct titles.
   Nobody2021 is never cited anywhere in this fixture -- see refs.bib.

The second entry is cited in a footnote here :footcite:`Tanaka2019`.

.. [#plain] This is the hand-written footnote body text.

.. The footbibliography directive is owned by sphinxcontrib.bibtex (MEM002).
   Unlike the bibliography directive it expands into footnote nodes rather
   than a definition grid, which is exactly the property S03 pins. It must
   stay LAST in the document, and it must stay the ONLY bibliography-family
   directive here.

.. footbibliography::
