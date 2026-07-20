Desc Signature Siblings Render Gate
====================================

This fixture reproduces the corpus symptom where multiple sibling
``desc_signature``s (overloads / alias groups / multi-option directives)
concatenate onto one running line instead of stacking on separate lines,
mirroring ``usage/domains/python.typ``'s ``compile()`` overload group.

.. py:function:: compile(source)
                  compile(source, filename)
                  compile(source, filename, symbol)

   Compile source into a code or AST object. Three sibling signature lines
   under one directive exercise the sibling desc_signature linebreak fix.

A single-signature directive must stay byte-unchanged (no extra separator
token for the lone signature -- the cardinality edge case).

.. py:function:: solo(source)

   Only one signature line; no sibling desc_signature exists.
