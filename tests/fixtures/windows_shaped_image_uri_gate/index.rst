Windows Shaped Image URI Gate
==============================

This fixture rewrites its single image node's URI to a Windows-shaped
absolute path -- backslash-separated directory components plus a literal
double quote in the basename -- via a custom post-transform registered in
``conf.py``, driven by the ``TYPSPHINX_WIN_URI_MODE`` environment
variable (IMG-07, Phase 59).

.. image:: _static/converted_stand_in.png
