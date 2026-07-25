Typst Lang Gate Japanese Source Proof
=======================================

This fixture exists solely to be compiled by
``tests/test_typst_lang_gate.py`` (GATE-01, CONF-07, SC#1's D-07 source
half). It is deliberately minimal and ASCII-only -- a title and one short
paragraph -- so the real ``typst.compile()`` this gate performs stays fast
and its outcome does not depend on any particular font being installed.
