Label At Char Render Gate
=========================

This fixture exists solely to be compiled to PDF by
``tests/test_label_at_char_render_gate.py``. It is not meant to be read as
prose -- a ``doctree-resolved`` handler registered in ``conf.py`` injects a
hyperlink target anchor and a same-document reference that both carry an id
containing a literal at-sign (``myapp.@thing.a``), mirroring the Sphinx
C-domain anonymous-entity ids (``c.Data.@data.a``) that produced the corpus
fatal. The anchor DEFINITION and the cross-REFERENCE must be sanitized to the
SAME Typst-valid label name, or the compile aborts.
