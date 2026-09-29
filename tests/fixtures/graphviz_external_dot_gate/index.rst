Graphviz External Dot Gate
==========================

.. The single directive below uses the external-file form, which R007
   scopes OUT. It must yield the bordered placeholder and exactly one
   warning -- never a rendered diagram.

   This note is an rST COMMENT, not prose, on purpose (MEM022): the gate
   asserts that the quoted label sentinels carried by the .dot file are
   ABSENT from the extracted PDF text, so any visible mention of them here
   would let the fixture satisfy the gate on its own words. They are not
   named in this comment either, for the same reason.

.. graphviz:: external.dot
