Bibtex Cross Document Render Gate
=================================

.. This master document is a PURE TOCTREE. Do NOT add any content here, and
   in particular:

   * NO cite:p / cite:t / cite:alp / any other cite role site. A citing site
     in the master would let the same-document (unguarded) resolution path
     contaminate S05's cross-document measurement -- the whole point is that
     every citing site sits in an INCLUDED chapter while the bibliography
     sits in a DIFFERENT included document.
   * NO bibliography directive. Per locked decision D012 the single
     bibliography lives in refs.rst, a third sibling document, so a
     chapter-to-bibliography link cannot be satisfied by the master's own
     page without crossing an include() boundary. See conf.py's module
     docstring for the full D012 rationale.

   Do not remove the three toctree entries or reorder them: the Sphinx-assigned
   citation anchor ids, and therefore the query() targets the gates match, are
   assignment-order dependent.

   DEFERRED CONSTRUCTS -- which slice owns what, so nothing is added here by
   mistake:

   * multiple bibliography directives in one document -> S04's fixture,
     tests/fixtures/bibtex_multi_bibliography_render_gate
   * footcite / footbibliography (the footnote route) -> S03's fixture,
     tests/fixtures/bibtex_footcite_render_gate
   * the full-form combination of routes -> S06

   NOTE: in a comment anywhere in this fixture, always write a role name
   WITHOUT its leading and trailing colons, as with cite:p above. The gates
   regex the RAW file for the fully-colonised cite roles and count every hit
   as a real citing site, so a colonised mention in prose would silently
   inflate the parsed citing-site count (MEM025's trap).

.. toctree::
   :maxdepth: 2

   chapter_one
   chapter_two
   refs
