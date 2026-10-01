Graphviz Malformed Dot Gate
===========================

.. Exactly ONE diagram below, and its DOT body is deliberately invalid: the
   stray-arrow form `"Alphaone" -> ;` names a source with no target. A
   SECOND diagram would make it ambiguous which one aborted the compile,
   so this fixture must keep exactly one.

   This note is an rST COMMENT rather than visible prose on purpose
   (MEM022): the gate asserts substrings of a compile error, and prose
   naming them could not satisfy those assertions -- but the same habit
   keeps the fixture from ever accidentally supplying its own evidence.

.. digraph:: broken

   "Alphaone" -> ;
