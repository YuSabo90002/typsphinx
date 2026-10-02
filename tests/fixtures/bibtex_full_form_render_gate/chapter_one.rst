Chapter One
===========

.. This document carries ALL FOUR inline citing shapes of the full-form
   surface, and it is the ONLY document in this fixture that carries any of
   them. Counted as emitted query() calls, its measured census is FOUR: one
   for the parenthetical site, one for the textual site, and TWO for the
   multi-key site (one per key named in it). Its grid count is ZERO -- neither
   bibliography directive lives here -- and its footnote count is TWO.

   Do NOT add a bibliography directive here. The corpus-wide bare one lives in
   refs.rst and the filtered chapter-local one lives in chapter_two.rst. A grid
   in this document would both break the zero-grid census below and make the
   resolution for these sites same-document, voiding the cross-document half
   of the measurement (the D012 precedent from S05).

   Do NOT add or remove a citing site without re-measuring: the per-route
   exactly-once counts (D013) are keyed to exactly the sites written below.

   NOTE: role names in comments are written WITHOUT their leading and trailing
   colons, as with cite:p, cite:t and footcite here. The sibling gates regex
   the RAW rst for the fully-colonised roles and count every hit as a real
   citing site, so a colonised mention in prose would silently inflate the
   parsed citing-site count (MEM022/MEM030's trap).

Parenthetical Site
------------------

.. The PARENTHETICAL shape (cite:p), naming the first key. Resolves across the
   include() boundary to the corpus-wide bare bibliography in refs.rst.

Chapter one cites the first entry parenthetically :cite:p:`Smith2020`.

Textual Site
------------

.. The TEXTUAL shape (cite:t), naming the second key. Deliberately a different
   inline shape from the site above so the full-form combination is
   characterised for both, exactly as the S05 fixture did across its two
   chapters -- except that here they coexist in ONE document.

Chapter one cites the second entry textually: :cite:t:`Tanaka2019` said so.

Multi Key Site
--------------

.. The MULTI-KEY shape: a single parenthetical site naming BOTH cited grid
   keys at once. This is the site that makes the chapter's query() census four
   rather than three -- one multi-key site emits one query() per key named.
   Keep both keys in this one role; splitting it into two single-key sites
   would keep the total at four while destroying the multi-key route itself.

Both entries are cited together here :cite:p:`Smith2020,Tanaka2019`.

Footnote Route Definition Site
------------------------------

.. The FIRST footnote-route site, naming the footnote-only key. This is where
   typsphinx emits the DEFINITION footnote form -- the bracket-wrapped,
   label-attached shape carrying the entry's formatted body. The key named
   here is cited by no other shape anywhere in this fixture, so the footnote
   route's exactly-once count cannot be satisfied by a grid row.

The footnote entry is cited in a footnote here :footcite:`Foot2018`.

Footnote Route Reuse Site
-------------------------

.. The SECOND footnote-route site, naming the SAME key as the site above.
   This is the reuse-form subject: the second reference to an
   already-emitted footnote id must emit the bare reuse form and must NOT emit
   a second definition. A second definition would mean a doubled footnote body
   in the compiled PDF, which is precisely what the exactly-once count on this
   route detects. Keep this site naming the same key as the definition site.

The same footnote entry is cited again :footcite:`Foot2018`.

.. The footbibliography directive is owned by sphinxcontrib.bibtex (MEM002).
   Unlike the bibliography directive it expands into footnote nodes rather
   than a definition grid, which is why this document's grid census stays
   zero while its footnote census is two. It must stay the ONLY
   bibliography-family directive in this document, and it must stay BELOW both
   footnote-route sites above.

.. footbibliography::

.. EVERYTHING BELOW IS DELIBERATE FILLER, and it exists for exactly one
   measured reason: to push the document that follows this one onto a LATER
   PAGE of the compiled master.pdf. S05 deferred the page-CROSSING proof to
   S06 precisely because its own fixture was too short to guarantee that a
   citing site and its bibliography entry ever landed on different pages -- a
   same-page link proves nothing about crossing. The filler below makes the
   crossing structural rather than incidental.

   Do NOT shorten or delete these sections to "tidy up" the fixture. If the
   page census ever needs re-measuring, re-measure it; do not assume the
   crossing survives a shorter chapter. Adding MORE filler is always safe;
   removing it is not. The filler carries no citing site of any kind, so it
   cannot perturb the query(), grid or footnote censuses above.

Filler Section One
------------------

This section exists to occupy vertical space in the compiled document so that
the bibliography entries rendered by later documents cannot share a page with
the citing sites above. It carries no citation of any kind.

Typesetting a document of this shape exercises the ordinary paragraph path of
the translator, which is deliberately uninteresting here. The only property
this prose needs to have is length, and the only property it must NOT have is
a citing site.

Nothing in this section should be read as documentation of behaviour. It is
ballast, and it is labelled as ballast so that a later reader does not mistake
it for a measurement subject.

Filler Section Two
------------------

A second ballast section, for the same reason as the first. Page geometry in
the compiled output depends on the template's page size and margins, neither
of which this fixture configures, so the amount of filler needed is an
empirical quantity rather than a derived one.

The quantity written here was chosen to leave comfortable headroom above the
measured minimum rather than to sit exactly at it. A fixture that only just
achieves a page break is a fixture that silently stops achieving it the next
time a default font metric changes upstream.

Repeating the same point in different words is, unusually, the intended
function of this paragraph. It adds lines, and adding lines is the entire
contract of this section.

Filler Section Three
--------------------

A third ballast section. By this point the compiled output has accumulated
enough material that the documents included after this one begin on a fresh
page, which is the condition the page-crossing proof depends upon.

As above, there is no citation here, no bibliography directive here, and
nothing here that any gate asserts against except insofar as its sheer
presence moves later content downward.

If a future change makes this fixture's page layout materially more compact,
the correct response is to add a fourth filler section, not to weaken the
page-crossing assertion that this filler exists to make possible.
