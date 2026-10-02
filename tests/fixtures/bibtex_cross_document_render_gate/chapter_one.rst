Chapter One
===========

.. This document must carry EXACTLY ONE citing site, the parenthetical form
   below, and NOTHING else of substance. Do not remove it and do not add a
   second site: S05's gates assert exactly one query() for this key's anchor
   in the emitted chapter_one.typ, and that the anchor matches a grid row
   label in refs.typ -- a DIFFERENT document.

   Do NOT add a bibliography directive here. Per locked decision D012 the
   single bibliography lives in refs.rst; a local bibliography would make the
   resolution same-document and void the cross-document measurement.

   The key cited here (Smith2020) is cited from nowhere else in this fixture.
   Chapter Two owns the other cited key. Never cite Nobody2021 -- it is the
   deliberately uncited refs.bib entry (MEM006).

   DEFERRED CONSTRUCTS: multiple bibliography directives belong to S04's
   fixture (tests/fixtures/bibtex_multi_bibliography_render_gate); footcite /
   footbibliography belong to S03's fixture
   (tests/fixtures/bibtex_footcite_render_gate); the full-form combination of
   routes belongs to S06. Write role names un-colonised in comments, as with
   cite:p here -- see index.rst's note on the MEM025 trap.

Chapter one cites the first entry parenthetically :cite:p:`Smith2020`.
