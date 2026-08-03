Second Document
=================

.. Requirement D-08 / D-10a. Cross-document citing site: cites
   Krizhevsky2012, defined in index.rst. Per D-08 this gets a working
   forward link and NO back-reference in index.rst's definition --
   docutils' own ``backrefs`` are same-document only.

This document cites [Krizhevsky2012]_, which is defined in the master
document.

References
----------

.. [Cross2019] Cross, C. (2019). Cited only from index.rst -- D-10a's
   cross-document citing-site proof.

.. [Same2020] CITSECONDDOCSENTINEL Same, S. (2020). The duplicate key's
   second definition -- D-10's definition-side namespacing case
   (``index:same2020`` vs ``second:same2020``, both non-colliding).
