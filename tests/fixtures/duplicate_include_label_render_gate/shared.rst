.. _shared-anchor:

Shared Chapter
==============

This chapter is reachable via two toctree paths in the master's include graph.
The explicit target above propagates onto this section, so its id is emitted as
a Typst ``<label>`` definition -- exactly the class of label the corpus
``.. py:module:: sphinx.ext.apidoc`` directive produced
(``<module-sphinx.ext.apidoc>``).

A same-document cross-reference to :ref:`shared-anchor` is emitted as a
``link(<...>, ...)`` reference, which must still resolve to the single surviving
anchor after the duplicate include is deduplicated.
