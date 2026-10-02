References
==========

.. This document hosts THE SINGLE bibliography for the whole fixture, and it
   is deliberately NOT the master -- locked decision D012. Both citing sites
   live in sibling included documents (chapter_one, chapter_two), so every
   citation must resolve across Typst's include() boundary to the grid emitted
   here. See conf.py's module docstring for the full D012 rationale.

   Do NOT remove the directive, do NOT add a second one, and do NOT add any
   option to it. The directive below must stay BARE: no filter, no keyprefix,
   and no :all: option.

   * A filter or a second directive would make this the multi-bibliography
     route, which is S04's fixture
     (tests/fixtures/bibtex_multi_bibliography_render_gate).
   * The :all: option would render every refs.bib entry, which would destroy
     the uncited-entry assertion: per MEM006 a bare bibliography renders ONLY
     cited entries, so Nobody2021's title "An intentionally uncited item"
     must have count 0 everywhere. Adding :all: would make that entry appear
     and the assertion would start failing for a reason unrelated to
     cross-document resolution.

   Do NOT add a cite site here either: this document must contribute no
   citing site of its own, so the grid rows emitted here come exclusively
   from the two chapter documents.

   DEFERRED CONSTRUCTS: footcite / footbibliography (the footnote route)
   belong to S03's fixture (tests/fixtures/bibtex_footcite_render_gate); the
   full-form combination of routes belongs to S06. Write role names
   un-colonised in comments, as with cite:p here -- see index.rst's note on
   the MEM025 trap.

   The bibliography directive itself is owned entirely by
   sphinxcontrib.bibtex (MEM002); typsphinx only renders the resolved nodes
   (MEM010).

.. bibliography::
