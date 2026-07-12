Page B
======

.. _shared-topic:

Shared Topic
------------

Page B also has a "Shared Topic" section, carrying an explicit
``.. _shared-topic:`` target. Its slug ``shared-topic`` collides with Page A's
section slug across the flattened master.

This paragraph makes a same-document reference to
:ref:`this very topic <shared-topic>`. Before per-document namespacing this
emitted a bare ``link(<shared-topic>)`` while ``<shared-topic>`` was ALSO
defined by Page A -- a duplicated, referenced label, which aborts the compile
with ``label ... occurs multiple times``.
