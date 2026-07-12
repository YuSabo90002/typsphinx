Included Document
=================

.. _included-target:

Included Target Section
-----------------------

This document IS reachable from the master toctree, so its anchors exist in the
compiled master.

Orphan cross-reference, whose target document is NOT included: see
:ref:`orphan-target`. Because the orphan document is excluded from every
toctree, this reference must degrade to plain text or the compile aborts.

Included cross-reference, whose target document IS included: jump to
:ref:`included-target`. This reference must still emit a working label link as
a regression guard, since only the non-included target degrades.
