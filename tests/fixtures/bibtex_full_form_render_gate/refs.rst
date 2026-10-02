References
==========

.. This document hosts the fixture's CORPUS-WIDE bibliography, and it is
   deliberately NOT the master -- the D012 precedent S05 locked. All inline
   citing sites live in sibling included documents (chapter_one, chapter_two),
   so every citation rendered here must resolve across Typst's include()
   boundary to the grid emitted in this document. See conf.py's module
   docstring for the full rationale.

   This document's measured grid census is ONE, and this directive is the
   second of the fixture's two bibliography directives -- the other is the
   filtered chapter-local one in chapter_two.rst.

   The directive below must stay BARE: no filter, no keyprefix, and NO :all:
   option.

   * A filter here would scope the corpus-wide grid to a subset, destroying
     the "one bare corpus-wide bibliography alongside one filtered
     chapter-local bibliography" shape that this fixture exists to exercise.
   * A keyprefix here would rename this grid's anchors, breaking the
     cross-document link from the chapter citing sites to these rows. The
     keyprefix belongs on the chapter-local directive ONLY, where it is
     required to avoid a duplicate citation id -- see chapter_two.rst.
   * The :all: option would render every refs.bib entry, which would destroy
     the uncited-entry negative control: per MEM006 a bare bibliography
     renders ONLY cited entries, which is what keeps the exactly-once counts
     non-vacuous. See refs.bib's header for which entry is permanently
     uncited and why.

   Do NOT add a citing site here either: this document must contribute no
   citing site of its own, so the grid rows emitted here come exclusively from
   the chapter documents.

   Do NOT add a footbibliography directive here: the footnote route lives
   entirely in chapter_one.rst, next to its own citing sites.

   The bibliography directive itself is owned entirely by sphinxcontrib.bibtex
   (MEM002); typsphinx only renders the resolved nodes (MEM010). Role names in
   comments are written WITHOUT their leading and trailing colons -- see
   index.rst's note on the MEM022/MEM030 trap.

.. bibliography::
