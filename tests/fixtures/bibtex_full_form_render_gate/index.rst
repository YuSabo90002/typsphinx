Bibtex Full Form Render Gate
============================

.. This master document is a PURE TOCTREE. Do NOT add any content here, and
   in particular:

   * NO cite:p / cite:t / footcite / any other citing role site. A citing site
     in the master would let the same-document (unguarded) resolution path
     contaminate S06's cross-document measurement -- the whole point is that
     every citing site sits in an INCLUDED chapter while the two
     bibliographies sit in OTHER documents. This follows the D012 precedent
     S05 locked for the cross-document fixture.
   * NO bibliography and NO footbibliography directive. The corpus-wide bare
     one lives in refs.rst and the filtered chapter-local one lives in
     chapter_two.rst; footbibliography lives in chapter_one.rst next to its
     own citing sites. Hosting any of them here would make the master BOTH
     the including document and a bibliography host, so a
     chapter-to-bibliography link could be satisfied by the master's own page
     without ever crossing an include() boundary in the direction under test.
     See conf.py's module docstring for the full rationale.

   Do NOT remove the three toctree entries and do NOT REORDER them. The
   Sphinx-assigned citation anchor ids -- and therefore the query() targets
   the gates match -- are assignment-order dependent (MEM043), so reordering
   silently renames every anchor and breaks the gates for a reason unrelated
   to citation rendering.

   NOTE: in a comment anywhere in this fixture, always write a role name
   WITHOUT its leading and trailing colons, as with cite:p and footcite
   above. The sibling gates regex the RAW rst file for the fully-colonised
   roles and count every hit as a real citing site, so a colonised mention in
   prose would silently inflate the parsed citing-site count (MEM022/MEM030's
   trap).

.. toctree::
   :maxdepth: 2

   chapter_one
   chapter_two
   refs
