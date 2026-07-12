Topic Line Block Render Gate
==============================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (BLK-02/BLK-03, SC#3). It is not meant to
be read as prose -- it exercises the generalized ``visit_title`` buffer-swap
(topic clue box, box-less contents pass-through), the ``line``/``line_block``
verbatim-break handlers, and the pre-existing admonition-title path
(including a multi-child inline-markup title, the Pitfall-1 regression)
against a real Typst compile.

Note: this fixture deliberately does NOT use ``.. epigraph::`` (or any
attributed ``block_quote``) -- see 13-RESEARCH.md Pitfall 4. Those hit two
unrelated, pre-existing bugs (a hard fatal with attribution; a literal-
source leak without) that are out of scope for BLK-02/BLK-03.

.. contents:: Table of Contents
   :local:

Topic Section
-------------

.. topic:: A Topic *Title*

   TOPICBODYSENTINEL body text.

Line Block Section
-------------------

Address
~~~~~~~

| ADDRESSLINEONE Main Street
| ADDRESSLINETWO Anytown USA

Poem
~~~~

| POEMLINEONE
|    POEMNESTEDONE
|    POEMNESTEDTWO
| POEMLINETHREE

Admonition Regression
-----------------------

.. note::

   ADMONITIONNOTESENTINEL note body text.

.. warning::

   ADMONITIONWARNINGSENTINEL warning body text.

.. admonition:: Custom *Title*

   ADMONITIONCUSTOMSENTINEL custom admonition body text.
