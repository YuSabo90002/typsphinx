Page A
======

Shared Topic
------------

Page A defines its OWN section titled "Shared Topic", which docutils auto-slugs
to the id ``shared-topic``. This is the NEGATIVE GUARD: it is the same slug
Page B uses, so the cross-document reference below must NOT be captured by this
local anchor -- it must land on Page B's ``shared-topic`` instead.

.. _local-a:

Local Section
-------------

Same-document reference (refid path): jump to the
:ref:`local section <local-a>`. This must emit a link to Page A's own
namespaced ``local-a`` anchor.

Cross-document reference (target in another document): see
:ref:`Page B's shared topic <shared-topic>`. Sphinx resolves this to Page B's
explicit ``shared-topic`` label, so it must be namespaced with Page B's docname
-- not Page A's, even though Page A has a same-slug local anchor.
