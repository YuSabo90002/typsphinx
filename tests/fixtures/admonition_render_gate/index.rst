Admonition Render Gate
=======================

This fixture exists to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (D-04, and Phase 39's
``TestAdmonitionPdfRenderGate`` header-text extension), AND to be compiled to
``.typ`` and string-scanned by ``tests/test_admonition_bucket_render_gate.py``
(Phase 39 GATE-01). It is not meant to be read as prose -- it exercises the
admonition markup/code-mode fix (Phase 8.1) and, as of Phase 39, carries
every one of the ten real Sphinx admonition types plus the pre-existing
nested note/warning pair, each with its own greppable body sentinel. Every
type below must keep exactly one sentinel-bearing construct -- do not add a
second sentinel occurrence for the same type, and do not remove a sentinel
from the construct that carries it.

Note With A Bullet List
------------------------

.. Requirement ADM-01. Expected post-phase gentle-clues function: info. CONTROL (bucket does not move).

.. note::

   ADMONNOTESENTINEL Before list.

   - Item one.
   - Item two.

Warning With A Literal Block
------------------------------

.. Requirement ADM-02. Expected post-phase gentle-clues function: warning. CONTROL (bucket does not move).

.. warning::

   ADMONWARNINGSENTINEL Before code.

   .. code-block:: python

      x = 1

Hint Type
---------

.. Requirement ADM-01. Expected post-phase gentle-clues function: tip. CONTROL (bucket does not move).

.. hint::

   ADMONHINTSENTINEL This is a hint admonition (D-06 new type).

Danger Type
-----------

.. Requirement ADM-02 (D-03). Expected post-phase gentle-clues function: error. DEFECT CASE -- today emits danger(...).

.. danger::

   ADMONDANGERSENTINEL This is a danger admonition (D-06 new type).

Nested Admonition
------------------

.. This nested note/warning pair deliberately carries NO sentinel -- it is
   about nesting itself, and giving it sentinels would put two candidate
   regions in play for the note and warning bucket assertions above.

.. note::

   Outer note before nested warning.

   .. warning::

      Inner warning nested inside the outer note.

   Outer note after nested warning.

Tip Type
--------

.. Requirement ADM-01. Expected post-phase gentle-clues function: tip. CONTROL (bucket does not move).

.. tip::

   ADMONTIPSENTINEL This is a tip admonition.

Important Type
---------------

.. Requirement ADM-02. Expected post-phase gentle-clues function: warning. CONTROL (bucket does not move).

.. important::

   ADMONIMPORTANTSENTINEL This is an important admonition.

Caution Type
-------------

.. Requirement ADM-02. Expected post-phase gentle-clues function: warning. CONTROL (bucket does not move).

.. caution::

   ADMONCAUTIONSENTINEL This is a caution admonition.

See Also Type
--------------

.. Requirement ADM-01 (D-02). Expected post-phase gentle-clues function: tip. DEFECT CASE -- today emits info(...) with title "See Also".

.. seealso::

   ADMONSEEALSOSENTINEL This is a seealso admonition.

Attention Type
---------------

.. Requirement ADM-02 (D-03). Expected post-phase gentle-clues function: error. DEFECT CASE -- today emits warning(...).

.. attention::

   ADMONATTENTIONSENTINEL This is an attention admonition.

Error Type
-----------

.. Requirement ADM-02. Expected post-phase gentle-clues function: error. CONTROL (bucket does not move).

.. error::

   ADMONERRORSENTINEL This is an error admonition.
