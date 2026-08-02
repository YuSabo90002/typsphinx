Citation Render Gate
=====================

.. toctree::
   :maxdepth: 1

   second

Citing Sites
------------

.. Requirement CIT-03 (SC#3). FORWARD reference -- Krizhevsky2012 is
   defined below in the References section, after this first use.
   DEFECT CASE pre-fix (citation/label nodes unhandled -- the classic
   compile fatal).

The CNN architecture traces its origin to [Krizhevsky2012]_.

.. Requirement CIT-04 / D-03 multi-marker shape. A second citation of the
   SAME key gives that definition two entries in backrefs, proving the
   ``(1,2)`` back-reference marker shape.

The same paper is cited a second time here: [Krizhevsky2012]_.

.. Requirement CIT-04 / D-03 single-marker shape. Exactly one citing site
   means the label text itself becomes the back-link, with no ``(1)``
   marker.

A different paper is cited exactly once: [Solo1998]_.

.. Requirement D-10a. Cross-document citing site -- Cross2019 is defined
   ONLY in second.rst. This paragraph must not also define anything.

This paragraph cites a key defined in another document: [Cross2019]_.

.. Requirement D-10b. Same2020 is a duplicate key defined in BOTH
   documents. Sphinx's citation domain resolves a duplicate key
   last-registered-wins across the whole build, so which document this
   reference lands in is decided by Sphinx and must never be hard-coded
   in an assertion.

This paragraph cites the duplicate key: [Same2020]_.

.. Requirement T-40-03. Nosuchkey has no definition anywhere -- the
   dangling-citing-reference case. Sphinx itself warns "citation not
   found" and leaves the reference unresolved before the translator runs,
   so the expected emission is plain text and no link call.

This paragraph cites an undefined key: [Nosuchkey]_.

Concat Protocol
----------------

.. Requirement SC#5 code-mode concat boundary. A definition-list TERM is
   one of this translator's five concat contexts (``_in_term``) --
   adjacent inline expressions in the term are ``+``-joined. The citing
   reference to Concat2000 sits inside that term, next to plain text.

Concat Term [Concat2000]_
    A short definition body for the concat-protocol boundary case.

Nested Protocol
-----------------

.. Requirement SC#5 list-item boundary; RESEARCH's independently
   reproduced second failure mode -- this construct fails today with a
   DIFFERENT fatal ("label ... does not exist in the document") than the
   top-level syntax fatal.

- Item one, a plain paragraph.

- Item two contains a citation list:

  .. [Nested2021] CITNESTEDSENTINEL A citation nested inside a list
     item's body.

  Referenced here as [Nested2021]_ within the same item.

References
----------

.. Requirement CIT-01 / CIT-02 / D-05. Five consecutive citation
   definitions form ONE run/grid. The comment between the second and
   third definitions below emits nothing and must NOT break the run --
   all five must still land in one grid.

.. [Krizhevsky2012] CITORDERALPHA Krizhevsky, A., Sutskever, I., &
   Hinton, G. E. (2012). ImageNet classification with deep convolutional
   neural networks. Advances in neural information processing systems,
   25. This entry body is padded further with extra prose so it wraps
   onto at least a second visual line when rendered inside a narrow grid
   column, exercising CIT-02's continuation-line hanging-indent
   measurement against a real, multi-line reference entry.

.. [Solo1998] CITORDERBRAVO Solo, J. (1998). A single-line reference
   entry.

.. An RST comment between two citation definitions. Comments emit
   nothing and must not break the D-05 run -- these five definitions
   must still land in ONE grid, not two.

.. [Never1999] CITORDERCHARLIE Never, N. (1999). An uncited reference
   entry -- D-07's plain, non-linked label case. Sphinx will log a
   "is not referenced" warning for this entry; that warning is expected.

.. [Same2020] CITORDERDELTA Same, S. (2020). The duplicate-key entry,
   defined again in second.rst -- D-10's definition-side namespacing
   case.

.. [Concat2000] CITORDERECHO Concat, C. (2000). A "quoted" reference with
   a café character, exercising the existing escape_typst_string path.

Run Break
----------

.. Requirement D-06. A real paragraph between two citation definitions
   breaks the run into two separate, independently-aligned grids.

.. [Break2021] CITBREAKONESENTINEL Break, O. (2021). First half of the
   broken run.

This paragraph breaks the citation run per D-06.

.. [Break2022] CITBREAKTWOSENTINEL Break, T. (2022). Second half of the
   broken run, in its own independently-aligned grid.
