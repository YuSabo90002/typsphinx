Abbr PEP Separator Render Gate
================================

This fixture exists solely to be compiled to PDF by
``tests/test_abbr_pep_separator_render_gate.py`` -- a regression gate for
FID-14 (the auto-generated PEP 3102 ``*`` / PEP 570 ``/`` signature
separators injecting their ``<abbr>`` hover-title text inline, cluttering
every affected signature). It pairs the auto-generated separators with a
genuine ``:abbr:`` role usage in the SAME document, per D-Disc-3, so both
the suppressed and the kept behaviors are proven in one compile.

Signature with both separators
--------------------------------

.. py:function:: abbrpepsepfunc(pos_only, /, both, *, kw_only)

   A function whose signature carries both a PEP 570 positional-only ``/``
   separator and a PEP 3102 keyword-only ``*`` separator.

Genuine abbreviation usage
-----------------------------

The :abbr:`ABBRSENTINELACRONYM (ABBRSENTINELEXPANSIONPHRASE)` term appears
in this prose and must keep its inline expansion.
