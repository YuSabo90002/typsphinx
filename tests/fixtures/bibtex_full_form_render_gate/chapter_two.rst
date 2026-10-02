Chapter Two
===========

.. This document carries ONE parenthetical citing site and the fixture's
   CHAPTER-LOCAL FILTERED bibliography. Its measured grid census is ONE. It is
   the second of the fixture's two bibliography directives -- the corpus-wide
   bare one lives in refs.rst -- and the coexistence of those two is one of the
   properties S06 exists to prove.

   Do NOT add a footbibliography directive here: the footnote route lives
   entirely in chapter_one.rst, next to its own citing sites.

   NOTE: role names in comments are written WITHOUT their leading and trailing
   colons, as with cite:p here. The sibling gates regex the RAW rst for the
   fully-colonised roles and count every hit as a real citing site, so a
   colonised mention in prose would silently inflate the parsed citing-site
   count (MEM022/MEM030's trap).

Citing Site
-----------

.. The sole citing site in this document, in the parenthetical shape, naming
   the key that this document's filtered bibliography below is scoped to.

Chapter two cites the second entry :cite:p:`Tanaka2019`.

References for Chapter Two
--------------------------

.. The CHAPTER-LOCAL bibliography. Owned entirely by sphinxcontrib.bibtex
   (MEM002), including filter evaluation and keyprefix handling.

   MEASURED CONSTRAINT 1 -- the filter needs the STRING ON THE LEFT of the %
   operator, exactly as written below. Do not rewrite it into the key-on-left
   comparison form (key == "..."). MEM034/MEM038 recorded that form degrading
   every citing site to "WARNING: could not find bibtex key
   [bibtex.key_not_found]" in the S04 fixture; MEASURED HERE AT T01 TIME, in
   THIS fixture, it degrades differently and far more quietly. Swapping this
   one line to the key-on-left form drops this document's grid from 1 to 0 --
   the chapter-local bibliography renders NOTHING, and "Another work entirely"
   disappears from chapter_two.typ -- while the build still exits 0 with ZERO
   warnings EVEN UNDER -W. No key_not_found warning fires, because the citing
   site above silently falls back to resolving against the corpus-wide bare
   bibliography in refs.rst, which still carries that key.

   CONSEQUENCE FOR THE GATES: build cleanliness alone cannot detect this
   regression in this fixture. A gate must assert this document's grid count
   and its rendered entry text POSITIVELY. A gate that only checks "strict
   build exits 0" would stay green with the chapter-local bibliography
   entirely missing.

   MEASURED CONSTRAINT 2 -- do NOT remove the keyprefix option. It is
   load-bearing, not cosmetic. This fixture has BOTH this chapter-local
   bibliography and the corpus-wide bare bibliography in refs.rst, and both
   cover the same key. Without a prefix here, sphinxcontrib-bibtex reports a
   duplicate citation id for that key and the strict (-W) build FAILS with
   rc=1. The prefix namespaces this grid's row so the two directives can
   coexist, which is the entire point of hosting them in one project. The same
   constraint is restated in conf.py's module docstring.

.. bibliography::
   :filter: "Tanaka2019" % key
   :keyprefix: c2-
