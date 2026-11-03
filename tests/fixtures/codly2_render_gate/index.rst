Codly2 Render Gate
==================

This fixture exists solely to be built by ``tests/test_codly2_render_gate.py``
and ``tests/test_codly2_output_gate.py``. Each code block carries a unique
lowercase sentinel; each paragraph marker before an empty block is a
distinctive uppercase token. It is not meant to be read as prose.

Line numbers
------------

.. code-block:: python

   nolnblk_a = "first"
   nolnblk_b = "second"

.. code-block:: python
   :linenos:

   numonblk_a = "first"
   numonblk_b = "second"
   numonblk_c = "third"

.. code-block:: python
   :linenos:
   :lineno-start: 10

   tenstartblk_a = "first"
   tenstartblk_b = "second"
   tenstartblk_c = "third"

.. code-block:: python
   :linenos:
   :lineno-start: 1

   onestartblk_a = "first"
   onestartblk_b = "second"

.. code-block:: python
   :linenos:
   :lineno-start: 0

   zerostartblk_a = "first"
   zerostartblk_b = "second"

.. code-block:: python
   :linenos:
   :lineno-start: 1000

   bigstartblk_a = "first"
   bigstartblk_b = "second"

Emphasized lines
----------------

.. code-block:: python
   :emphasize-lines: 2

   emphblk_a = "first"
   emphblk_b = "second"
   emphblk_c = "third"
   emphblk_d = "fourth"

.. code-block:: python
   :linenos:
   :lineno-start: 10
   :emphasize-lines: 2

   comboblk_a = "first"
   comboblk_b = "second"
   comboblk_c = "third"

.. code-block:: python
   :linenos:
   :emphasize-lines: 2-4,4,6

   dedupeblk_a = "first"
   dedupeblk_b = "second"
   dedupeblk_c = "third"
   dedupeblk_d = "fourth"
   dedupeblk_e = "fifth"
   dedupeblk_f = "sixth"
   dedupeblk_g = "seventh"

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,9

   rangeblk_a = "first"
   rangeblk_b = "second"
   rangeblk_c = "third"

Languages
---------

.. code-block::

   nolangblk_a = "default language"

.. code-block:: none

   nonelangblk_a = "explicit none"

A doctest block:

>>> doctestblk_a = "doctest"
>>> print(doctestblk_a)
doctest

Empty and one-line blocks
-------------------------

EMPTYBEFOREMARK

.. code-block:: python

EMPTYAFTERMARK

.. code-block:: python

   singleblk_a = "only line"

.. literalinclude:: tab_snippet.txt
   :language: python
   :linenos:

Encoding
--------

.. literalinclude:: encoding_snippet.txt
   :language: text

Captioned listings
------------------

.. code-block:: python
   :caption: Capone first listing
   :name: cap-one

   capblk_a = "first listing"

.. figure:: figure.svg

   Figcap image figure

.. code-block:: python
   :caption: Cap ]br #x $m$
   :name: cap-two

   capblk_b = "second listing"

Reference by number: :numref:`NUMREFSENT %s <cap-one>`.
Reference by name: :ref:`cap-two`.

Code in containers
------------------

- Listitemblk intro:

  .. code-block:: python

     listblk_a = "in a list item"

.. note::

   .. code-block:: python

      admonblk_a = "in an admonition"

.. list-table::

   * - Cellblk intro

       .. code-block:: python

          cellblk_a = "in a table cell"
