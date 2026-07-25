Typst Lang Gate Malformed Language Proof
==========================================

This fixture exists solely to be compiled by
``tests/test_typst_lang_gate.py`` (GATE-01, CONF-07, SC#4). It is
deliberately minimal and ASCII-only -- a title and one short paragraph --
so the real ``typst.compile()`` this gate performs stays fast and
independent of any font requirement.
