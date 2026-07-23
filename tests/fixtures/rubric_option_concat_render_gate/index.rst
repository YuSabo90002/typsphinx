Rubric Option Concat Render Gate
==================================

This fixture reproduces the corpus symptom where a rubric option-group
heading merges onto the same line as the first following option, mirroring
``man/sphinx-quickstart.rst``'s "Structure Options"/``--sep`` pattern.

.. rubric:: Structure Options

.. option:: --sep

   If specified, separate source and build directories.

A rubric at true end-of-document (nothing follows the trailing separator)
must still compile cleanly with no visible artifact.

.. rubric:: Trailing Heading
