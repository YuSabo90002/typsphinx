Bibtex Citation Render Gate
============================

.. This fixture is deliberately minimal and has NO second.rst and NO
   toctree: the cross-document case belongs to S05, and an included
   document would change the master/content split that T03 asserts
   against. A second bibliography belongs to S04 -- do not add one here.
   The textual (``cite:t``) and multi-key (one ``cite:p`` naming two
   keys) forms were added by S02 and now live below, after the
   bibliography; they are part of this fixture's locked baseline and must
   not be removed. NOTE: in a comment here, always write a role name
   WITHOUT its leading colon, as above. The gate's _parse_cited_keys and
   T01's fixture verify both regex the RAW file for ``:cite:<x>:`` and
   count every hit as a real citing site, so a fully-colonised mention in
   prose silently inflates the citing-site count.

Citing Site
-----------

.. A single parenthetical citing site for the first key in refs.bib.
   Pre-resolution this is a pending_xref with reftarget="Smith2020";
   after sphinxcontrib-bibtex resolves it, it is a reference node whose
   rendered marker is what T03 looks for in the body (MEM001).

The parenthetical form cites the first entry here :cite:p:`Smith2020`.

References
----------

.. The bibliography directive is owned by sphinxcontrib.bibtex (MEM002).
   It expands into resolved citation nodes, which typsphinx renders as a
   single Typst grid -- each entry appearing exactly once.

.. bibliography::

Textual Site
------------

.. S02: a single TEXTUAL citing site for the second key in refs.bib.
   This locks the ``cite:t`` form (R005): sphinxcontrib-bibtex renders the
   author surname OUTSIDE the bracket group, i.e. the body emits the
   surname text node immediately before "[" and the resolved link inside
   it. That surname-before-bracket ordering is the only thing
   distinguishing this from the parenthetical form above. Placed after
   the bibliography on purpose -- the directive renders whatever is cited
   anywhere in the document, so Tanaka2019 still gets a grid row.

The textual form names the author inline: :cite:t:`Tanaka2019`.

Multi Site
----------

.. S02: a single MULTI-KEY citing site naming BOTH refs.bib keys in one
   role. This locks the two-key ``cite:p`` form (R004): the two resolved
   references share ONE bracket group, separated by a ", " Text node, in
   the same order as the role argument. Keep both keys and keep the order
   Smith2020 then Tanaka2019 -- the gate asserts rst key order is
   preserved in the emitted markup.

Both entries can be cited at once :cite:p:`Smith2020,Tanaka2019`.
