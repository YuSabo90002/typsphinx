Substitution Definition Render Gate
====================================

This fixture reproduces the corpus fatal where a substitution_definition
node -- having no ``visit_substitution_definition`` handler -- fell through
to ``unknown_visit`` (which warns but does not skip) and leaked its inline
``literal``/``text`` children out as juxtaposed top-level Typst expressions
with no separator, e.g. ``raw("a")text(", ")raw("b")...``.

The definition below has three adjacent inline children (three ``literal``
nodes joined by plain ``text`` separators), matching the shape of the corpus
fatal:

.. |substthings| replace:: ``SUBSTLITERALALPHA``, ``SUBSTLITERALBETA``, ``SUBSTLITERALGAMMA``

SUBSTUSESENTINEL paragraph that uses the substitution here: |substthings| and
nowhere else.
