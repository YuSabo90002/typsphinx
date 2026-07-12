Duplicate Include Label Render Gate
===================================

The master reaches ``shared`` two ways: directly (below) AND nested under
``sub`` -- a diamond in the include graph, mirroring Sphinx's own
``doc/index.rst`` (which lists ``usage/extensions/index`` both directly in its
"Reference" toctree and nested under ``usage/index`` in its "User guide"
toctree). Without include-dedup, ``shared.typ`` is ``#include``d twice and
every ``<label>`` it defines is emitted twice.

.. toctree::

   sub
   shared
