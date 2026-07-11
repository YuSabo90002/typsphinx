Preview Smoke
==============

This fixture exists solely to be compiled by
``tests/test_preview_smoke_gate.py`` (CI-02). It is not meant to be read as
prose -- it exercises all four bundled ``@preview`` packages (``codly``,
``codly-languages``, ``mitex``, ``gentle-clues``) via real function calls,
not just their ``#import`` statements. The ``.. math::`` block below is the
load-bearing coverage: it is the one directive type the
``admonition_render_gate`` fixture (Phase 8.1) never included, and the only
way to actually invoke mitex's ``mitex(`...`)`` call -- the exact code path
the historical ``kai`` regression broke.

Note Block
----------

.. note::

   Exercises gentle-clues (admonition -> clue-type content block).

Code Block
----------

.. code-block:: python

   x = 1

Exercises codly + codly-languages (labeled code block -> codly()/codly-range()
calls, initialized globally via #codly(languages: codly-languages)).

Math Block
----------

.. math::

   e^{i \pi} + 1 = 0

Exercises mitex (block math -> a real ``mitex(`...`)`` call -- this is the
code path the ``kai`` regression broke, and the only one the existing
admonition_render_gate fixture never invokes).
