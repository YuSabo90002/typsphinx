Deps Override
=============

Every package the user-supplied ``/_typsphinx/deps.typ`` imports is
exercised: admonitions (gentle-clues), a code block (codly), and math
(mitex).

.. note::

   A note, rendered by gentle-clues 1.3.0.

.. warning::

   A warning, rendered by gentle-clues 1.3.0.

.. tip::

   A tip, rendered by gentle-clues 1.3.0.

.. code-block:: python
   :emphasize-lines: 1

   x = 1
   y = 2

Inline math :math:`a^2 + b^2 = c^2` and block math:

.. math::

   e^{i \pi} + 1 = 0
